import asyncio
import sys

from Database import Database
from chunk_embed_save import chunk, embed, save_embeddings

async def ingest_document(file_path:str):
    db = Database()
    db.connect()

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            document = f.read()

        chunks = chunk(document, 500, 50)
        embeddings = embed(chunks)

        save_embeddings(db, chunks, embeddings)

    except Exception as ex:
        print(f"Exception ingesting document {ex}")
    finally:
        db.close()


if __name__=="__main__":
    file_path = sys.argv[1]
    asyncio.run(ingest_document(file_path))

