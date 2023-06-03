class User:
    def __init__(self, id):
        self.id = id
        self.username = None
        self.password = None

    def get_id(self):
        return str(self.id)

    @classmethod
    def get(cls, id):
        # Retrieve user from the database based on the ID
        # You can use this method to fetch user details from your user database
        # and populate the User instance attributes
        user = User(id)
        user.username = "admin"
        user.password = "admin"
        return user
