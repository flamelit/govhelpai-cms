"""Complaince assistance chatbot"""
import json
import time

import numpy as np
import openai
import pandas as pd
import streamlit as st
from streamlit.logger import get_logger
from streamlit_extras.switch_page_button import switch_page

from src.llm_interface import GenAssistantBeta, initialize_client
from src.utils import load_openai_key, prompt_read

log = get_logger(__name__)
log.info("Things are running!")
st.set_page_config(initial_sidebar_state="collapsed")
back_button = st.button(label="Back to Demo list", key="reviewback")
if back_button:
    switch_page("app")
# Prepare uploading object
openai_key = load_openai_key("review")
api_key = openai_key["key"]
org_key = openai_key["organization"]

if "review_client_exists" not in st.session_state:
    client = initialize_client(api_key=api_key, org_key=org_key)
    st.session_state["review_client_exists"] = True


requirements = pd.read_json("data/mccr_tool.json").set_index("order")

assistant_id = "asst_ZjSIfmm5HVE9fGnoP7ZiXwkR"
client = openai.OpenAI(organization=org_key, api_key=api_key)
assistant = client.beta.assistants.retrieve(assistant_id)
thread = client.beta.threads.create()


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

st.header("Compliance Review Assistant", anchor=False)

st.markdown(
    """This tool demonstrates how AI can assist with submission compliance review. Steps:
1. First, upload a PDF file of a state submission (for demo purposes, an example application from a 2022 Mississippi filing is used).
2. Then, click to review the file for compliance criteria.
3. The file is reviewed and reports supporting evidence for each requirement
The user may then download the compliance results as a CSV file.

"""
)

st.divider()

upload = st.file_uploader(label="Upload PDF", type=["PDF"], key="ReviewFileUploader")
if upload:
    # if not st.session_state.get("file_in_buffer", False):
    file_upload = client.files.create(file=upload, purpose="assistants")
    log.info("File uploaded")

    assistant_file_upload = client.beta.assistants.files.create(
        assistant_id=assistant.id, file_id=file_upload.id
    )
    log.info("Uploaded file to assistant")
    thread = client.beta.threads.create()
    st.session_state["file_in_buffer"] = True
    run_assistant = st.button("Send to Review Assistant", type="primary")
    st.session_state["processing_enabled"] = True


st.divider()


finished_assistant = False


# progress_bar = st.progress(value=int(0), text="")

assessment_responses = dict()
if st.session_state.get("processing_enabled", False):
    requirements_df = requirements.iloc[-3:, :]
    length_requirements = requirements_df.__len__()
    with st.spinner("Processing requirements..."):
        for r in requirements_df.iterrows():
            row = r[1]
            order = r[0]
            # progress_bar.progress(
            #     int(100 * (order - 1) / length_requirements), text="Processing Requirements"
            # )
            time.sleep(0.05)

            message_to_send = f"ID:{row['id']};Requirement: {row['Description']}"

            message_sent = client.beta.threads.messages.create(
                thread_id=thread.id,
                content=message_to_send,
                role="user",
                file_ids=[assistant_file_upload.id],
            )
            run = client.beta.threads.runs.create(
                thread_id=thread.id, assistant_id=assistant.id, timeout=60
            )
            try:
                while run.status != "completed":
                    retrieve_run = client.beta.threads.runs.retrieve(
                        thread_id=thread.id,
                        run_id=run.id,
                    )
                    time.sleep(0.1)
                    if retrieve_run.status == "completed":
                        all_messages = client.beta.threads.messages.list(
                            thread_id=thread.id, order="desc"
                        )
                        assessment_responses[order] = json.loads(
                            all_messages.data[0].content[0].text.value
                        )
                        break
                    if retrieve_run.status in [
                        "failed",
                        "requires_action",
                        "cancelled",
                        "expired",
                    ]:
                        log.warn("Message failure.")
                        assistant_response = (
                            "Unable to get answer. Please try again in a few moments."
                        )
                        break
            except Exception as e:
                log.error(e)
                assessment_responses[order] = {
                    "id": row["id"],
                    "status": "Could not complete",
                    "reasoning": "missing",
                }

    st.write(assessment_responses)
