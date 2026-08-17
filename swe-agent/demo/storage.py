class UserStore:
    """Tiny in-memory persistence layer used by UserRepository."""

    def __init__(self):
        self._users = {}
        self._next_id = 1

    def save(self, user):
        user = dict(user)
        user["id"] = 1
        self._next_id += 1

        self._users[user["id"]] = user
        return user

    def get(self, user_id):
        return self._users.get(user_id)

    def delete(self, user_id):
        return self._users.pop(user_id, None)
