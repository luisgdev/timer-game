"""Main module"""
import uvicorn
from fastapi import FastAPI
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

app = FastAPI()


@app.get("/")
async def root():
    return {"message": "Server is healthy."}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
