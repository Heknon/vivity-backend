from __future__ import annotations


class UserSettings:
    def __init__(
            self,
            email: str,
            phone: str,
            currency_type: str,
            unit: int,

    ):
        self.email = email
        self.phone = phone
        self.unit = unit
        self.currency_type = currency_type
