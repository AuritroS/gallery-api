import os, sys, datetime, pytest
from dotenv import load_dotenv
import pytest

# make project root importable
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app import app
from mongoengine import connect, disconnect
import certifi

from models.user import User
from models.tribe import Tribe
from models.artist import Artist
from models.artifact import Artifact

# ─── DB setup ───────────────────────────────────────────────
load_dotenv()
TEST_DB = os.getenv("MONGO_URI")


def _mongo_tls_enabled() -> bool:
    return os.getenv("MONGO_TLS", "true").lower() == "true"


disconnect()
connect(
    host=TEST_DB,
    uuidRepresentation="standard",
    alias="default",
    tls=_mongo_tls_enabled(),
tlsCAFile=certifi.where() if _mongo_tls_enabled() else None,

)


# ─── Auto-clear DB before each test ─────────────────────────
@pytest.fixture(autouse=True)
def _clear_db():
    User.drop_collection()
    Tribe.drop_collection()
    Artist.drop_collection()
    Artifact.drop_collection()


# ─── Flask test-client ─────────────────────────────────────
@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as c:
        yield c


# ─── Helper: register + login -> auth header ───────────────
@pytest.fixture
def auth_header(client):
    creds = {"username": "alice", "password": "secret"}
    print("[auth_header] registering and logging in user 'alice'")
    client.post("/auth/register", json=creds)
    # immediately promote alice to admin
    from models.user import User

    u = User.objects.get(username="alice")
    u.role = "admin"
    u.save()
    tok = client.post("/auth/login", json=creds).get_json()["access_token"]
    return {"Authorization": f"Bearer {tok}"}


# ─── Health -------------------------------------------------
def test_health(client):
    print("[test_health] GET /health/db should return db_status=OK")
    r = client.get("/health/db")
    assert r.status_code == 200
    assert r.get_json()["db_status"] == "OK"


# ─── Unauth check (write should 401) -----------------------
def test_unauthorized_write(client):
    print("[test_unauthorized_write] POST /api/v1/tribes/ without token → 401")
    r = client.post("/api/v1/tribes/", json={"name": "X", "region": "Y"})
    assert r.status_code == 401


# ─── Tribes CRUD -------------------------------------------
def test_tribes_crud(client, auth_header):
    print(
        "[test_tribes_crud] Tribes CRUD: list empty → create → fetch → update → delete"
    )
    # list empty
    assert client.get("/api/v1/tribes/").get_json() == []

    # create
    t = client.post(
        "/api/v1/tribes/",
        headers=auth_header,
        json={"name": "Wiradjuri", "region": "NSW"},
    ).get_json()
    tid = t["id"]

    # fetch
    assert client.get(f"/api/v1/tribes/{tid}").status_code == 200

    # update
    upd = client.put(
        f"/api/v1/tribes/{tid}", headers=auth_header, json={"description": "Updated"}
    ).get_json()
    assert upd["description"] == "Updated"

    # delete
    assert (
        client.delete(f"/api/v1/tribes/{tid}", headers=auth_header).status_code == 204
    )


# ─── Artists CRUD ------------------------------------------
def test_artists_crud(client, auth_header):
    print(
        "[test_artists_crud] Artists CRUD: create tribe → create artist → list → update → delete"
    )
    # need a tribe first
    tid = client.post(
        "/api/v1/tribes/", headers=auth_header, json={"name": "Noongar", "region": "WA"}
    ).get_json()["id"]

    # create artist
    a = client.post(
        "/api/v1/artists/",
        headers=auth_header,
        json={
            "name": "Artist1",
            "bio": "Bio",
            "tribe": tid,
            "active_years": [1990, 2000],
        },
    ).get_json()
    aid = a["id"]

    # list
    assert len(client.get("/api/v1/artists/").get_json()) == 1

    # update
    up = client.put(
        f"/api/v1/artists/{aid}", headers=auth_header, json={"bio": "New"}
    ).get_json()
    assert up["bio"] == "New"

    # delete
    assert (
        client.delete(f"/api/v1/artists/{aid}", headers=auth_header).status_code == 204
    )


# ─── Artifacts CRUD ----------------------------------------
def test_artifacts_crud(client, auth_header):
    print(
        "[test_artifacts_crud] Artifacts CRUD: create tribe/artist → create artifact → list → update → delete"
    )
    # tribe + artist
    tid = client.post(
        "/api/v1/tribes/",
        headers=auth_header,
        json={"name": "Pitjantjatjara", "region": "Central"},
    ).get_json()["id"]
    aid = client.post(
        "/api/v1/artists/",
        headers=auth_header,
        json={"name": "A1", "tribe": tid, "active_years": [1950, 1990]},
    ).get_json()["id"]

    # create artifact
    art = client.post(
        "/api/v1/artifacts/",
        headers=auth_header,
        json={
            "title": "Art1",
            "artist": aid,
            "created_date": datetime.datetime.utcnow().isoformat(),
        },
    ).get_json()
    art_id = art["id"]

    # list
    assert client.get("/api/v1/artifacts/").status_code == 200

    # update
    au = client.put(
        f"/api/v1/artifacts/{art_id}", headers=auth_header, json={"era": "Contemporary"}
    ).get_json()
    assert au["era"] == "Contemporary"

    # delete
    assert (
        client.delete(f"/api/v1/artifacts/{art_id}", headers=auth_header).status_code
        == 204
    )


