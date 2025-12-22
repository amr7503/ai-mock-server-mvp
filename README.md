# AI Powered Mock API Generator – Samsung PRISM MVP

This project is an MVP of an AI-driven Mock API server
that generates realistic, schema-valid responses from OpenAPI specs
using Gemini LLM — wrapped in a beautiful Streamlit UI.

## Features
- Upload OpenAPI spec
- Select endpoint + method
- AI generates realistic JSON response
- Schema validation
- Latency tracking
- Professional UI

## Setup
pip install -r requirements.txt
Add Gemini Key in config.toml
streamlit run app.py

## Future Enhancements
- FastAPI backend
- RL + GNN
- Response diversity scoring
- Docker support
