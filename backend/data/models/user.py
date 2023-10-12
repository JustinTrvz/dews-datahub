import datetime
import uuid


class User:
    def __init__(self, name: str, surname: str, mail: str, street_name: str, street_number: int, postal_code: int, city: str, country: str):
        # Initialize class variables
        self.ID = str(uuid.uuid4())
        self.NAME = name
        self.SURNAME = surname
        self.MAIL = mail
        self.STREET_NAME = street_name
        self.STREET_NUMBER = street_number
        self.CITY = city
        self.COUNTRY = country
        self.POSTAL_CODE = postal_code
        self.CREATED_TIMESTAMP = datetime.datetime.now()
        self.LAST_MODIFIED_TIMESTAMP = self.CREATED_TIMESTAMP

    def is_valid(self):
        if any(class_var == "" or class_var is None for class_var in [self.ID, self.NAME, self.SURNAME, self.MAIL, self.CREATED_TIMESTAMP, self.LAST_MODIFIED_TIMESTAMP]):
            return False
        else:
            return True

    def to_dict(self):
        return {
            "id": self.ID,
            "name": self.NAME,
            "surname": self.SURNAME,
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
