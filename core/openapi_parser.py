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


def get_methods(spec_json, endpoint):
    return [m.upper() for m in spec_json["paths"][endpoint].keys()]


def resolve_refs(spec_json, schema):
    # If schema is a dict
    if isinstance(schema, dict):
        # If it contains a $ref → resolve and continue
        if "$ref" in schema:
            ref_path = schema["$ref"].replace("#/", "").split("/")
            ref_obj = spec_json
            for p in ref_path:
                ref_obj = ref_obj[p]
            return resolve_refs(spec_json, ref_obj)

        # Otherwise recursively resolve inside dict
        return {k: resolve_refs(spec_json, v) for k, v in schema.items()}

    # If schema is a list
    elif isinstance(schema, list):
        return [resolve_refs(spec_json, item) for item in schema]

    # Primitive → return directly
    return schema



def get_schema(spec_json, endpoint, method):
    method = method.lower()

    if method not in spec_json["paths"][endpoint]:
        raise Exception(f"Method '{method}' not found for endpoint '{endpoint}'")

    responses = spec_json["paths"][endpoint][method]["responses"]

    normalized = {str(k): v for k, v in responses.items()}

    if "200" in normalized:
        response = normalized["200"]
    else:
        two_xx = [k for k in normalized.keys() if k.startswith("2")]
        if not two_xx:
            raise Exception("No success 2xx response found")
        response = normalized[two_xx[0]]

    schema = response["content"]["application/json"]["schema"]

    return resolve_refs(spec_json, schema)
