import os
import requests
from requests.adapters import HTTPAdapter, Retry
import json
import html
import numpy as np

EMBED_API_URL = os.environ.get('EMBED_API_URL')
EMBED_API_KEY = os.environ.get('EMBED_API_KEY')
if not EMBED_API_KEY:
    raise RuntimeError('Embedding API key missing from EMBED_API_KEY environment variable.')

class QueryHandler():
    def __init__(
            self,
            sanitized_query_input: str,
            embed_api_url: str = EMBED_API_URL,
            embed_api_key: str = EMBED_API_KEY):
        '''Initialize a query handler'''
        self.query = {'inputs':str(sanitized_query_input)}
        headers = {"Authorization": "Bearer "+ embed_api_key,
                     "Content-Type": 'application/json'}

        if str(os.environ.get('EMBED_API_TYPE')) == 'huggingface':
            self.embeddings = self.embed_huggingface(embed_api_url, headers)
        else:
            raise NotImplementedError('Non-huggingface embedding API not implemented yet.')

    def embed_huggingface(
            self,
            url,
            headers):
        '''Send query to the embedding API and return the response as a numpy array.'''
        s = requests.Session()
        retries = Retry(total=5, backoff_factor=3, status_forcelist=[ 502, 503, 504 ])
        s.mount('http://', HTTPAdapter(max_retries=retries))

        try:
            ret_value = np.array(s.post(
                url,
                json=self.query,
                headers=headers
            ).json()['embeddings'])

            return ret_value
        except KeyError as k:
            print(k)
