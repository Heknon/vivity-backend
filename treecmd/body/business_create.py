class BusinessCreate:
    def __init__(
            self,
            name: str,
            email: str,
            phone: str,
            latitude: float,
            longitude: float,
            business_national_number: str,
            owner_id: str
    ):
        self.name = name
        self.email = email
        self.phone = phone
        self.latitude = latitude
        self.longitude = longitude
        self.business_national_number = business_national_number
        self.owner_id = owner_id
