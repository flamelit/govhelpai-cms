"""State Plan Amendment Chatbot"""
import io
import json
import time

import openai
import streamlit as st
from streamlit.logger import get_logger
from streamlit_extras.switch_page_button import switch_page

from src.utils import load_openai_key

log = get_logger(__name__)


def delete_file(client, assistant_id, file_id):
    with st.spinner("Removing file"):
        client.beta.assistants.files.delete(assistant_id=assistant_id, file_id=file_id)
        client.files.delete(file_id=file_id)


def send_file_to_llm(upload):
    bytes_to_upload = io.BytesIO(upload.getbuffer())
    bytes_to_upload.name = upload.name
    bytes_to_upload.seek(0)

    uploaded_file = client.files.create(file=bytes_to_upload, purpose="assistants")

    uploaded_assistant_file = client.beta.assistants.files.create(
        assistant_id=assistant_id, file_id=uploaded_file.id
    )
    return uploaded_file, uploaded_assistant_file


openai_key = load_openai_key("guide")
api_key = openai_key["key"]
org_key = openai_key["organization"]
assistant_id = "asst_WcWHfaz8o007Bo8VvJbglw2M"
client = openai.OpenAI(organization=org_key, api_key=api_key)

assistant = client.beta.assistants.retrieve(assistant_id=assistant_id)
st.set_page_config(initial_sidebar_state="collapsed")

st.markdown(
    """
<style>
    [data-testid="collapsedControl"] {
        display: none
    }
    div[data-testid="stToolbar"] {
    visibility: hidden;
    height: 0%;
    position: fixed;
    }
    div[data-testid="stDecoration"] {
    visibility: hidden;
    height: 0%;
    position: fixed;
    }
    div[data-testid="stStatusWidget"] {
    visibility: hidden;
    height: 0%;
    position: fixed;
    }
    #MainMenu {
    visibility: hidden;
    height: 0%;
    }
    header {
    visibility: hidden;
    height: 0%;
    }
    footer {
    visibility: hidden;
    height: 0%;
    }
</style>
""",
    unsafe_allow_html=True,
)

col1, col2 = st.columns(2, gap="large")

with col1:
    chat_page = st.button(
        label="Guide Chat Page",
        key="guide",
        use_container_width=True,
        type="primary",
    )
if chat_page:
    switch_page("guide")


st.header("SPA Trail Guide Admin Page", anchor=False)

uploader, manager = st.tabs(["Upload Files", "Manage Files"])


with uploader:
    st.subheader("Upload a new file", anchor=False)

    upload = st.file_uploader(
        label="Upload file for Chat",
        key="GuideAdminFileUpload",
        type=["PDF"],
    )

    if upload:
        upload_buffer = io.BytesIO(upload.getbuffer())
        upload_buffer.name = upload.name
        send_file_to_assistant = st.button("Send to Assistant", type="primary")
        if send_file_to_assistant:
            with st.spinner("Processing..."):
                send_file_to_llm(upload)
                st.success("Processing Completed.")
with manager:
    st.subheader("Current File List", anchor=False)

    assistant_file_list = client.beta.assistants.files.list(assistant_id=assistant.id)

    keep_list = ["cib112321.pdf", "SPA Submission & Processing 2023.pdf"]
    all_files_list = [client.files.retrieve(x.id) for x in assistant_file_list]
    deletable_files_list = [
        x.filename for x in all_files_list if x.filename not in keep_list
    ]
    deletable_files_dict = {
        x.id: x.filename for x in all_files_list if x.filename not in keep_list
    }

    for i in keep_list:
        col1, col2 = st.columns(2, gap="large")
        with col1:
            st.write(i)
        with col2:
            st.button("Remove File", disabled=True, key=i)

    for k, v in deletable_files_dict.items():
        col1, col2 = st.columns(2, gap="large")
        # fileinfo = client.files.retrieve(i.id)
        with col1:
            # st.write(fileinfo.filename)
            st.write(v)
        with col2:
            st.button(
                "Remove File",
                key=k,
                on_click=delete_file,
                kwargs={
                    "client": client,
                    "assistant_id": assistant_id,
                    "file_id": k,
                },
            )
    st.divider()

    # for cf in current_file_list:
    # pass
