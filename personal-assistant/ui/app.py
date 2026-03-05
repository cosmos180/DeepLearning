import streamlit as st
import requests
import os
from dotenv import load_dotenv

load_dotenv()

API_URL = os.getenv("BACKEND_API_URL", "http://localhost:8000/api/v1")

st.set_page_config(page_title="Personal Assistant", layout="wide")

st.title("🧠 Second Brain Ingestion")

st.markdown("### Add to Knowledge Base")
input_text = st.text_area("Enter a URL or a Quick Note", height=150)

if st.button("Ingest"):
    if not input_text:
        st.warning("Please enter some text.")
    else:
        with st.spinner("Processing..."):
            try:
                response = requests.post(f"{API_URL}/ingest", json={"text": input_text})
                if response.status_code == 200:
                    data = response.json()
                    st.success(f"Saved: {data['title']}")
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        st.markdown(f"**Category:** {data['category']}")
                        st.markdown(f"**Tags:** {', '.join(data['tags'])}")
                        st.info(data['summary'])
                    
                    with col2:
                        st.code(f"File: {data['file_path']}")
                else:
                    st.error(f"Error: {response.text}")
            except Exception as e:
                st.error(f"Connection failed: {e}")

st.markdown("---")
st.markdown("### Recent Activities")
st.write("To be implemented: List recent files from backend.")
