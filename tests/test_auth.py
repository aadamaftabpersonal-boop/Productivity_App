import pytest

pytestmark = pytest.mark.asyncio


async def test_register_and_login(client):
    r = await client.post("/auth/register", json={
        "email": "a@b.com", "password": "supersecret1", "full_name": "A B"
    })
    assert r.status_code == 201

    r = await client.post("/auth/login", json={"email": "a@b.com", "password": "supersecret1"})
    assert r.status_code == 200
    body = r.json()
    assert "access_token" in body and "refresh_token" in body


async def test_login_wrong_password_rejected(client):
    await client.post("/auth/register", json={
        "email": "a@b.com", "password": "supersecret1", "full_name": "A B"
    })
    r = await client.post("/auth/login", json={"email": "a@b.com", "password": "wrong"})
    assert r.status_code == 401


async def test_refresh_rotates_token(client, registered_user):
    _, _, tokens = registered_user
    old_refresh = tokens["refresh_token"]

    r = await client.post("/auth/refresh", json={"refresh_token": old_refresh})
    assert r.status_code == 200
    new_tokens = r.json()

    # rotation actually happened: new refresh token differs from the old one
    assert new_tokens["refresh_token"] != old_refresh

    # the OLD refresh token must now be dead — using it again should fail
    r2 = await client.post("/auth/refresh", json={"refresh_token": old_refresh})
    assert r2.status_code == 401


async def test_refresh_reuse_revokes_entire_family(client, registered_user):
    """The core security property CP Hub claims: if a revoked refresh token is
    replayed (token theft scenario), the ENTIRE token family should be killed,
    not just that one token — so a stolen-then-rotated token can't be used to
    silently re-establish a session via a still-valid sibling token.
    """
    _, _, tokens = registered_user
    original_refresh = tokens["refresh_token"]

    # Legitimate rotation happens once
    r1 = await client.post("/auth/refresh", json={"refresh_token": original_refresh})
    assert r1.status_code == 200
    rotated_tokens = r1.json()
    new_refresh = rotated_tokens["refresh_token"]

    # Attacker replays the OLD (now-revoked) token -> reuse detected
    r2 = await client.post("/auth/refresh", json={"refresh_token": original_refresh})
    assert r2.status_code == 401
    assert "reuse" in r2.json()["detail"].lower()

    # The legitimate rotated token must ALSO now be dead, because the whole
    # family was revoked -- this is the property that separates "reuse
    # detection" from just "can't use an old token twice"
    r3 = await client.post("/auth/refresh", json={"refresh_token": new_refresh})
    assert r3.status_code == 401


async def test_logout_revokes_token(client, registered_user):
    _, _, tokens = registered_user
    refresh = tokens["refresh_token"]

    r = await client.post("/auth/logout", json={"refresh_token": refresh})
    assert r.status_code == 204

    r2 = await client.post("/auth/refresh", json={"refresh_token": refresh})
    assert r2.status_code == 401
