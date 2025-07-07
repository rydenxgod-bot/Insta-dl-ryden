from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import JSONResponse
import httpx
import re
import asyncio

app = FastAPI()

INSTAGRAM_REGEX = r"(https?:\/\/)?(www\.)?(instagram\.com|instagr\.am)\/.*"

async def fetch_with_retries(url: str, retries: int = 3, timeout: int = 20):
    for attempt in range(1, retries + 1):
        try:
            async with httpx.AsyncClient(timeout=timeout) as client:
                res = await client.get(url)
                res.raise_for_status()
                return res.json()
        except Exception as e:
            if attempt == retries:
                raise e
            await asyncio.sleep(1.5)  # wait between retries

@app.get("/api/insta")
async def insta_proxy(url: str = Query(..., description="Instagram reel URL")):
    if not re.match(INSTAGRAM_REGEX, url):
        raise HTTPException(status_code=400, detail=" Invalid URL. Only Instagram URLs are allowed.")
    
    backend_url = f"https://tele-social.vercel.app/down?url={url}"
    try:
        data = await fetch_with_retries(backend_url)

        if not data.get("status"):
            raise HTTPException(status_code=400, detail="⚠️ Backend returned an error or unsupported reel.")

        return JSONResponse(content=data)

    except httpx.HTTPStatusError as e:
        raise HTTPException(status_code=502, detail=f"❌ Backend HTTP error: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"💥 Unexpected error: {str(e)}")
