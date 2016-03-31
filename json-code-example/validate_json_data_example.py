"""
example script to validate JSON data against a user defined schema
"""
import ipaddress
import yaml
import json
from cerberus import Validator

# JSON schema for the validation (as a python dictionary)
schema_json = {
    "networks": {
        "type": "list",
        "schema": {
            "type": "dict",
            "schema": {
                "vlan": {
                    "type": "dict",
                    "schema": {
                        "id": {
                            "type": "integer",
                            "min": 1,
                            "max": 4094
                        },
                        "name": {
                            "type": "string"
                        }
                    }
                },
                "ipv4": {
                    "type": "dict",
                    "schema": {
                        "address": {
                            "type": "ipv4address"
                        },
                        "prefix_length": {
                            "type": "integer"
                        }
                    }
                }
            }
        }
    }
}

# same schema as above (YAML formatted)
raw_schema_yaml = """
networks:
 type: list
 schema:
  type: dict
  schema:
   vlan:
    type: dict
    schema:
     id:
      type: integer
      min: 1
      max: 4094
     name:
      type: string
   ipv4:
    type: dict
    schema:
     address:
      type: ipv4address
     prefix_length:
      type: integer
"""
schema_yaml = yaml.load(raw_schema_yaml)


class NetworkDataJsonValidator(Validator):
    """
    A simple JSON data validator with a custom data type for IPv4 addresses
    """
    def _validate_type_ipv4address(self, field, value):
        """
        checks that the given value is a valid IPv4 address
        """
        try:
            # try to create an IPv4 address object using the python3 ipaddress module
            ipaddress.IPv4Address(value)
        except:
            self._error(field, "Not a valid IPv4 address")


if __name__ == "__main__":
    # some example data
    valid_sample_data = {
        "networks": [
            {
                "vlan" : {
                    "id": 1,
                    "name": "data"
                },
                "ipv4": {
                    "address": "10.1.1.1",
                    "prefix_length": 24
                }
            }
        ]
    }
    invalid_sample_data = {
        "networks": [
            {
                "vlan": {
                    "id": 5000,
                    "name": "data"
                },
                "ipv4": {
                    "address": "FE80::1",
                    "prefix_length": 24
                }
            }
        ]
    }

    # create an instance of the NetworkDataJsonValidator
    validator_json = NetworkDataJsonValidator(schema_json)
    validator_yaml = NetworkDataJsonValidator(schema_yaml)

    # validate the valid sample data
    print("validate the valid sample data")
    result_json = validator_json.validate(valid_sample_data)
    print("--> data validation result (using the JSON expressed schema): %s" % result_json)
    result_yaml = validator_yaml.validate(valid_sample_data)
    print("--> data validation result (using the JSON expressed schema): %s" % result_yaml)

    # validate the invalid sample data
    print("validate the invalid sample data")
    result_json = validator_json.validate(invalid_sample_data)
    print("--> data validation result (using the JSON expressed schema): %s" % result_json)
    print("--> Validation errors:")
    print(json.dumps(validator_json.errors, indent=4))

    result_yaml = validator_yaml.validate(invalid_sample_data)
    print("--> data validation result (using the JSON expressed schema): %s" % result_yaml)
    print("--> Validation errors:")
    print(json.dumps(validator_yaml.errors, indent=4))
