import pydantic 

class RAGChunkAndSrc(pydantic.BaseModel):
    chunks: list[str]
    source_id: str = None 
    
    
class RAGUpsertResults(pydantic.BaseModel):
    ingested: int  
    
    
class RAGSearchResults(pydantic.BaseModel):
    context: list[str]
    sources: list[str]
    
    
class RAGQueryResults(pydantic.BaseModel):
    answer: str 
    sources: list[str] 
    num_contexts: int