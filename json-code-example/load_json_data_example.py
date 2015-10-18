import json

# you can also use the open function to read the content of a file to a string
json_data = """ {
    "key 1": "value 1",
    "key 2": "value 2",
    "decimal": 10,
    "boolean": true,
    "list": [1, 2, 3],
    "dictionary": {
        "child key 1": "child value",
        "child key 1": "child value"
    }
}"""

my_dict = json.loads(json_data)

# keys() example
print("keys at the first level within the dictionary")
for key in my_dict.keys():
    print("    %s" % key)
print("\n\n")

# access values in the dictionary
print("string value: %s" % my_dict["key 1"])
print("decimal value: %d" % my_dict["decimal"])
print("decimal value: %r" % my_dict["boolean"])
print("list values: %s" % my_dict["list"])
