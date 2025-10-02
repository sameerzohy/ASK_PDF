import logging
from google import genai
from fastapi import FastAPI
import inngest
import inngest.fast_api
from inngest.experimental import ai

from dotenv import load_dotenv
import uuid 
import os
import datetime 

from data_loader import load_and_chunk_pdf, embed_texts 
from vector_db import QdrantStorage
from custom_types import RAGQueryResults, RAGUpsertResults, RAGSearchResults, RAGChunkAndSrc

load_dotenv() 

inngest_client = inngest.Inngest(
    app_id='rag_app', 
    logger=logging.getLogger('uvicorn'), 
    is_production= False,
    serializer=inngest.PydanticSerializer(), 
)

@inngest_client.create_function(
    fn_id= "RAG Ingest PDF", 
    trigger= inngest.TriggerEvent(event="rag/ingest_pdf")
)
async def rag_ingest_pdf(ctx: inngest.Context): 
    ctx.logger.info('Starting RAG ingestion process for a PDF.') 
    def _load(ctx: inngest.Context) -> RAGChunkAndSrc:
        pdf_path = ctx.event.data["pdf_path"]
        source_id = ctx.event.data.get("source_id", pdf_path)
        chunks = load_and_chunk_pdf(pdf_path)
        return RAGChunkAndSrc(chunks=chunks, source_id=source_id)
        
        
    
    def _upsert(chunks_and_src: RAGChunkAndSrc) -> RAGUpsertResults:
        chunks = chunks_and_src.chunks 
        source_id = chunks_and_src.source_id
        vectors = embed_texts(chunks)
        ids = [str(uuid.uuid5(uuid.NAMESPACE_URL, f"{source_id}:{i}")) for i in range(len(chunks))]
        payload = [{"source": source_id, "text": c} for c in chunks]
        QdrantStorage().upsert(ids=ids, vectors=vectors, payloads=payload)
        return RAGUpsertResults(ingested=len(chunks))
    
    
     
    try:
        chunks_and_src = await ctx.step.run("load-and-chunk", lambda: _load(ctx), output_type=RAGChunkAndSrc)
        ingested = await ctx.step.run("embed-and-upsert", lambda: _upsert(chunks_and_src), output_type=RAGUpsertResults)
        return ingested.model_dump()
    except Exception as e:
        import logging
        logging.exception("Error in rag_ingest_pdf")
        return {"error": str(e)}


@inngest_client.create_function(
    fn_id="RAG: Query PDF",
    trigger=inngest.TriggerEvent(event="rag/query_pdf_ai")
)
async def rag_query_pdf_ai(ctx: inngest.Context)->RAGSearchResults:
    def _search(question:str, top_k:int=5):
        query_vector = embed_texts([question])[0]
        results = QdrantStorage().search(query_vector=query_vector, top_k=top_k)
        return RAGSearchResults(context=results['contexts'], sources=results['sources'])
    question = ctx.event.data['question']
    top_k = int(ctx.event.data.get('top_k', 5))
    
    found = await ctx.step.run("embed-and-search", lambda: _search(question, top_k), output_type=RAGSearchResults)
    content_block = "\n\n".join(f"-{c}" for c in found.context)

    user_content = (
        "Use the following Content to answer the question. \n\n"
        f"Content:{content_block}\n\n"
        f"Question:{question} \n"
        "Answer concisely using the context above"
    )
    
    # Use Google Generative AI directly
    def _generate_answer():
        from google import genai
        client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
        response = client.models.generate_content(
            model="gemini-2.0-flash-exp",
            contents=user_content,
            config={
                "system_instruction": "Answer for the questions only from the provided context",
                "max_output_tokens": 1024,
                "temperature": 0.2
            }
        )
        return response.text
    
    answer = await ctx.step.run("llm-answer", _generate_answer)
    return {"answer": answer, "sources": found.sources, "num_contexts": len(found.context)}


app = FastAPI()

inngest.fast_api.serve(app, inngest_client, [rag_ingest_pdf, rag_query_pdf_ai])






# "question": "who's resume is that?",
#     "top_k":5