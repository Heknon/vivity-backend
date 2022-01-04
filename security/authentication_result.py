from enum import Enum


class AuthenticationResult(Enum):
    TokenInvalid = 0
    EmailExists = 1
    PasswordIncorrect = 2
    PresentInBlacklist = 3
    Success = 4
    NotBusiness = 5
    MissingFields = 6
