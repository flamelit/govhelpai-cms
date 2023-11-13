import streamlit as st
from pathlib import Path
import os
import base64
from src.storage_interface import AWSStorageHandler
from src.embedding_interface import QueryHandler
from src.faiss_handler import FaissIndexHandler
from src.llm_interface import openai_run
import numpy as np
import faiss
import json
from streamlit.logger import get_logger
import streamlit_authenticator as stauth
import yaml
from yaml.loader import SafeLoader


DATA_PATH = os.environ.get('DATA_PATH')
# Create logger
log = get_logger(__name__)
log.info('Things are running!')

if 'sidebar_state' not in st.session_state:
    st.session_state.sidebar_state = 'collapsed'

st.set_page_config(
    page_icon='images/diagrams-GovHelp.AI Logo-web.png',
    page_title="GovHelp.AI - Supercharging Government Services",
    layout = 'wide',
    initial_sidebar_state = st.session_state.sidebar_state,
)


@st.cache_resource
def get_base64_of_bin_file(bin_file):
    with open(bin_file, 'rb') as f:
        data = f.read()
    return base64.b64encode(data).decode()


@st.cache_resource
def get_sites():
    with open('data/site.json') as sites_file:
        sites = json.loads(sites_file.read())
    return sites


@st.cache_resource
def get_img_with_href(local_img_path, target_url, width=200, height=200):
    img_format = os.path.splitext(local_img_path)[-1].replace('.', '')
    bin_str = get_base64_of_bin_file(local_img_path)
    html_code = f'''
        <a href="{target_url}">
            <img src="data:image/{img_format};base64,{bin_str}" width="{width}" height="{height}"/>
        </a>'''
    return html_code

@st.cache_resource(show_spinner=False)
def load_objects():
    '''Load objects from AWS S3 bucket and create FAISS
    index using Streamlit Caching'''
    log.info('Retrieving AWS storage object')
    storage_obj = AWSStorageHandler()
    faiss_obj = storage_obj.load_joblib_obj()
    embeddings = np.array(faiss_obj['embeddings'])
    documents = faiss_obj['documents']
    log.info('Object obtained')

    log.info('Creating FAISS index')
    vector_store = FaissIndexHandler(embeddings, documents)
    log.info('FAISS index created')

    log.info('Testing embedding handler')
    test_embedder_state = QueryHandler(
        sanitized_query_input=('What form should I file for my small'
        ' business to become an S-corp?'),
        embed_api_url=os.environ.get('EMBED_API_URL'),
        embed_api_key=os.environ.get('EMBED_API_KEY'))

    slides_download = AWSStorageHandler(filename='GovHelpAIWhitepaper.pdf')
    with open(DATA_PATH+'/GovHelpAIWhitepaper.pdf', 'rb') as cc:
        slides_pdf_data = cc.read()

    try:
        assert isinstance(test_embedder_state.embeddings, np.ndarray)
    except AssertionError:
        log.error('Embedding handler not working')
        raise
    return embeddings, documents, vector_store, slides_pdf_data

with st.spinner('Fetching GovHelp.AI resources'):
    embeddings, documents, vector_store, slides_pdf_data = load_objects()
    sites = get_sites()

