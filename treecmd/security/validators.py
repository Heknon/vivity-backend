import re

from password_validator import PasswordValidator

VALIDATOR = PasswordValidator().min(8).letters()
EMAIL_REGEX = re.compile(r"^(([^<>()[\]\.,;:\s@\"]+(\.[^<>()[\]\.,;:\s@\"]+)*)|(\".+\"))@(([^<>()[\]\.,;:\s@\"]+\.)+[^<>()[\]\.,;:\s@\"]{2,})$")
