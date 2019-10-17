class RestaurantDoesntExistError(Exception):
    def __init__(self):
        self.message = "Restaurant with given ID doesn't exist."
