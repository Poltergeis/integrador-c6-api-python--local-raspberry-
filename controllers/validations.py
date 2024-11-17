import re
def validate_existing_strings(strings : list[str]):
    return all(strings)

def validate_email(email : str):
    return False if email is None else bool(re.match(r"[^@]+@[^@]+\.[^@]+", email))

def validate_safe_string(string : str):
        return False if string is None else bool(re.match(r"^[a-zA-Z0-9_ ]*$", string))