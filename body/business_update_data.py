from typing import Dict

from body.business_contact_info import BusinessContactInfo


class BusinessUpdateData:
    def __init__(self, name: str, add_locations: [Dict[str, int]], remove_locations: [Dict[str, int]], contact: BusinessContactInfo):
        self.name = name
        self.add_locations = add_locations
        self.remove_locations = remove_locations
        self.contact = contact
