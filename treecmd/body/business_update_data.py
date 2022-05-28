from body.business_contact_info import BusinessContactInfo
from database import Location


class BusinessUpdateData:
    def __init__(self, name: str, location: Location, contact: BusinessContactInfo):
        self.name = name
        self.contact = contact
        self.location = location