# ─── Auth edge cases ---------------------------------------
def test_register_duplicate_username(client):
    print("[test_register_duplicate_username] register same user twice → 400")
    creds = {"username": "bob", "password": "pw"}
    r1 = client.post("/auth/register", json=creds)
    assert r1.status_code == 201

    r2 = client.post("/auth/register", json=creds)
    assert r2.status_code == 400
    assert "Username already exists" in r2.get_json()["message"]


def test_login_bad_credentials(client):
    print("[test_login_bad_credentials] login unregistered or wrong-password → 401")
    # unregistered user → 401
    r = client.post("/auth/login", json={"username": "nobody", "password": "x"})
    assert r.status_code == 401

    # wrong password → 401
    client.post("/auth/register", json={"username": "alice", "password": "secret"})
    r = client.post("/auth/login", json={"username": "alice", "password": "nope"})
    assert r.status_code == 401


# ─── Validation errors -------------------------------------
@pytest.mark.parametrize(
    "route,payload",
    [
        ("/api/v1/tribes/", {"region": "X"}),  # missing `name`
        ("/api/v1/tribes/", {"name": "X"}),  # missing `region`
        ("/api/v1/artists/", {"name": "A", "tribe": "t"}),  # missing `active_years`
        ("/api/v1/artifacts/", {"artist": "a"}),  # missing `title`
    ],
)
def test_create_validation_errors(client, auth_header, route, payload):
    print(
        f"[test_create_validation_errors] POST {route} with invalid payload {payload} → 422"
    )
    r = client.post(route, headers=auth_header, json=payload)
    assert r.status_code == 422


# ─── Not-found edge cases ---------------------------------
def test_404_on_unknown_tribe(client, auth_header):
    print("[test_404_on_unknown_tribe] GET/PUT/DELETE unknown tribe_id → 404")
    assert client.get("/api/v1/tribes/abcdef").status_code == 404
    assert (
        client.put("/api/v1/tribes/abcdef", headers=auth_header, json={}).status_code
        == 404
    )
    assert (
        client.delete("/api/v1/tribes/abcdef", headers=auth_header).status_code == 404
    )


def test_create_artist_with_bad_tribe(client, auth_header):
    print(
        "[test_create_artist_with_bad_tribe] POST /api/v1/artists/ with non-existent tribe → 404"
    )
    bad = {
        "name": "A",
        "tribe": "000000000000000000000000",
        "active_years": [2000, 2001],
    }
    r = client.post("/api/v1/artists/", headers=auth_header, json=bad)
    assert r.status_code == 404
    assert "Tribe not found" in r.get_json()["message"]


def test_create_artifact_with_bad_artist(client, auth_header):
    print(
        "[test_create_artifact_with_bad_artist] POST /api/v1/artifacts/ with non-existent artist → 404"
    )
    bad = {
        "title": "X",
        "artist": "000000000000000000000000",
        "created_date": "2025-01-01T00:00:00",
    }
    r = client.post("/api/v1/artifacts/", headers=auth_header, json=bad)
    assert r.status_code == 404
    assert "Artist not found" in r.get_json()["message"]


# ─── Authorization errors ----------------------------------
def test_protected_routes_require_token(client):
    print("[test_protected_routes_require_token] write endpoints without token → 401")
    r = client.post("/api/v1/tribes/", json={"name": "X", "region": "Y"})
    assert r.status_code == 401


def test_protected_routes_reject_invalid_token(client):
    print(
        "[test_protected_routes_reject_invalid_token] write endpoints with invalid token → 401/422"
    )
    r = client.post(
        "/api/v1/tribes/",
        headers={"Authorization": "Bearer invalid.token.here"},
        json={"name": "X", "region": "Y"},
    )
    assert r.status_code in (401, 422)


# ─── Extra fields rejection --------------------------------
def test_unknown_field_rejection(client, auth_header):
    print("[test_unknown_field_rejection] POST /api/v1/tribes/ with extra field → 422")
    r = client.post(
        "/api/v1/tribes/",
        headers=auth_header,
        json={"name": "X", "region": "Y", "foo": "bar"},
    )
    assert r.status_code == 422


@pytest.fixture(scope="session", autouse=True)
def cleanup_test_db(request):
    """
    After the entire test session finishes, drop all test collections
    so nothing lingers in the test database.
    """

    def teardown():
        from models.user import User
        from models.tribe import Tribe
        from models.artist import Artist
        from models.artifact import Artifact

        print("\n[cleanup_test_db] Dropping test collections…")
        User.drop_collection()
        Tribe.drop_collection()
        Artist.drop_collection()
        Artifact.drop_collection()
        print("[cleanup_test_db] Done.")

    request.addfinalizer(teardown)
