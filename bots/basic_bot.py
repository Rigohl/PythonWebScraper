import os
import requests

GM_ENDPOINT = os.environ.get('GM_API_ENDPOINT')
GM_TOKEN = os.environ.get('GOOGLE_OAUTH_TOKEN')


def call_gm(payload: dict) -> dict:
    headers = {'Authorization': f'Bearer {GM_TOKEN}', 'Content-Type':'application/json'}
    r = requests.post(GM_ENDPOINT, json=payload, headers=headers)
    r.raise_for_status()
    return r.json()


if __name__ == '__main__':
    # example usage (do not run without setting env vars)
    payload = {'messages':[{'role':'system','content':'You are a metadata extractor.'}, {'role':'user','content':'<html><head><title>Test</title></head><body></body></html>'}]}
    print(call_gm(payload))
