"""
Tests for the Mergington High School Activities API
"""
import pytest
from fastapi.testclient import TestClient


class TestActivitiesAPI:
    """Test class for activities API endpoints"""
    
    def test_root_redirect(self, client: TestClient):
        """Test that root endpoint redirects to static/index.html"""
        response = client.get("/", follow_redirects=False)
        assert response.status_code == 307
        assert response.headers["location"] == "/static/index.html"
    
    def test_get_activities(self, client: TestClient, reset_activities):
        """Test getting all activities"""
        response = client.get("/activities")
        assert response.status_code == 200
        
        activities = response.json()
        assert isinstance(activities, dict)
        assert len(activities) > 0
        
        # Check specific activity exists
        assert "Chess Club" in activities
        assert "Programming Class" in activities
        
        # Check activity structure
        chess_club = activities["Chess Club"]
        assert "description" in chess_club
        assert "schedule" in chess_club
        assert "max_participants" in chess_club
        assert "participants" in chess_club
        
        # Check data types
        assert isinstance(chess_club["max_participants"], int)
        assert isinstance(chess_club["participants"], list)
    
    def test_signup_for_activity_success(self, client: TestClient, reset_activities):
        """Test successful signup for an activity"""
        email = "newstudent@mergington.edu"
        activity = "Chess Club"
        
        # Get initial participant count
        response = client.get("/activities")
        initial_count = len(response.json()[activity]["participants"])
        
        # Sign up for activity
        response = client.post(f"/activities/{activity}/signup?email={email}")
        assert response.status_code == 200
        
        result = response.json()
        assert "message" in result
        assert email in result["message"]
        assert activity in result["message"]
        
        # Verify participant was added
        response = client.get("/activities")
        activities = response.json()
        participants = activities[activity]["participants"]
        assert email in participants
        assert len(participants) == initial_count + 1
    
    def test_signup_for_nonexistent_activity(self, client: TestClient, reset_activities):
        """Test signup for a nonexistent activity"""
        response = client.post("/activities/Nonexistent Activity/signup?email=test@mergington.edu")
        assert response.status_code == 404
        
        result = response.json()
        assert result["detail"] == "Activity not found"
    
    def test_signup_duplicate_participant(self, client: TestClient, reset_activities):
        """Test signup when student is already registered"""
        email = "michael@mergington.edu"  # Already in Chess Club
        activity = "Chess Club"
        
        response = client.post(f"/activities/{activity}/signup?email={email}")
        assert response.status_code == 400
        
        result = response.json()
        assert result["detail"] == "Student is already signed up"
    
    def test_signup_activity_full(self, client: TestClient, reset_activities):
        """Test signup when activity is at capacity"""
        activity = "Math Olympiad"  # Has max_participants = 10
        
        # Fill up the activity to capacity
        response = client.get("/activities")
        current_participants = len(response.json()[activity]["participants"])
        max_participants = response.json()[activity]["max_participants"]
        
        # Add participants until full
        for i in range(max_participants - current_participants):
            email = f"student{i}@mergington.edu"
            response = client.post(f"/activities/{activity}/signup?email={email}")
            assert response.status_code == 200
        
        # Try to add one more (should fail)
        response = client.post(f"/activities/{activity}/signup?email=overflow@mergington.edu")
        assert response.status_code == 400
        
        result = response.json()
        assert result["detail"] == "Activity is full"
    
    def test_unregister_from_activity_success(self, client: TestClient, reset_activities):
        """Test successful unregistration from an activity"""
        email = "michael@mergington.edu"  # Already in Chess Club
        activity = "Chess Club"
        
        # Get initial participant count
        response = client.get("/activities")
        initial_count = len(response.json()[activity]["participants"])
        
        # Unregister from activity
        response = client.delete(f"/activities/{activity}/unregister?email={email}")
        assert response.status_code == 200
        
        result = response.json()
        assert "message" in result
        assert email in result["message"]
        assert activity in result["message"]
        assert "Unregistered" in result["message"]
        
        # Verify participant was removed
        response = client.get("/activities")
        activities = response.json()
        participants = activities[activity]["participants"]
        assert email not in participants
        assert len(participants) == initial_count - 1
    
    def test_unregister_from_nonexistent_activity(self, client: TestClient, reset_activities):
        """Test unregister from a nonexistent activity"""
        response = client.delete("/activities/Nonexistent Activity/unregister?email=test@mergington.edu")
        assert response.status_code == 404
        
        result = response.json()
        assert result["detail"] == "Activity not found"
    
    def test_unregister_non_participant(self, client: TestClient, reset_activities):
        """Test unregister when student is not registered"""
        email = "notregistered@mergington.edu"
        activity = "Chess Club"
        
        response = client.delete(f"/activities/{activity}/unregister?email={email}")
        assert response.status_code == 400
        
        result = response.json()
        assert result["detail"] == "Student is not signed up for this activity"
    
    def test_url_encoding_in_activity_names(self, client: TestClient, reset_activities):
        """Test that activity names with spaces are properly handled"""
        email = "urltest@mergington.edu"
        activity = "Programming Class"  # Has space in name
        
        # Test signup with URL encoding
        encoded_activity = "Programming%20Class"
        response = client.post(f"/activities/{encoded_activity}/signup?email={email}")
        assert response.status_code == 200
        
        # Verify participant was added
        response = client.get("/activities")
        participants = response.json()[activity]["participants"]
        assert email in participants
        
        # Test unregister with URL encoding
        response = client.delete(f"/activities/{encoded_activity}/unregister?email={email}")
        assert response.status_code == 200
        
        # Verify participant was removed
        response = client.get("/activities")
        participants = response.json()[activity]["participants"]
        assert email not in participants
    
    def test_email_validation_in_urls(self, client: TestClient, reset_activities):
        """Test that emails with special characters are properly handled"""
        email = "test.user+tag@mergington.edu"
        activity = "Chess Club"
        
        # Test signup with special email
        response = client.post(f"/activities/{activity}/signup", params={"email": email})
        assert response.status_code == 200
        
        # Verify participant was added
        response = client.get("/activities")
        participants = response.json()[activity]["participants"]
        assert email in participants


