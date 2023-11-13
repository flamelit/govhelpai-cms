import os

import streamlit as st
from compare_summary import CompareSummary

col1, col2 = st.columns([.3, .7])

with col1:
    uploaded_files = st.file_uploader(
        label = 'Full File Uploader',
        accept_multiple_files = True,
        key = 'full_file_uploader'
    )
    if not isinstance(uploaded_files, list):
        list_files = [uploaded_files]
    else:
        list_files = uploaded_files

# with col2:
#     if len(list_files) > 0:
