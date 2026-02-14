import requests
import json

# Base URL
BASE_URL = "http://localhost:5000"

def test_create_student():
    """Test creating a new student via POST"""
    url = f"{BASE_URL}/course/student"
    
    # Test data
    student_data = {
        "studentName": "Test Student",
        "studentID": "S99999",
        "score": 88.5,
        "grade": "B+"
    }
    
    print("Testing POST /course/student")
    print(f"Sending data: {json.dumps(student_data, indent=2)}")
    
    try:
        response = requests.post(url, json=student_data)
        
        print(f"\nStatus Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        
        if response.status_code == 201:
            print("\n✓ Student created successfully!")
        else:
            print("\n✗ Failed to create student")
            
    except requests.exceptions.ConnectionError:
        print("\n✗ Error: Could not connect to the API. Make sure the server is running!")
    except Exception as e:
        print(f"\n✗ Error: {str(e)}")

def test_get_all_students():
    """Test getting all students"""
    url = f"{BASE_URL}/course/students"
    
    print("\n" + "="*50)
    print("Testing GET /course/students")
    
    try:
        response = requests.get(url)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
    except Exception as e:
        print(f"✗ Error: {str(e)}")

def test_multiple_students():
    """Test creating multiple students"""
    students = [
        {"studentName": "Emma Wilson", "studentID": "S10001", "score": 95.0, "grade": "A"},
        {"studentName": "Michael Brown", "studentID": "S10002", "score": 82.5, "grade": "B"},
        {"studentName": "Sophia Davis", "studentID": "S10003", "score": 91.0, "grade": "A-"},
    ]
    
    print("\n" + "="*50)
    print("Testing Multiple Student Creation")
    
    for student in students:
        print(f"\nCreating: {student['studentName']}")
        try:
            response = requests.post(f"{BASE_URL}/course/student", json=student)
            if response.status_code == 201:
                print(f"  ✓ Created successfully (ID: {response.json()['id']})")
            else:
                print(f"  ✗ Failed: {response.json()}")
        except Exception as e:
            print(f"  ✗ Error: {str(e)}")

if __name__ == "__main__":
    print("="*50)
    print("STUDENT GRADES API - POST ENDPOINT TESTS")
    print("="*50)
    
    # Run tests
    test_create_student()
    test_get_all_students()
    test_multiple_students()
    
    print("\n" + "="*50)
    print("Tests completed!")
    print("="*50)
