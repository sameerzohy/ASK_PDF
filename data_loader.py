from google import genai
from llama_index.readers.file import PDFReader 
from llama_index.core.node_parser import SentenceSplitter
from dotenv import load_dotenv


load_dotenv()
client = genai.Client() 

# --- UPDATED EMBEDDING MODEL ---
# Using Google's current recommended text embedding model for high quality.
# The dimension for text-embedding-004 is 768, which must be updated.
EMBED_MODEL = "text-embedding-004" 
EMBED_DIM = 768 # <- IMPORTANT: Update dimension to match the model (text-embedding-004 is 768-D)

splitter = SentenceSplitter(chunk_size=1000, chunk_overlap=200)


def load_and_chunk_pdf(path:str):
    docs = PDFReader().load_data(file=path)
    # The rest of the chunking logic remains the same
    texts = [d.text for d in docs if getattr(d, "text", None)]
    chunks = []
    for t in texts:
        chunks.extend(splitter.split_text(t))
    return chunks


def embed_texts(texts: list[str]) -> list[list[float]]:
    response = client.models.embed_content(
        model=EMBED_MODEL,
        contents=texts,
    )
    
    return [r.values for r in response.embeddings]





# import functools
# from google import genai
# from llama_index.readers.file import PDFReader 
# from llama_index.core.node_parser import SentenceSplitter
# from llama_index.core.schema import TextNode  # Recommended import for clarity
# from dotenv import load_dotenv
# # ... other imports remain the same ...

# # ... global variables (client, EMBED_MODEL, splitter) remain the same ...

# def load_and_chunk_pdf(path: str) -> list[TextNode]: # <--- Change return type hint
#     # 1. Load the document (returns a list of Document objects)
#     documents = PDFReader().load_data(file=path)
    
#     # 2. Split the documents into nodes (chunks)
#     # This automatically retains metadata like source file, page number, etc.
#     nodes = splitter.get_nodes_from_documents(documents) 
    
#     return nodes # <--- Return Node objects, not raw text strings


# def embed_text(nodes: list[TextNode]) -> list[list[float]]:
#     # Extract the raw text from the nodes for the API call
#     texts = [node.text for node in nodes]
    
#     response = client.embeddings.create(
#         model=EMBED_MODEL,
#         input=texts
#     )
#     # Assuming you'll want to combine the embeddings back into the nodes later,
#     # but for just getting the vectors, this is fine.
#     return [item.embedding for item in response.data] # Note: access `embedding` (singular)