import streamlit as st
import json
import toml
import yaml

from core.openapi_parser import load_spec, extract_endpoints, get_methods, get_schema
from core.gemini_service import configure_gemini, generate_response
from core.validator import validate_schema
from core.metrics import add_metric, get_stats
from core.rate_limiter import check_rate_limit

CONFIG = toml.load("config.toml")
configure_gemini(CONFIG["GEMINI_API_KEY"])

st.set_page_config(page_title="AI Mock Server", layout="wide")

if "trigger_generate" not in st.session_state:
    st.session_state["trigger_generate"] = False

st.markdown(
    """
    <h1 style='text-align:center;'>⚡ AI Powered Mock API Generator</h1>
    <p style="text-align:center;">Upload or Paste OpenAPI → Select Endpoint → Generate AI Mock Responses</p>
    """,
    unsafe_allow_html=True
)

uploaded_file = st.file_uploader("Upload OpenAPI JSON/YAML", type=["json","yaml","yml"])
st.write("OR")
text_input = st.text_area("Paste OpenAPI JSON / YAML", height=220)

spec = None

if uploaded_file:
    spec = load_spec(uploaded_file)
    st.success("OpenAPI Loaded Successfully ✔️")

elif text_input.strip():
    try:
        try: spec = json.loads(text_input)
        except: spec = yaml.safe_load(text_input)
        st.success("OpenAPI Loaded Successfully ✔️")
    except Exception as e:
        st.error("Invalid OpenAPI")
        st.code(str(e))

if spec:
    endpoint = st.selectbox("Select Endpoint", extract_endpoints(spec))
    methods = get_methods(spec, endpoint)
    method = st.selectbox("HTTP Method", methods).lower()

    schema = get_schema(spec, endpoint, method)

    tabs = st.tabs(["📄 Schema", "📝 Request Body", "⚙️ Options", "📊 Metrics"])

    with tabs[0]:
        st.json(schema)

    with tabs[1]:
        request_body = st.text_area("Request Body", "{}")

    with tabs[2]:
        mode = st.radio("Select Response Mode",
            ["Success", "400 Error", "404 Error", "500 Error"]
        )

        err_map = {"400 Error": "400","404 Error": "404","500 Error": "500"}
        error_type = err_map.get(mode, None)

        if st.button("🚀 Generate Response"):
            allowed, msg = check_rate_limit()
            if not allowed:
                st.error(msg)
            else:
                st.session_state["trigger_generate"] = True

        if st.session_state.get("trigger_generate"):
            with st.spinner("Contacting AI..."):
                response, latency = generate_response(schema, method, request_body, error_type)

            st.subheader("🧾 Generated Response")
            st.json(response)

            valid, error = validate_schema(response, schema) if not error_type else (False, None)

            if valid:
                st.success("Schema Valid ✓")
            elif error_type:
                st.warning("Intentional Error Mode Active")
            else:
                st.error("Schema Invalid")
                st.code(error)

            add_metric(latency, valid)
            st.metric("Latency", f"{latency:.2f} ms")

            st.session_state["trigger_generate"] = False

    with tabs[3]:
        avg_latency, compliance = get_stats()
        st.metric("Avg Latency", f"{avg_latency:.2f} ms")
        st.metric("Schema Compliance", f"{compliance:.1f}%")
