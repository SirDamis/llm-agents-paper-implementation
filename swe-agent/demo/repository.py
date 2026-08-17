from storage import UserStore


class UserRepository:
    def __init__(self, store=None):
        self.store = store or UserStore()

    def get_user(self, user_id):
        user = self.store.get(user_id)
        if user is None:
            return None

        return {
            "id": user["id"],
            "name": user["name"],
            "email": user["email"],
        }

    def create_user(self, name, email):
        user = {
            "name": name.strip(),
            "email": email.strip().lower(),
        }
        self.store.save(user)
        return user
