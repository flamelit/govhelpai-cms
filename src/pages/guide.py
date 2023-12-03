"""State Plan Amendment Chatbot"""
import json
import time

import openai
import streamlit as st
from streamlit.logger import get_logger
from streamlit_extras.switch_page_button import switch_page

from src.utils import load_openai_key

log = get_logger(__name__)
openai_key = load_openai_key("guide")
api_key = openai_key["key"]
org_key = openai_key["organization"]

st.set_page_config(initial_sidebar_state="collapsed")

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

col1, col2 = st.columns(2, gap="large")
with col1:
    back_button = st.button(
        label="Back to Demo list",
        key="guideback",
        use_container_width=True,
        type="primary",
    )
with col2:
    reset_button = st.button(
        label="Reset Chat",
        key="guidereset",
        use_container_width=True,
    )
if back_button:
    switch_page("app")
if reset_button:
    if "messages" in st.session_state:
        del st.session_state["messages"]

assistant_id = "asst_WcWHfaz8o007Bo8VvJbglw2M"
client = openai.OpenAI(organization=org_key, api_key=api_key)
assistant = client.beta.assistants.retrieve(assistant_id)
thread = client.beta.threads.create()

st.title("State Plan Amendment Q&A", anchor=False)
st.divider()

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Accept user input
if prompt := st.chat_input("What questions can I answer?"):
    # Display user message in chat message container
    with st.chat_message("user"):
        st.markdown(prompt)
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.spinner("CMS SPA Guide is thinking..."):
        message_sent = client.beta.threads.messages.create(
            thread_id=thread.id, content=prompt, role="user"
        )
        run = client.beta.threads.runs.create(
            thread_id=thread.id, assistant_id=assistant.id, timeout=60
        )
        while run.status != "completed":
            retrieve_run = client.beta.threads.runs.retrieve(
                thread_id=thread.id, run_id=run.id
            )
            time.sleep(0.1)
            if retrieve_run.status == "completed":
                all_messages = client.beta.threads.messages.list(
                    thread_id=thread.id, order="desc"
                )
                assistant_response = all_messages.data[0].content[0].text.value
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
    with st.chat_message("assistant"):
        st.markdown(assistant_response)
    st.session_state.messages.append(
        {"role": "assistant", "content": assistant_response}
    )
