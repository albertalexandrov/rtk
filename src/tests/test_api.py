import dateutil.parser
import pytest
from starlette import status


class TestCreateUser:
    async def test_empty_body(self, client):
        resp = await client.post("/users")

        assert resp.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    @pytest.mark.parametrize(
        "field,bad_value",
        [
            ("name", ""),
            ("name", "a" * 256),
            ("surname", ""),
            ("surname", "a" * 256),
            ("email", "NOT-EMAIL"),
            ("email", "a" * 255 + "@mail.ru"),
            ("birthday", "NOT-DATE"),
        ],
    )
    async def test_bad_values(self, field, bad_value, client):
        payload = {
            "name": "Иван",
            "surname": "Иванов",
            "email": "ivan.ivanov.2023.2024@yandex.com",
            "birthday": "2005-10-23T04:00:00+03:00",
        }
        payload[field] = bad_value
        resp = await client.post("/users", json=payload)

        assert resp.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

        detail = resp.json()["detail"][0]

        assert detail["loc"][1] == field
        assert detail["input"] == bad_value

    async def test_created(self, client, users_repository):
        payload = {
            "name": "Иван",
            "surname": "Иванов",
            "email": "ivan.ivanov.2023.2024@yandex.com",
            "birthday": "2005-10-23T04:00:00+03:00",
        }

        resp = await client.post("/users", json=payload)

        assert resp.status_code == status.HTTP_201_CREATED

        user = await users_repository.get()
        resp_body = resp.json()

        assert resp_body["id"] == user.id
        assert resp_body["name"] == user.name
        assert resp_body["surname"] == user.surname
        assert resp_body["email"] == user.email
        assert dateutil.parser.parse(resp_body["birthday"]) == user.birthday


class TestGetUser:
    async def test_404(self, client):
        resp = await client.get("/user/1")

        assert resp.status_code == status.HTTP_404_NOT_FOUND

    async def test_200(self, client):
        payload = {
            "name": "Иван",
            "surname": "Иванов",
            "email": "ivan.ivanov.2023.2024@yandex.com",
            "birthday": "2005-10-23T04:00:00+03:00",
        }

        create_user_resp = await client.post("/users", json=payload)

        assert create_user_resp.status_code == status.HTTP_201_CREATED

        create_user_resp_body = create_user_resp.json()
        user_id = create_user_resp_body["id"]
        get_user_resp = await client.get(f"/users/{user_id}")

        assert get_user_resp.status_code == status.HTTP_200_OK

        get_user_resp_body = get_user_resp.json()

        assert get_user_resp_body == create_user_resp_body


class TestDeleteUser:
    async def test_404(self, client):
        resp = await client.delete("/user/1")

        assert resp.status_code == status.HTTP_404_NOT_FOUND

    async def test_200(self, client):
        payload = {
            "name": "Иван",
            "surname": "Иванов",
            "email": "ivan.ivanov.2023.2024@yandex.com",
            "birthday": "2005-10-23T04:00:00+03:00",
        }

        create_user_resp = await client.post("/users", json=payload)

        assert create_user_resp.status_code == status.HTTP_201_CREATED

        create_user_resp_body = create_user_resp.json()
        user_id = create_user_resp_body["id"]

        delete_user_resp = await client.delete(f"/users/{user_id}")

        assert delete_user_resp.status_code == status.HTTP_200_OK

        get_user_resp = await client.get(f"/users/{user_id}")

        assert get_user_resp.status_code == status.HTTP_404_NOT_FOUND


class TestUpdateUser:
    async def test_404(self, client):
        resp = await client.delete("/user/1")

        assert resp.status_code == status.HTTP_404_NOT_FOUND

    async def test_full_update(self, client):
        payload = {
            "name": "Иван",
            "surname": "Иванов",
            "email": "ivan.ivanov.2023.2024@yandex.com",
            "birthday": "2005-10-23T04:00:00+03:00",
        }

        create_user_resp = await client.post("/users", json=payload)

        assert create_user_resp.status_code == status.HTTP_201_CREATED

        user_id = create_user_resp.json()["id"]

        update_data = {
            "name": "Сергей",
            "surname": "Сергеев",
            "email": "sergey.sergeev@yandex.com",
            "birthday": "2005-01-01T08:00:00+03:00",
        }

        resp = await client.get(f"/users/{user_id}")

        assert resp.status_code == 200

        update_user_resp = await client.patch(f"/users/{user_id}", json=update_data)

        assert update_user_resp.status_code == status.HTTP_200_OK

        update_user_resp_body = update_user_resp.json()

        assert update_user_resp_body["name"] == update_data["name"]
        assert update_user_resp_body["surname"] == update_data["surname"]
        assert update_user_resp_body["email"] == update_data["email"]
        assert dateutil.parser.parse(
            update_user_resp_body["birthday"]
        ) == dateutil.parser.parse(update_data["birthday"])
