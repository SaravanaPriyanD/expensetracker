import uuid

import pytest

from app import app as flask_app
from database.db import create_user
from database.queries import (
    get_category_breakdown,
    get_recent_transactions,
    get_summary_stats,
    get_user_by_id,
)


@pytest.fixture
def client():
    flask_app.config["TESTING"] = True
    flask_app.config["SECRET_KEY"] = "test-secret"
    with flask_app.test_client() as c:
        yield c


@pytest.fixture
def auth_client(client):
    with client.session_transaction() as sess:
        sess["user_id"] = 1
    return client


# ------------------------------------------------------------------ #
# SA2: get_user_by_id tests                                           #
# ------------------------------------------------------------------ #

def test_get_user_by_id_valid():
    result = get_user_by_id(1)
    assert result is not None
    assert result["name"] == "Demo User"
    assert result["email"] == "demo@spendly.com"
    parts = result["member_since"].split(" ")
    assert len(parts) == 2
    assert len(parts[1]) == 4 and parts[1].isdigit()


def test_get_user_by_id_invalid():
    result = get_user_by_id(99999)
    assert result is None


# ------------------------------------------------------------------ #
# SA2: get_summary_stats tests                                        #
# ------------------------------------------------------------------ #

def test_get_summary_stats_with_expenses():
    result = get_summary_stats(1)
    assert result["total_spent"] == pytest.approx(841.24)
    assert result["transaction_count"] == 8
    assert result["top_category"] == "Bills"


def test_get_summary_stats_no_expenses():
    new_user_id = create_user("SA2Test", f"sa2test-{uuid.uuid4().hex}@test.com", "pass")
    result = get_summary_stats(new_user_id)
    assert result == {"total_spent": 0, "transaction_count": 0, "top_category": "—"}


# ------------------------------------------------------------------ #
# SA1: get_recent_transactions tests                                  #
# ------------------------------------------------------------------ #

def test_get_recent_transactions_with_expenses():
    result = get_recent_transactions(1)
    assert isinstance(result, list)
    assert len(result) == 8
    assert result[0]["date"] >= result[-1]["date"]
    for item in result:
        assert set(["date", "description", "category", "amount"]).issubset(item.keys())


def test_get_recent_transactions_no_expenses():
    new_user_id = create_user("Test", f"sa1test-{uuid.uuid4().hex}@test.com", "pass")
    result = get_recent_transactions(new_user_id)
    assert result == []


# ------------------------------------------------------------------ #
# SA3: get_category_breakdown tests                                   #
# ------------------------------------------------------------------ #

def test_get_category_breakdown_with_expenses():
    result = get_category_breakdown(1)
    assert len(result) == 7
    assert result[0]["name"] == "Bills"
    assert result[0]["amount"] == pytest.approx(340.0)
    assert all(isinstance(c["pct"], int) for c in result)
    assert sum(c["pct"] for c in result) == 100
    assert result[0]["amount"] >= result[1]["amount"]


def test_get_category_breakdown_no_expenses():
    new_user_id = create_user("SA3Test", f"sa3test-{uuid.uuid4().hex}@test.com", "pass")
    result = get_category_breakdown(new_user_id)
    assert result == []


# ------------------------------------------------------------------ #
# Route tests (added by main agent after subagents complete)          #
# ------------------------------------------------------------------ #

def test_profile_unauthenticated(client):
    response = client.get("/profile")
    assert response.status_code == 302
    assert "/login" in response.headers["Location"]


def test_profile_authenticated(auth_client):
    response = auth_client.get("/profile")
    body = response.data.decode("utf-8")
    assert response.status_code == 200
    assert "Demo User" in body
    assert "demo@spendly.com" in body
    assert "₹" in body
    assert "841.24" in body
    assert "Bills" in body
