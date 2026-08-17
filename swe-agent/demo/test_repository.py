from repository import UserRepository
from storage import UserStore


def test_create_and_get_user():
    repo = UserRepository(UserStore())

    created = repo.create_user(" Ada Lovelace ", " ADA@EXAMPLE.COM ")

    assert created["id"] == 1
    assert created["name"] == "Ada Lovelace"
    assert created["email"] == "ada@example.com"

    fetched = repo.get_user(1)
    assert fetched == {
        "id": 1,
        "name": "Ada Lovelace",
        "email": "ada@example.com",
    }


def test_user_ids_are_unique_across_creates():
    repo = UserRepository(UserStore())

    first = repo.create_user("Ada", "ada@example.com")
    second = repo.create_user("Grace", "grace@example.com")

    assert first["id"] != second["id"]
    assert first["id"] == 1
    assert second["id"] == 2


def test_delete_removes_user():
    store = UserStore()
    repo = UserRepository(store)

    repo.create_user("Ada", "ada@example.com")
    assert store.delete(1)["name"] == "Ada"
    assert repo.get_user(1) is None
