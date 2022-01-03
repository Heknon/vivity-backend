class AuthorizedRouteRequestBody:
    def __init__(self, authorization_id: str):
        self.authorization_id = authorization_id


class ForgotPasswordAuthorizedRouteRequestBody(AuthorizedRouteRequestBody):
    def __init__(self, authorization_id: str, password: str):
        super().__init__(authorization_id)
        self.password = password
