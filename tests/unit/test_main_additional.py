
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient

from main import app


client = TestClient(app)


def test_health_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}


@pytest.mark.parametrize(
    "endpoint,a,b,expected",
    [
        ("/add", 10, 5, 15),
        ("/subtract", 10, 5, 5),
        ("/multiply", 10, 5, 50),
        ("/divide", 10, 5, 2),
    ],
)
def test_calculator_success(endpoint, a, b, expected):
    response = client.post(endpoint, json={"a": a, "b": b})
    assert response.status_code == 200
    assert response.json()["result"] == expected


@pytest.mark.parametrize(
    "endpoint,function_name",
    [
        ("/add", "add"),
        ("/subtract", "subtract"),
        ("/multiply", "multiply"),
    ],
)
def test_calculator_unexpected_errors(endpoint, function_name):
    with patch(
        f"main.{function_name}",
        side_effect=RuntimeError("Simulated operation failure"),
    ):
        response = client.post(endpoint, json={"a": 10, "b": 5})

    assert response.status_code == 400
    assert response.json() == {
        "error": "Simulated operation failure"
    }


def test_division_by_zero():
    response = client.post(
        "/divide",
        json={"a": 10, "b": 0},
    )
    assert response.status_code == 400
    assert "error" in response.json()


def test_division_unexpected_error():
    with patch(
        "main.divide",
        side_effect=RuntimeError("Simulated internal failure"),
    ):
        response = client.post(
            "/divide",
            json={"a": 10, "b": 2},
        )

    assert response.status_code == 500
    assert response.json() == {
        "error": "Internal Server Error"
    }


@pytest.mark.parametrize(
    "endpoint",
    ["/add", "/subtract", "/multiply", "/divide"],
)
def test_invalid_input(endpoint):
    response = client.post(
        endpoint,
        json={"a": "invalid", "b": 5},
    )

    assert response.status_code == 400
    assert "error" in response.json()


def test_missing_input():
    response = client.post(
        "/add",
        json={"a": 10},
    )

    assert response.status_code == 400
    assert "error" in response.json()