class TestDataIntegrity:
    """Test class for data integrity and edge cases"""
    
    def test_activities_persistence_across_requests(self, client: TestClient, reset_activities):
        """Test that activity data persists across multiple requests"""
        email = "persistence@mergington.edu"
        activity = "Drama Club"
        
        # Sign up
        response = client.post(f"/activities/{activity}/signup?email={email}")
        assert response.status_code == 200
        
        # Verify in separate request
        response = client.get("/activities")
        participants = response.json()[activity]["participants"]
        assert email in participants
        
        # Unregister
        response = client.delete(f"/activities/{activity}/unregister?email={email}")
        assert response.status_code == 200
        
        # Verify removal in separate request
        response = client.get("/activities")
        participants = response.json()[activity]["participants"]
        assert email not in participants
    
    def test_multiple_activities_signup(self, client: TestClient, reset_activities):
        """Test that a student can sign up for multiple activities"""
        email = "multisport@mergington.edu"
        activities_to_join = ["Chess Club", "Swimming Club", "Art Workshop"]
        
        for activity in activities_to_join:
            response = client.post(f"/activities/{activity}/signup?email={email}")
            assert response.status_code == 200
        
        # Verify student is in all activities
        response = client.get("/activities")
        all_activities = response.json()
        
        for activity in activities_to_join:
            assert email in all_activities[activity]["participants"]
    
    def test_activity_capacity_limits(self, client: TestClient, reset_activities):
        """Test that activity capacity limits are enforced correctly"""
        response = client.get("/activities")
        activities_data = response.json()
        
        for activity_name, activity_info in activities_data.items():
            max_participants = activity_info["max_participants"]
            current_participants = len(activity_info["participants"])
            available_spots = max_participants - current_participants
            
            # Verify we can add up to the limit
            for i in range(available_spots):
                email = f"capacity_test_{i}@mergington.edu"
                response = client.post(f"/activities/{activity_name}/signup?email={email}")
                assert response.status_code == 200
            
            # Verify we can't exceed the limit
            overflow_email = f"overflow_{activity_name}@mergington.edu"
            response = client.post(f"/activities/{activity_name}/signup?email={overflow_email}")
            assert response.status_code == 400
            assert "Activity is full" in response.json()["detail"]
            
            break  # Test just one activity to avoid too many operations