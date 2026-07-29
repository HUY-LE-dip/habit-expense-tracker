from fastapi.testclient import TestClient

# This take "app" from main.py and allows us to test it
from main import app 

# This defined a client that we can use to send requests to our FastAPI app
client = TestClient(app)

# Test function to check the root endpoint
def test_read_root():
    # Send a GET request to the root endpoint
    response = client.get("/")  

    # Check that the response status code is 200 (OK)
    assert response.status_code == 200  

    # Check that the response JSON matches the expected output
    assert response.json() == {"status": "ok"}  

# Test function to check the habit creation endpoint
def test_create_habit():
    # Send a POST request to create a new habit
    response = client.post("/habits?name=Test Habit")

    # Check that the response status code is 200 (OK)
    assert response.status_code == 200  
    data = response.json()
    # Check that the response JSON contains the expected habit name
    assert response.json()["name"] == "Test Habit"

# Test function to check the expense creation endpoint
def test_create_expense():
    # Send a POST request to create a new expense
    response = client.post("/expenses?amount=10&category=Test Expense")

    # Check that the response status code is 200 (OK)
    assert response.status_code == 200  
    data = response.json()
    # Check that the response JSON contains the expected expense amount and description
    assert data["amount"] == 10
    assert data["category"] == "Test Expense"

def test_get_habit_streak():
    # Create a new habit first
    response = client.post("/habits?name=Streak Habit")
    assert response.status_code == 200
    habit_id = response.json()["id"]

    # Log the habit for today
    log_response = client.post(f"/habits/{habit_id}/log")
    assert log_response.status_code == 200

    # Fetch the habit streak
    streak_response = client.get(f"/habits/{habit_id}/streak")
    assert streak_response.status_code == 200
    streak_data = streak_response.json()

    # Check that the streak is at least 1 (since we just logged it)
    assert streak_data["streak"] >= 1
    