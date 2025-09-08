from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import os
import requests
import json

app = FastAPI()

GM_ENDPOINT = os.environ.get('GM_API_ENDPOINT', 'https://generativemodels.googleapis.com/v1/models/MODEL:generate')
GM_TOKEN = os.environ.get('GOOGLE_OAUTH_TOKEN')

class HTMLIn(BaseModel):
    url: str | None = None
    html: str | None = None

class ExtractOut(BaseModel):
    title: str | None
    meta_description: str | None


def call_gm_api(payload: dict) -> dict:
    if GM_TOKEN is None:
        raise RuntimeError('GM_TOKEN not set in environment')
    headers = {'Authorization': f'Bearer {GM_TOKEN}', 'Content-Type':'application/json'}
    r = requests.post(GM_ENDPOINT, json=payload, headers=headers, timeout=30)
    r.raise_for_status()
    return r.json()


@app.post('/extract', response_model=ExtractOut)
def extract(in_data: HTMLIn):
    if not (in_data.html or in_data.url):
        raise HTTPException(status_code=400, detail='Provide html or url')
    html = in_data.html or requests.get(in_data.url, timeout=15).text
    payload = {'messages': [{'role':'system','content':'You are an extractor that returns JSON with title and meta_description.'},
                            {'role':'user','content':f'---BEGIN HTML---\n{html}\n---END HTML---'}],
               'maxOutputTokens':800}
    resp = call_gm_api(payload)
    try:
        content = resp.get('output', [{}])[0].get('content')
        parsed = json.loads(content)
        return ExtractOut(title=parsed.get('title'), meta_description=parsed.get('meta_description'))
    except Exception:
        raise HTTPException(status_code=502, detail='Invalid model response')
