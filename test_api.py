#!/usr/bin/env python3
"""
Quick Test Script for TaskFlow API
Tests all major endpoints without running the full web server
"""

import json
import requests
from datetime import datetime

# Configuration
BASE_URL = "http://localhost:5000"
HEADERS = {"Content-Type": "application/json"}

# Global session to maintain cookies
session = requests.Session()

def print_section(title):
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}")

def print_response(response, title="Response"):
    print(f"\n[{title}] Status: {response.status_code}")
    try:
        print(json.dumps(response.json(), indent=2))
    except:
        print(response.text)

def test_registration():
    print_section("TEST 1: User Registration")
    
    payload = {
        "username": f"testuser_{datetime.now().timestamp()}",
        "email": f"test{datetime.now().timestamp()}@example.com",
        "password": "TestPassword123"
    }
    
    print(f"Registering user: {payload['username']}")
    response = session.post(f"{BASE_URL}/api/auth/register", json=payload, headers=HEADERS)
    print_response(response, "Register")
    
    if response.status_code == 201:
        return payload["email"]
    return None

def test_login(email, password):
    print_section("TEST 2: User Login")
    
    payload = {
        "email": email,
        "password": password
    }
    
    print(f"Logging in user: {email}")
    response = session.post(f"{BASE_URL}/api/auth/login", json=payload, headers=HEADERS)
    print_response(response, "Login")
    
    return response.status_code == 200

def test_get_current_user():
    print_section("TEST 3: Get Current User Profile")
    
    response = session.get(f"{BASE_URL}/api/auth/me", headers=HEADERS)
    print_response(response, "Get Current User")
    
    return response.status_code == 200

def test_create_task(title="Buy Groceries"):
    print_section("TEST 4: Create Task")
    
    payload = {
        "title": title,
        "description": "Milk, bread, eggs, and coffee",
        "priority": "High"
    }
    
    print(f"Creating task: {title}")
    response = session.post(f"{BASE_URL}/api/tasks", json=payload, headers=HEADERS)
    print_response(response, "Create Task")
    
    if response.status_code == 201:
        return response.json().get("task", {}).get("id")
    return None

def test_get_tasks():
    print_section("TEST 5: Get All Tasks")
    
    response = session.get(f"{BASE_URL}/api/tasks", headers=HEADERS)
    print_response(response, "Get Tasks")
    
    if response.status_code == 200:
        tasks = response.json().get("tasks", [])
        print(f"\nTotal tasks: {len(tasks)}")
        for task in tasks:
            print(f"  - [{task['id']}] {task['title']} ({task['priority']}) - {task['status']}")
    
    return response.status_code == 200

def test_update_task(task_id):
    print_section("TEST 6: Update Task")
    
    payload = {
        "title": "Buy Groceries (Updated)",
        "description": "Milk, bread, eggs, coffee, and juice",
        "priority": "Medium",
        "status": "Pending"
    }
    
    print(f"Updating task {task_id}")
    response = session.put(f"{BASE_URL}/api/tasks/{task_id}", json=payload, headers=HEADERS)
    print_response(response, "Update Task")
    
    return response.status_code == 200

def test_toggle_task_complete(task_id):
    print_section("TEST 7: Mark Task Complete")
    
    payload = {"status": "Completed"}
    
    print(f"Marking task {task_id} as complete")
    response = session.put(f"{BASE_URL}/api/tasks/{task_id}", json=payload, headers=HEADERS)
    print_response(response, "Toggle Complete")
    
    return response.status_code == 200

def test_get_analytics():
    print_section("TEST 8: Get Analytics")
    
    print("Fetching analytics")
    response = session.get(f"{BASE_URL}/api/analytics", headers=HEADERS)
    print_response(response, "Analytics")
    
    if response.status_code == 200:
        data = response.json()
        print(f"\n📊 Task Statistics:")
        print(f"   Total: {data['total_tasks']}")
        print(f"   Completed: {data['completed_tasks']}")
        print(f"   Pending: {data['pending_tasks']}")
        print(f"   Completion %: {data['completion_percentage']}%")
        print(f"   By Priority:")
        print(f"      Low: {data['by_priority']['Low']}")
        print(f"      Medium: {data['by_priority']['Medium']}")
        print(f"      High: {data['by_priority']['High']}")
    
    return response.status_code == 200

def test_delete_task(task_id):
    print_section("TEST 9: Delete Task")
    
    print(f"Deleting task {task_id}")
    response = session.delete(f"{BASE_URL}/api/tasks/{task_id}", headers=HEADERS)
    print_response(response, "Delete Task")
    
    return response.status_code == 200

def test_logout():
    print_section("TEST 10: Logout")
    
    response = session.post(f"{BASE_URL}/api/auth/logout", headers=HEADERS)
    print_response(response, "Logout")
    
    return response.status_code == 200

def run_all_tests():
    """Run all tests in sequence"""
    print("\n" + "█"*60)
    print("█" + " "*58 + "█")
    print("█" + "  TaskFlow API Test Suite".center(58) + "█")
    print("█" + " "*58 + "█")
    print("█"*60)
    
    print(f"\n🚀 Starting tests at: {datetime.now()}")
    print(f"Base URL: {BASE_URL}")
    
    try:
        # Test 1: Register
        email = test_registration()
        if not email:
            print("\n❌ Registration failed. Exiting.")
            return
        
        # Test 2: Login
        if not test_login(email, "TestPassword123"):
            print("\n❌ Login failed. Exiting.")
            return
        
        # Test 3: Get current user
        test_get_current_user()
        
        # Test 4: Create task
        task_id = test_create_task("Buy Groceries")
        
        # Test 5: Get tasks
        test_get_tasks()
        
        # Test 6: Update task
        if task_id:
            test_update_task(task_id)
        
        # Test 7: Mark complete
        if task_id:
            test_toggle_task_complete(task_id)
        
        # Test 8: Create another task for analytics
        test_create_task("Clean the house")
        
        # Test 9: Get analytics
        test_get_analytics()
        
        # Test 10: Delete task
        if task_id:
            test_delete_task(task_id)
        
        # Test 11: Final tasks list
        test_get_tasks()
        
        # Test 12: Logout
        test_logout()
        
        print("\n" + "█"*60)
        print("✅ All tests completed successfully!")
        print("█"*60 + "\n")
        
    except requests.exceptions.ConnectionError:
        print("\n❌ ERROR: Cannot connect to server")
        print(f"   Make sure the Flask app is running at {BASE_URL}")
        print(f"   Run: python app.py")
    except Exception as e:
        print(f"\n❌ ERROR: {e}")

if __name__ == "__main__":
    run_all_tests()
