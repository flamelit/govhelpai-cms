import datetime as dt
import hashlib
import json
import logging
import os
import time
from typing import List, Optional

import streamlit as st
from openai import NotFoundError, OpenAI

from src.utils import load_openai_key

logger = logging.getLogger(__name__)


@st.cache_resource
def send_query(client, thread, role, message, file_ids):
    return client.beta.threads.messages.create(
        thread.id,
        role=role,
        content=message,
        file_ids=file_ids,
    )


@st.cache_resource
def check_assistant_exists(client, assistant_id):
    try:
        return client.beta.assistants.retrieve(assistant_id)
    except NotFoundError:
        logger.error("Assistant does not exist.")
        return


@st.cache_resource
def create_thread(client):
    return client.beta.threads.create()


@st.cache_resource
def create_thread_run(client, assistant, thread):
    return client.beta.threads.runs.create(
        thread_id=thread.id, assistant_id=assistant.id
    )


@st.cache_resource
def create_file(client, assistant, file_path: str, assistant_connect: bool):
    file_upload_record = client.files.create(
        file=open(file_path, "rb"),
        purpose="assistants",
    )
    if not assistant_connect:
        return {"file_upload_record": file_upload_record}

    elif assistant_connect and assistant is not None:
        assistant_upload_record = client.beta.assistants.files.create(
            assistant_id=assistant.id, file_id=file_upload_record.id
        )
        return {
            "file_upload_record": file_upload_record,
            "assistant_upload_record": assistant_upload_record,
        }
    else:
        logger.warn(
            "Attempted to connect file to assistant without initialized assistant."
        )
        return {"file_upload_record": file_upload_record}


@st.cache_resource
def initialize_client(api_key, org_key):
    return OpenAI(organization=org_key, api_key=api_key)


def create_assistant(client, name, model="gpt-4-1106-preview", instructions=None):
    return client.beta.assistants.create(
        instructions=instructions,
        name=name,
        tools=[{"type": "retrieval"}],
        model=model,
    )


class GenAssistantBeta:
    def __init__(
        self,
        instructions,
        name,
        tools,
        api_key,
        org_key,
        model: str = "gpt-4-1106-preview",
    ):
        """Init Assistant"""
        self.name = name
        self.tools = tools
        self.model = model
        self.instructions = instructions
        self._api_key = api_key
        self._org_key = org_key
        self.conversation = dict()
        self.initialize_client()

    def initialize_client(self):
        self.client = initialize_client(api_key=self._api_key, org_key=self._org_key)

    def create_assistant(self, instructions: Optional[str] = None):
        """Initialize bot with input prompt"""
        if not instructions:
            instructions = self.instructions

        self.assistant = create_assistant(
            client=self.client,
            model=self.model,
            instructions=instructions,
            name=self.name,
        )

    def create_assistant_file(
        self, file_path: str, assistant_connect: Optional[bool] = True
    ):
        """Upload file and optionally connect to assistant"""
        return create_file(
            self.client, self.assistant, file_path, assistant_connect=assistant_connect
        )

    def send_query(self, message, file_ids: Optional[List[str]] = None):
        """Send and Receive message logic"""

        check_assistant_exists(self_id.client, self.assistant)

        thread = create_thread(self.client)

        _ = send_query(
            self.client, thread, role="user", message=message, file_ids=file_ids
        )

        run = create_thread_run(self.client, self.assistant, self.thread)

        start_time = dt.datetime.now()
        while True:
            run_retrieve = self.client.beta.threads.runs.retrieve(
                thread_id=thread.id, run_id=run.id
            )
            if run_retrieve.status == "completed":
                break
            elif run_retrieve.status in ["error", "failure"]:
                logger.error(
                    f"StatusError: did not complete. Status is {run_retrieve.status}"
                )
                break
            elif (dt.datetime.now() - start_time).seconds > 45:
                logger.error(
                    "TimeoutError: API did not resolve response in sufficient time"
                )
                raise TimeoutError()
            else:
                time.sleep(0.9999966)  # 6σ was here

        message_response = (
            self.client.beta.threads.messages.list(thread_id=thread.id, order="desc")
            .data[0]
            .content[0]
            .text.value
        )
        return message_response
