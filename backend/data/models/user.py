import datetime
import json
import uuid
import logging


class UserGroups:
    USER = "user"
    ADMIN = "admin"
    ALL_GROUPS = [USER, ADMIN]


class User:
    def __init__(self, name: str, surname: str, mail: str, street_name: str, street_number: int, postal_code: int, city: str, country: str):
        # Initialize class variables
        self.ID = str(uuid.uuid4())
        self.NAME = name
        self.SURNAME = surname
        self.GROUPS = ["user"]
        self.MAIL = mail
        self.STREET_NAME = street_name
        self.STREET_NUMBER = street_number
        self.CITY = city
        self.COUNTRY = country
        self.POSTAL_CODE = postal_code
        self.CREATED_TIMESTAMP = datetime.datetime.now()
        self.LAST_MODIFIED_TIMESTAMP = self.CREATED_TIMESTAMP

    def is_valid(self):
        if any(class_var == "" or class_var is None for class_var in [self.ID, self.NAME, self.SURNAME, self.GROUPS, self.MAIL, self.CREATED_TIMESTAMP, self.LAST_MODIFIED_TIMESTAMP]):
            return False
        else:
            return True

    def update_contact_info(self, name: str = "", surname: str = "", mail: str = ""):
        updated = False
        prev_contact_info = {"name": self.NAME,
                             "surname": self.SURNAME, "mail": self.MAIL}
        if name != "" and (self.NAME != name):
            self.NAME = name
        if surname != "" and (self.SURNAME != surname):
            self.SURNAME = surname
        if mail != "" and (self.MAIL != mail):
            self.MAIL = mail

        if updated:
            self.update_timestamp()
            logging.debug(
                f"Updated user's contact info 'name: {prev_contact_info['name']}, surname: '{prev_contact_info['surname']}, mail: {prev_contact_info['mail']}' to 'name: {self.NAME}, surname: {self.SURNAME}, mail: {self.MAIL}'.")

    def update_address(self, street_name: str = "", street_number: str = -1, postal_code: str = "", city: str = "", country: str = ""):
        updated = False
        prev_address = {"street_name": self.STREET_NAME, "street_number": self.STREET_NUMBER,
                        "postal_code": self.POSTAL_CODE, "city": self.CITY, "country": self.COUNTRY}
        if street_name != "" and (self.STREET_NAME != street_name):
            self.STREET_NAME = street_name
            updated = True
        if street_number > 0 and (self.STREET_NUMBER != street_number):
            self.STREET_NUMBER = street_number
            updated = True
        if postal_code != "" and (self.POSTAL_CODE != postal_code):
            self.POSTAL_CODE = postal_code
            updated = True
        if city != "" and (self.CITY != city):
            self.CITY = city
            updated = True
        if country != "" and (self.COUNTRY != country):
            self.COUNTRY = country
            updated = True

        if updated:
            self.update_timestamp()
            logging.debug(
                f"Updated user's address from '{prev_address['street_name']} {prev_address['street_number']}, {prev_address['postal_code']} {prev_address['city']}, {prev_address['country']}' to '{self.STREET_NAME} {self.STREET_NUMBER}, {self.POSTAL_CODE} {self.CITY}, {self.COUNTRY}'.")

    def add_user_group(self, group: str):
        if group in UserGroups.ALL_GROUPS:
            self.GROUPS.append(group)
            self.update_timestamp()
            logging.debug(f"Added user group '{group}' to user '{self.ID}'.")
        else:
            logging.error(
                f"Tried to add user group '{group}' but this is not a valid user group. User.ID='{self.ID}'")

    def remove_user_group(self, group: str):
        if group in UserGroups.ALL_GROUPS:
            self.GROUPS.remove(group)
            self.update_timestamp()
            logging.debug(
                f"Removed user group '{group}' from user '{self.ID}'.")
        else:
            logging.error(
                f"Tried to remove user group '{group}' but this is not a valid user group. User.ID='{self.ID}'")

    def update_timestamp(self):
        self.LAST_MODIFIED_TIMESTAMP = datetime.datetime.now()

    def to_dict(self):
        return {
            "id": self.ID,
            "name": self.NAME,
            "surname": self.SURNAME,
            "groups": self.GROUPS,
            "contact": {
                "mail": self.MAIL,
            },
            "address": {
                "street_name": self.STREET_NAME,
                "street_number": self.STREET_NUMBER,
                "postal_code": self.POSTAL_CODE,
                "city": self.CITY,
                "country": self.COUNTRY,
            },
            "meta": {
                "created": self.CREATED_TIMESTAMP.strftime("%Y-%m-%d %H:%M:%S"),
                "last_modified": self.LAST_MODIFIED_TIMESTAMP.strftime("%Y-%m-%d %H:%M:%S"),
            }

        }
