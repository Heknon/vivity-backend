from enum import Enum


class AuthenticationResult(Enum):
    TokenInvalid = 0
    EmailExists = 1
    PasswordIncorrect = 2
    PresentInBlacklist = 3
    Success = 4
    NotBusiness = 5
    MissingFields = 6
    EmailIncorrect = 7
    PasswordInvalid = 8
    EmailInvalid = 9
    WrongOTP = 10
    TooManyAttempts = 11
    OTPBlocked = 12

