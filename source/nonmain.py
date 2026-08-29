from fastapi import FastAPI

nonapp = FastAPI()

@nonapp.get("/")
def root():
    return {"message": "non API"}