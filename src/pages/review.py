"""Complaince assistance chatbot"""
import json
import time

import numpy as np
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

# gab = GenAssistantBeta(
#     instructions=prompt_read(use="review")["instructions"],
#     name="govhelpai-assistant-testing",
#     tools=[{"type": "retrieval"}],
#     model="gpt-4-1106-preview",
#     api_key=api_key,
#     org_key=org_key,
# )
# gab.create_assistant()

st.markdown(
    """
<style>
    [data-testid="collapsedControl"] {
        display: none
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


upload = st.file_uploader(label="Uplaod PDF", type=["PDF"], key="ReviewFileUploader")
if upload:
    file_create_record = gab.create_files(
        file_path="data/example_1915B_MS_Waiver_App.pdf", assistant_connect=True
    )
    run_assistant = st.button("Send to Review Assistant", type="primary")

st.divider()


finished_assistant = False

length_requirements = requirements.__len__()

if run_assistant and not finished_assistant:
    progress_bar = st.progress(value=int(0), text="Processing Requirements")

    assessment_responses = dict()

    for row in requirements.iterrows():
        progress_bar.progress(
            int(100 * row[0] / length_requirements), text="Processing Requirements"
        )
        time.sleep(0.05)

        assessment_responses[row["id"]] = gab.send_query(
            message=f"ID: {row['id']}; Requirement: {row['requirement']}",
            file_ids=[file_create_record["assistant_upload_record"].id],
        )

    finished_assistant = True

elif run_assistant and finished_assistant:
    st.table(requirements.head())


# msg =
# )
