import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base, get_db
from app.main import app

SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)

@pytest.fixture(scope="function", autouse=True)
def setup_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

# --- Health ---
def test_health_check():
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"
    assert response.json()["stack"] == "python"

# --- Tournaments ---
def test_create_tournament():
    response = client.post("/tournaments/", json={
        "name": "Torneio Teste",
        "description": "Descrição",
        "max_players": 16,
        "prize": "1000 moedas"
    })
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Torneio Teste"
    assert data["status"] == "open"
    assert data["max_players"] == 16

def test_list_tournaments():
    client.post("/tournaments/", json={"name": "T1"})
    client.post("/tournaments/", json={"name": "T2"})
    response = client.get("/tournaments/")
    assert response.status_code == 200
    assert len(response.json()) == 2

def test_get_tournament():
    create = client.post("/tournaments/", json={"name": "T1"})
    tid = create.json()["id"]
    response = client.get(f"/tournaments/{tid}")
    assert response.status_code == 200
    assert response.json()["name"] == "T1"

def test_update_tournament():
    create = client.post("/tournaments/", json={"name": "T1"})
    tid = create.json()["id"]
    response = client.put(f"/tournaments/{tid}", json={"name": "T1 Atualizado"})
    assert response.status_code == 200
    assert response.json()["name"] == "T1 Atualizado"

def test_delete_tournament():
    create = client.post("/tournaments/", json={"name": "T1"})
    tid = create.json()["id"]
    response = client.delete(f"/tournaments/{tid}")
    assert response.status_code == 204

# --- Players ---
def test_register_player():
    t = client.post("/tournaments/", json={"name": "T1"})
    tid = t.json()["id"]
    response = client.post(f"/players/tournament/{tid}", json={
        "nickname": "Player1",
        "server": "S1",
        "level": 50,
        "power": 10000
    })
    assert response.status_code == 201
    assert response.json()["nickname"] == "Player1"

def test_duplicate_nickname():
    t = client.post("/tournaments/", json={"name": "T1"})
    tid = t.json()["id"]
    client.post(f"/players/tournament/{tid}", json={"nickname": "Player1", "server": "S1"})
    response = client.post(f"/players/tournament/{tid}", json={"nickname": "Player1", "server": "S2"})
    assert response.status_code == 400

def test_max_players_limit():
    t = client.post("/tournaments/", json={"name": "T1", "max_players": 2})
    tid = t.json()["id"]
    client.post(f"/players/tournament/{tid}", json={"nickname": "P1", "server": "S1"})
    client.post(f"/players/tournament/{tid}", json={"nickname": "P2", "server": "S1"})
    response = client.post(f"/players/tournament/{tid}", json={"nickname": "P3", "server": "S1"})
    assert response.status_code == 400

# --- Bracket ---
def test_generate_bracket_insufficient_players():
    t = client.post("/tournaments/", json={"name": "T1"})
    tid = t.json()["id"]
    client.post(f"/players/tournament/{tid}", json={"nickname": "P1", "server": "S1"})
    response = client.post(f"/tournaments/{tid}/start")
    assert response.status_code == 400

def test_generate_bracket_even_players():
    t = client.post("/tournaments/", json={"name": "T1"})
    tid = t.json()["id"]
    for i in range(4):
        client.post(f"/players/tournament/{tid}", json={"nickname": f"P{i}", "server": "S1"})
    response = client.post(f"/tournaments/{tid}/start")
    assert response.status_code == 200
    assert response.json()["status"] == "ongoing"
    matches = client.get(f"/matches/tournament/{tid}")
    assert len(matches.json()) == 2

def test_generate_bracket_odd_players():
    t = client.post("/tournaments/", json={"name": "T1"})
    tid = t.json()["id"]
    for i in range(3):
        client.post(f"/players/tournament/{tid}", json={"nickname": f"P{i}", "server": "S1"})
    response = client.post(f"/tournaments/{tid}/start")
    assert response.status_code == 200
    matches = client.get(f"/matches/tournament/{tid}")
    data = matches.json()
    assert len(data) == 2
    bye_match = [m for m in data if m["player_b_id"] is None]
    assert len(bye_match) == 1
    assert bye_match[0]["status"] == "finished"
    assert bye_match[0]["winner_id"] == bye_match[0]["player_a_id"]

def test_set_winner_and_advance():
    t = client.post("/tournaments/", json={"name": "T1"})
    tid = t.json()["id"]
    for i in range(4):
        client.post(f"/players/tournament/{tid}", json={"nickname": f"P{i}", "server": "S1"})
    client.post(f"/tournaments/{tid}/start")
    matches = client.get(f"/matches/tournament/{tid}").json()
    m1 = matches[0]
    winner_id = m1["player_a_id"]
    client.post(f"/matches/{m1['id']}/winner/{winner_id}")
    m2 = matches[1]
    winner_id2 = m2["player_b_id"]
    client.post(f"/matches/{m2['id']}/winner/{winner_id2}")
    all_matches = client.get(f"/matches/tournament/{tid}").json()
    round2 = [m for m in all_matches if m["round"] == 2]
    assert len(round2) == 1
    assert round2[0]["player_a_id"] == winner_id
    assert round2[0]["player_b_id"] == winner_id2

def test_full_tournament_flow():
    t = client.post("/tournaments/", json={"name": "Final Test"})
    tid = t.json()["id"]
    p1 = client.post(f"/players/tournament/{tid}", json={"nickname": "Champion", "server": "S1"}).json()
    p2 = client.post(f"/players/tournament/{tid}", json={"nickname": "RunnerUp", "server": "S1"}).json()
    client.post(f"/tournaments/{tid}/start")
    matches = client.get(f"/matches/tournament/{tid}").json()
    client.post(f"/matches/{matches[0]['id']}/winner/{p1['id']}")
    tournament = client.get(f"/tournaments/{tid}").json()
    assert tournament["status"] == "finished"
