from qdrant_client import QdrantClient
from qdrant_client.models import VectorParams, Distance, PointStruct
from data_loader import EMBED_DIM

class QdrantStorage:
    def __init__(self, url="http://localhost:6333", collection="docs", dim=EMBED_DIM):
        self.client = QdrantClient(url=url, timeout=30)
        self.collection = collection
        self.dim = dim

        # This will delete the collection if it exists and create it with the correct dimensions.
        if not self.client.collection_exists(collection_name=self.collection):
            self.client.create_collection(
                collection_name=self.collection,
                vectors_config=VectorParams(size=self.dim, distance=Distance.COSINE),
            )
        
    def upsert(self, ids, vectors, payloads):
        points = [PointStruct(id=ids[i], vector=vectors[i], payload=payloads[i]) for i in range(len(ids))]
        self.client.upsert(collection_name=self.collection, points=points)
        
    
    def search(self, query_vector, top_k:int=5):
        results = self.client.search(
            collection_name=self.collection,
            query_vector=query_vector,
            limit=top_k,
            with_payload=True
        )
        contexts = []
        sources = set()
        
        for r in results:
            payload = getattr(r, "payload", None) or {}
            text = payload.get("text", "")
            source = payload.get("source", "")
            if text:
                contexts.append(text)
                sources.add(source)
                
        return {"contexts": contexts, "sources": list(sources)}