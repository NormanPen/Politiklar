"""Tests for authentication, user management, API keys, and user favorites."""

import hashlib
from uuid import uuid4

from fastapi.testclient import TestClient


def test_oauth_sync_new_and_existing_user(client: TestClient) -> None:
    # 1. Sync new Google user
    payload = {
        "provider": "google",
        "provider_account_id": "google-sub-123456",
        "email": "testuser@example.org",
        "name": "Test User",
        "avatar_url": "https://example.org/avatar.jpg",
    }
    response = client.post("/api/v1/auth/oauth-sync", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "testuser@example.org"
    assert data["name"] == "Test User"
    assert data["role"] == "user"
    assert data["is_active"] is True
    user_id = data["id"]

    # 2. Sync same user with updated name
    update_payload = {
        "provider": "google",
        "provider_account_id": "google-sub-123456",
        "email": "testuser@example.org",
        "name": "Updated Test User",
        "avatar_url": "https://example.org/new-avatar.jpg",
    }
    response2 = client.post("/api/v1/auth/oauth-sync", json=update_payload)
    assert response2.status_code == 200
    data2 = response2.json()
    assert data2["id"] == user_id
    assert data2["name"] == "Updated Test User"
    assert data2["avatar_url"] == "https://example.org/new-avatar.jpg"


def test_get_user_profile(client: TestClient) -> None:
    # Unknown user returns 404
    unknown_id = str(uuid4())
    res_404 = client.get(f"/api/v1/auth/users/{unknown_id}")
    assert res_404.status_code == 404

    # Create user
    res_create = client.post(
        "/api/v1/auth/oauth-sync",
        json={
            "provider": "google",
            "provider_account_id": "google-profile-1",
            "email": "profile@example.org",
            "name": "Profile Person",
        },
    )
    user_id = res_create.json()["id"]

    # Fetch user
    res_get = client.get(f"/api/v1/auth/users/{user_id}")
    assert res_get.status_code == 200
    assert res_get.json()["email"] == "profile@example.org"


def test_api_keys_workflow(client: TestClient) -> None:
    res_user = client.post(
        "/api/v1/auth/oauth-sync",
        json={
            "provider": "google",
            "provider_account_id": "google-key-user",
            "email": "apikey@example.org",
            "name": "API Key User",
        },
    )
    user_id = res_user.json()["id"]

    # Create key
    res_key = client.post(
        f"/api/v1/auth/users/{user_id}/api-keys",
        json={"name": "MCP Server Key"},
    )
    assert res_key.status_code == 201
    key_data = res_key.json()
    assert key_data["name"] == "MCP Server Key"
    assert "raw_key" in key_data
    assert key_data["raw_key"].startswith("pk_")
    assert key_data["key_prefix"].startswith("pk_live_")

    raw_key = key_data["raw_key"]
    calculated_hash = hashlib.sha256(raw_key.encode("utf-8")).hexdigest()

    # List keys (raw_key should NOT be included in list)
    res_list = client.get(f"/api/v1/auth/users/{user_id}/api-keys")
    assert res_list.status_code == 200
    keys = res_list.json()
    assert len(keys) == 1
    assert keys[0]["name"] == "MCP Server Key"
    assert "raw_key" not in keys[0]


def test_favorites_workflow(client: TestClient) -> None:
    res_user = client.post(
        "/api/v1/auth/oauth-sync",
        json={
            "provider": "google",
            "provider_account_id": "google-fav-user",
            "email": "fav@example.org",
            "name": "Favorites User",
        },
    )
    user_id = res_user.json()["id"]
    entity_id = str(uuid4())

    # Add favorite
    res_add = client.post(
        f"/api/v1/auth/users/{user_id}/favorites",
        json={"entity_type": "bundestag_member", "entity_id": entity_id},
    )
    assert res_add.status_code == 201
    fav_id = res_add.json()["id"]

    # Idempotent re-add returns same record
    res_readd = client.post(
        f"/api/v1/auth/users/{user_id}/favorites",
        json={"entity_type": "bundestag_member", "entity_id": entity_id},
    )
    assert res_readd.status_code == 201
    assert res_readd.json()["id"] == fav_id

    # List favorites
    res_list = client.get(f"/api/v1/auth/users/{user_id}/favorites")
    assert res_list.status_code == 200
    favs = res_list.json()
    assert len(favs) == 1
    assert favs[0]["entity_type"] == "bundestag_member"

    # Remove favorite
    res_del = client.delete(f"/api/v1/auth/users/{user_id}/favorites/{fav_id}")
    assert res_del.status_code == 204

    # List is now empty
    res_list_after = client.get(f"/api/v1/auth/users/{user_id}/favorites")
    assert len(res_list_after.json()) == 0
