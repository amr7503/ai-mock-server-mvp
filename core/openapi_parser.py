import json
import yaml


def load_spec(file):
    content = file.read()
    
    try:
        spec_json = json.loads(content)
    except:
        spec_json = yaml.safe_load(content)

    return spec_json
    


def extract_endpoints(spec_json):
    return list(spec_json["paths"].keys())



def get_schema(spec_json, endpoint, method):
    method = method.lower()
    
    responses = spec_json["paths"][endpoint][method]["responses"]

    # Normalize keys to string
    normalized = {str(k): v for k, v in responses.items()}

    # Prefer 200 if present
    if "200" in normalized:
        response = normalized["200"]
    else:
        # fallback: pick any 2xx response
        two_xx = [k for k in normalized.keys() if k.startswith("2")]
        if not two_xx:
            raise Exception("No success response (2xx) found in OpenAPI spec")
        response = normalized[two_xx[0]]

    return (
        response["content"]["application/json"]["schema"]
    )
