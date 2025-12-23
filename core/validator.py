from jsonschema import validate
from jsonschema.exceptions import ValidationError

def validate_schema(data, schema):
    try:
        validate(instance=data, schema=schema)
        return True, None
    except ValidationError as e:
        return False, str(e)
