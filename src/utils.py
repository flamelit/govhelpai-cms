import json
import logging
import os
import sys
from pathlib import Path
from typing import List, Optional, Union

import streamlit as st


def st_chat_clear_history():
    st.session_state["chat_dialogue"] = []


def setup_logger(logger_name, log_level=logging.ERROR):
    # Create logger
    log = logging.getLogger(logger_name)
    log.setLevel(log_level)

    # Create a formatter
    formatter = logging.Formatter(
        "%(asctime)s | %(name)s | %(levelname)s | %(message)s"
    )

    # Create a console handler and add it to the logger
    stdout_handler = logging.StreamHandler(sys.stdout)
    stdout_handler.setLevel(log_level)
    stdout_handler.setFormatter(formatter)
    log.addHandler(stdout_handler)

    return log


def prompt_read(use: str) -> dict:
    with open("data/prompt.json", "r") as assess_prompt:
        load = json.loads(assess_prompt.read())
    try:
        return [x for x in load if x["name"] == use][0]
    except IndexError:
        raise ValueError(f"API use {use} not found")


def load_openai_key(use: str) -> dict:
    if "OPENAI_API_KEY" not in os.environ or "OPEN_AI_ORG" not in os.environ:
        with open(os.path.expanduser("~/.secrets/openai.json"), "r") as open_file:
            load = json.loads(open_file.read())
        try:
            return [x for x in load if x["use"] == use][0]
        except IndexError:
            raise ValueError(f"API use {use} not found")
    else:
        return {
            "use": use,
            "key": os.environ["OPENAI_API_KEY"],
            "organization": os.environ["OPEN_AI_ORG"],
        }
