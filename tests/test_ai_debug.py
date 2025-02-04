import pytest
from fastapi.testclient import TestClient
from app.main import app
import redis
import json

# Test Client for FastAPI
client = TestClient(app)

# Redis Client
redis_client = redis.StrictRedis(host="localhost", port=6379, db=0, decode_responses=True)

@pytest.fixture(scope="function", autouse=True)
def clear_redis_cache():
    """ Clear Redis cache before each test """
    redis_client.flushdb()

def test_ai_debug_cache():
    code = "def hello(): pass"  # Sample code to test
    # Check if the response is not cached initially
    cached_result = redis_client.get(code)
    assert cached_result is None

    # First request, should not be cached
    response = client.post("/ai-debug/", json={"code": code})
    assert response.status_code == 200
    assert "suggestion" in response.json()

    # Check if the response is cached after the first request
    cached_result = redis_client.get(code)
    assert cached_result is not None
    cached_data = cached_result
    assert "suggestion" in cached_data

    # Second request, should return cached response
    response = client.post("/ai-debug/", json={"code": code})
    assert response.status_code == 200
    assert response.json() == json.loads(cached_data)
