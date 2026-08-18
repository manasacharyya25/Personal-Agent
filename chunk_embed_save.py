from sentence_transformers import SentenceTransformer

def chunk(text: str, chunk_size: int, overlap: int):
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunks.append(text[start:end])
        start = chunk_size - overlap
    return chunks


def embed(chunks : list[str]) -> list[list[float]]:
    model = SentenceTransformer("BAAI/bge-base-en-v1.5")

    embeddings = model.encode(
        chunks,
        normalize_embeddings=True
    )

    return embeddings

async def save_embeddings(db, chunks, embeddings):
    for chunk, embedding in zip(chunks, embeddings):
        await db.execute(
            """
            INSERT INTO document_chunk(chunk, embedding)
            VALUES($1, $2)
            """,
            chunk,
            embedding
        )
