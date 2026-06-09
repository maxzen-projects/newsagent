from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
import json

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

BASE_DIR = Path(__file__).resolve().parent

def load_json(filename):
    path = BASE_DIR / filename

    print("Reading:", path)

    if not path.exists():
        print("NOT FOUND:", path)
        return []

    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    print("Loaded", len(data), "items")
    return data


@app.get("/articles")
def get_articles():
    return load_json("articles.json")


@app.get("/locality")
def get_locality():
    return load_json("locality_articles.json")


@app.get("/semantic")
def get_semantic():
    return load_json("semantic_articles.json")


@app.get("/final")
def get_final():
    return load_json("final_articles.json")