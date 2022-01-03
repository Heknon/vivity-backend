class TokenData:
    def __init__(self, email, username, user_id):
        self.email = email
        self.username = username
        self.user_id = user_id


class BusinessUserTokenData(TokenData):
    def __init__(self, email, username, user_id, business_name, business_id):
        super().__init__(email, username, user_id)
        self.business_name = business_name
        self.business_id = business_id
