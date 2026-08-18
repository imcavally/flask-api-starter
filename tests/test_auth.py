"""Authentication flow: register, login, refresh, profile, error cases."""


class TestRegister:
    def test_register_creates_user(self, client):
        res = client.post(
            "/api/v1/auth/register",
            json={"email": "new@example.com", "password": "password123"},
        )
        assert res.status_code == 201
        body = res.get_json()
        assert body["email"] == "new@example.com"
        assert body["role"] == "user"
        assert "password" not in body
        assert "password_hash" not in body

    def test_register_duplicate_email_conflicts(self, client, user):
        res = client.post(
            "/api/v1/auth/register",
            json={"email": user.email, "password": "password123"},
        )
        assert res.status_code == 409

    def test_register_rejects_short_password(self, client):
        res = client.post(
            "/api/v1/auth/register",
            json={"email": "new@example.com", "password": "short"},
        )
        assert res.status_code == 422


class TestLogin:
    def test_login_returns_token_pair(self, client, user):
        res = client.post(
            "/api/v1/auth/login",
            json={"email": user.email, "password": "password123"},
        )
        assert res.status_code == 200
        body = res.get_json()
        assert body["access_token"]
        assert body["refresh_token"]

    def test_login_wrong_password_is_401(self, client, user):
        res = client.post(
            "/api/v1/auth/login",
            json={"email": user.email, "password": "wrong-password"},
        )
        assert res.status_code == 401

    def test_login_unknown_email_is_401(self, client):
        res = client.post(
            "/api/v1/auth/login",
            json={"email": "ghost@example.com", "password": "password123"},
        )
        assert res.status_code == 401


class TestRefresh:
    def test_refresh_issues_new_access_token(self, client, user):
        tokens = client.post(
            "/api/v1/auth/login",
            json={"email": user.email, "password": "password123"},
        ).get_json()
        res = client.post(
            "/api/v1/auth/refresh",
            headers={"Authorization": f"Bearer {tokens['refresh_token']}"},
        )
        assert res.status_code == 200
        assert res.get_json()["access_token"]

    def test_access_token_cannot_refresh(self, client, user_headers):
        res = client.post("/api/v1/auth/refresh", headers=user_headers)
        assert res.status_code == 401


class TestMe:
    def test_me_returns_profile(self, client, user, user_headers):
        res = client.get("/api/v1/auth/me", headers=user_headers)
        assert res.status_code == 200
        assert res.get_json()["email"] == user.email

    def test_me_without_token_is_401(self, client):
        res = client.get("/api/v1/auth/me")
        assert res.status_code == 401
        body = res.get_json()
        assert body["code"] == 401
        assert body["status"] == "Unauthorized"

    def test_me_with_garbage_token_is_401(self, client):
        res = client.get(
            "/api/v1/auth/me", headers={"Authorization": "Bearer not-a-token"}
        )
        assert res.status_code == 401
