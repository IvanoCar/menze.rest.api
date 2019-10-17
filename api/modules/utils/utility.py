from uuid import uuid4

class Utility:
    @staticmethod
    def generate_uuid():
        return uuid4().hex
