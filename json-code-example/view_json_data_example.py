import json

my_dictionary = {
    "key 1": "Value 1",
    "key 2": "Value 2",
    "decimal": 100,
    "boolean": False,
    "list": [1, 2, 3],
    "dict": {
        "child key 1": "value 1",
        "child key 2": "value 2"
    }
}

print(json.dumps(my_dictionary))
print(json.dumps(my_dictionary, indent=4))
print(json.dumps(my_dictionary, indent=4, sort_keys=True))
