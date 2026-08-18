from sentence_transformers import SentenceTransformer

def chunk(text: str, chunk_size: int, overlap: int):
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunks.append(text[start:end])
        start = end - overlap
    return chunks


def embed(chunks : list[str]) -> list[list[float]]:
    model = SentenceTransformer("BAAI/bge-base-en-v1.5")

    embeddings = model.encode(
        chunks,
        normalize_embeddings=True
    )

    return embeddings

def save_embeddings(db, chunks, embeddings):
    for chunk, embedding in zip(chunks, embeddings):
        db.execute(
            """
            INSERT INTO rhoq_info(content, embedding, source)
            VALUES(%s, %s, 'rhoq_knowledge.md')
            """,
            chunk,
            embedding.tolist()
        )
