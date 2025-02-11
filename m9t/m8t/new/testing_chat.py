import json
import hashlib
def hash_string(input_string):
    hash_object = hashlib.sha256()
    hash_object.update(input_string.encode('utf-8'))
    return hash_object.hexdigest()
username_passwords = [("admin",hash_string("12345"))]
with open("username_passwords.json", "w+") as file:
    json.dump(username_passwords, file)