import streamlit as st
import json
import time
import yaml

from core.openapi_parser import load_spec, extract_endpoints, get_schema
from core.validator import validate_schema
from core.gemini_service import configure_gemini, generate_response
from core.utils import pretty_json

import toml

CONFIG = toml.load("config.toml")
configure_gemini(CONFIG["GEMINI_API_KEY"])

st.set_page_config(
    page_title="AI Powered Mock API Generator",
    page_icon="⚡",
    layout="wide"
)

st.markdown("""
<style>
.main {
    background: linear-gradient(135deg,#040f16, #0b3351);
}
</style>
""", unsafe_allow_html=True)

st.title("⚡ AI Powered Mock API Generator (MVP)")
st.write("Upload OpenAPI spec → Select Endpoint → Generate Realistic Mock Response Using Gemini")

uploaded_file = st.file_uploader("Upload OpenAPI JSON/YAML", type=["json", "yaml", "yml"])

if uploaded_file:
    spec = load_spec(uploaded_file)
    paths = extract_endpoints(spec)


    st.success("OpenAPI Loaded Successfully ✔️")

    col1, col2 = st.columns(2)

    with col1:
        endpoint = st.selectbox("Select Endpoint", paths)

    with col2:
        method = st.selectbox("HTTP Method", ["get", "post", "put", "delete"])

    schema = get_schema(spec, endpoint, method)
    st.subheader("📄 Response Schema Preview")
    st.json(schema)

    request_body = st.text_area("Optional Request Body", placeholder="{ }")

    if st.button("🚀 Generate AI Mock Response"):
        with st.spinner("Thinking with Gemini..."):
            response, latency = generate_response(schema, request_body)

        st.subheader("🧾 Generated Response")
        st.json(response)

        valid, error = validate_schema(response, schema)

        st.subheader("🔎 Validation Result")
        if valid:
            st.success("Schema Valid ✓")
        else:
            st.error("Schema Invalid ❌")
            st.text(error)

        st.metric("⏱ Latency", f"{latency:.2f} ms")

        st.success("Done 🎉")