def render_app():

    st.session_state.sidebar_state = 'expanded'

    st.markdown("""
        <style>
            [data-testid=stSidebar] {
                background-color: #e9e9ff;
            }
        </style>
        """, unsafe_allow_html=True)

    # Reduce font size to be used in chat boxes
    custom_css = """
        <style>
            .stTextArea textarea {font-size: 13px;}
            div[data-baseweb="select"] > div {font-size: 13px !important!}
        </style>
    """

    st.markdown(custom_css, unsafe_allow_html=True)
    hide_streamlit_style = """
                <style>
                #MainMenu {visibility: hidden;}
                footer {visibility: hidden;}
                </style>
                """
    st.markdown(hide_streamlit_style, unsafe_allow_html=True)

    st.sidebar.image('images/diagrams-GovHelp.AI Logo-web.png', width=150, )
    st.sidebar.markdown('''# GovHelp.AI\n### Supercharging Government Services''')


    #Set up/Initialize Session State variables:
    if 'chat_dialogue' not in st.session_state:
        st.session_state['chat_dialogue'] = []
    if 'llm' not in st.session_state:

        st.session_state['llm'] = os.environ.get('LLM_API_TYPE')


    def clear_history():
        st.session_state['chat_dialogue'] = []
    but1, but2 = st.sidebar.columns(2)
    with but1:
        pdf_download_button = st.download_button(
            label='About (PDF)',
            data=slides_pdf_data,
            use_container_width=True,
            file_name = 'GovHelpAIWhitepaper.pdf',
            mime='application/octet-stream'
        )
    with but2:
        clear_chat = st.button("Clear Chat",
                                       use_container_width=True,
                                       on_click=clear_history)



    st.sidebar.divider()

    st.sidebar.markdown('GovHelp.AI prototype is focused on tax-form related questions a person might ask the IRS.\n\n*Not affiliated with any Government.\n Application is Prototype.*')

    st.sidebar.divider()

    boostaro_logo_html = get_img_with_href(
        'images/boostaro_logo.png',
        'https://www.boostaro.com',
        width=177,
        height=44)
    flamelit_logo_html = get_img_with_href(
        'images/flamelit_logo_large.png',
        'https://www.flamelit.tech',
        width=184,
        height=42)
    st.sidebar.markdown("""
                        *Built with :blue_heart: by:*
                        """)
    st.sidebar.markdown(boostaro_logo_html, unsafe_allow_html=True)
    st.sidebar.markdown('  ')
    st.sidebar.markdown(flamelit_logo_html, unsafe_allow_html=True)

    # Display chat messages from history on app rerun
    for message in st.session_state.chat_dialogue:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if prompt := st.chat_input("Type your question here to talk to GovHelp.AI"):
        st.session_state.chat_dialogue.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)


        with st.spinner('GovHelp.AI is thinking...'):
            query = QueryHandler(prompt)
            nearest_elems = vector_store.search(
                np.reshape(
                    query.embeddings,
                    (1,query.embeddings.shape[0])),
                k=100)
            nearest_labels = vector_store.find_labels(nearest_elems[1][0], documents)
            docs, _ = vector_store.most_common_docs(nearest_labels)

            doc_dict = {}
            for doc in docs[:3]:
                log.info(f'Retrieving document {doc} from AWS.')
                aws_doc = AWSStorageHandler(filename='irs_instructions/'+doc)
                with open(os.environ.get('DATA_PATH')+'/irs_instructions/'+doc, 'r') as docfile:
                    doc_dict[doc] = {'content' : docfile.read()[:2500], 'website' : sites[doc]}
                    log.info(f'Document retrieved: {doc}')
            llm_output = openai_run(
                query = query.query['inputs'],
                relevant_docs= [v for _, v in doc_dict.items()],
                revelent_doc_names=docs
                )
            log.info(f'Query: {query.query}')
            log.info(f'Response: {llm_output}')
            llm_response = llm_output['choices'][0]['message']['content']

            view_sites = f'''\n\nLinks for documents that may be relevant to your search include:
* [{docs[0].upper().split('.')[0]}]({doc_dict[docs[0]]['website']})
* [{docs[1].upper().split('.')[0]}]({doc_dict[docs[1]]['website']})
* [{docs[2].upper().split('.')[0]}]({doc_dict[docs[2]]['website']})

You may also visit the [IRS Help page](https://www.irs.gov/help/telephone-assistance) for additional tools and resources.

            '''

            st.session_state.chat_dialogue.append(
                {"role": "assistant",
                "content": llm_response+view_sites})
            with st.chat_message("assistant"):
                st.markdown(llm_response + view_sites)


with open('./tmp_auth/auth.yaml') as file:
    config = yaml.load(file, Loader=SafeLoader)

authenticator = stauth.Authenticate(
    config['credentials'],
    config['cookie']['name'],
    config['cookie']['key'],
    config['cookie']['expiry_days'],
)

name, authentication_status, username = authenticator.login('Login to Prototype GovHelp.AI.\nUser: "challenge", Pass: "llmgovhelpai"', 'main')

if authentication_status is True:
    authenticator.logout('Logout', 'sidebar')
    render_app()
elif authentication_status is False:
    st.error('Username or password is incorrect.')
elif authentication_status is None:
    st.warning('''We added a temporary login form to prevent spam/abuse.
               Please login using user/pass as challenge/llmgovhelpai''')
