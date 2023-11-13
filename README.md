# HelpfulAI

LLM Chatbot implementation enabling digital services success by giving help to individuals as they seek information from domains that can be overwhelming.

Data sources
- Internal Revenue Service
  - [Form instructions](https://www.irs.gov/instructions)
  - [Internal Revenue Code](https://www.irs.gov/privacy-disclosure/tax-code-regulations-and-official-guidance)
- USCIS
  - [Form Instructions](https://www.uscis.gov/forms/all-forms)
  - [Legislation](https://www.uscis.gov/laws-and-policy/legislation/immigration-and-nationality-act)
  - [Regulations](https://www.uscis.gov/laws-and-policy/regulations)
  - [Policy Manual](https://www.uscis.gov/policy-manual)
  - [Memoranda](https://www.uscis.gov/laws-and-policy/policy-memoranda)


# Runtime
Expected runtime variables include

| Enviornment Variable Name | Content | Notes |
| --- | --- | --- |
| EMBED_API_URL | Endpoint for embedding | |
| EMBED_API_KEY | API Key/token, if required | |
| EMBED_API_TYPE | Currently accepts only value `huggingface` | |
| LLM_API_URL | Endpoint for LLM | optional for `openai` |
| LLM_API_KEY | API Key/token, if required | |
| LLM_API_TYPE | Currently accepts only value `openai` or `llama2`| |
| STORAGE_URI | URI for documents blob container | |
| STORAGE_BLOB | Name of Blob for storage | |
| STORAGE_KEY | Key for storage access, currently accepts an AWS Secret Key ID | |
| STORAGE_TOKEN | Token for storage access, currently accepts an AWS Secret Token | |
| DATA_PATH | Path to store data | optional, useful for testing. Default `/data/` |

# Setup
Run `setup.sh`

# Next steps
- [X] ~Prompt engineering and refinement~
- [X] ~Adding documents to the openai call~
- [X] ~Add to response with "Please consider the following forms for more information:"~
  - [ ] Adjust some type of confidence handling to add this value, else use default IRS instructions.
- [X] ~Map docs to websites (static like)~
- [X] ~Connect public facing~
- [X] ~Add authentication~
- [X] ~challenge.govhelp.ai~
- [X] ~Add S3 pdf doc of slides (s3 handler via streamlit)~
- [X] ~Finish slides~
