"""NZZ ContextAI — Streamlit Demo Interface."""

import streamlit as st

st.set_page_config(page_title="NZZ ContextAI", page_icon="📰", layout="wide")
st.title("📰 NZZ ContextAI")
st.caption("Semantic search and context-aware answers from the NZZ archive.")

query = st.text_input("Your question", placeholder="Was berichtete die NZZ über die Finanzkrise 2008?")

if st.button("Search") and query:
    with st.spinner("Retrieving and generating answer..."):
        st.info("Pipeline not yet connected — implement src/ modules first.")
