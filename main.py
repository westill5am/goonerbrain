from fastapi import FastAPI, HTTPException
from scraper import scrape_sites

app = FastAPI()

@app.get("/")
def root():
    return {"message": "API is running"}

@app.get("/search")
def search(q: str):
    try:
        results = scrape_sites(q)
        if not results:
            raise HTTPException(status_code=404, detail="No results found")
        return {"results": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
        #comment
