# Student Grades API

A Flask-based REST API for managing student grades and information.

## Overview

This API allows you to:
- Create and manage student records
- Store student information (name, ID, score, grade)
- Update student scores
- Retrieve individual or all student records

## Errors Fixed

### 1. **Critical Error on Line 70 - Non-existent `grade()` Function**
**Original Code:**
```python
new_grade = grade(
    student.studentID = args['studentID'],
    student.score = args['score']
)
```

**Issues:**
- Attempted to call a non-existent `grade()` function
- Invalid syntax using `=` instead of proper assignment within function parameters
- Logic error: trying to create a new object instead of updating existing student

**Fix:**
```python
student.score = args['score']
db.session.commit()
return student, 200
```
- Changed to properly update the existing student's score
- Removed the invalid function call
- Used correct SQLAlchemy update pattern

---

### 2. **Line 19 - Missing `self.` Prefix in `__repr__` Method**
**Original Code:**
```python
def __repr__(self):
    return f"Student(Name={studentName}, studentID={studentID},score={score}, grade={grade})"
```

**Issue:**
- Variables referenced without `self.` prefix would cause `NameError`

**Fix:**
```python
def __repr__(self):
    return f"Student(Name={self.studentName}, studentID={self.studentID}, score={self.score}, grade={self.grade})"
```

---

### 3. **Lines 45 & 56 - Incorrect Decorator Name `@marshalWith`**
**Original Code:**
```python
@marshalWith(userFields)
```

**Issue:**
- Flask-RESTful uses `@marshal_with` (lowercase 'w'), not `@marshalWith`

**Fix:**
```python
@marshal_with(userFields)
```

---

### 4. **Line 56 - Duplicate `post()` Method**
**Original Code:**
```python
class Student(Resource):
    def post(self):
        # Create student
        ...
    
    def post(self, student_id):  # Duplicate method name!
        # Update student score
        ...
```

**Issue:**
- Two methods with the same name (`post`) in the same class
- The second method would override the first
- Incorrect HTTP method for updating resources

**Fix:**
```python
class Student(Resource):
    def post(self):
        # Create student
        ...
    
    def put(self, student_id):  # Changed to PUT method
        # Update student score
        ...
```
- Changed second method to `put()` following REST conventions
- PUT is the correct HTTP method for updating existing resources

---

### 5. **Line 38 - Missing `score` Field in `userFields`**
**Original Code:**
```python
userFields = {
    'id':fields.Integer,
    'studentName':fields.String,
    'studentID':fields.String,
    'grade':fields.String
}
```

**Issue:**
- `score` field was missing from serialization fields
- Would cause score data to not be returned in API responses

**Fix:**
```python
userFields = {
    'id':fields.Integer,
    'studentName':fields.String,
    'studentID':fields.String,
    'score':fields.Float,  # Added score field
    'grade':fields.String
}
```

---

### 6. **Missing API Resource Route**
**Issue:**
- The `Student` class was defined but not registered with the API

**Fix:**
```python
api.add_resource(Student, '/course/student', '/course/student/<int:student_id>')
```
- Added route registration after class definition
- Supports both POST (without ID) and GET/PUT (with ID)

---

### 7. **Line 55 - Missing `score` Parameter in Student Creation**
**Original Code:**
```python
student = StudentModel(studentName=args['studentName'], studentID=args['studentID'], grade=args['grade'])
```

**Issue:**
- `score` parameter was missing when creating new student
- Would cause database error since `score` is a required field

**Fix:**
```python
student = StudentModel(studentName=args['studentName'], studentID=args['studentID'], score=args['score'], grade=args['grade'])
```

---

## API Endpoints

### 1. Get All Students
```
GET /course/students
```
Returns a list of all students in the database.

### 2. Create New Student
```
POST /course/student
Content-Type: application/json

{
    "studentName": "John Doe",
    "studentID": "S12345",
    "score": 85.5,
    "grade": "A"
}
```

### 3. Get Single Student
```
GET /course/student/<student_id>
```
Returns details of a specific student by their database ID.

### 4. Update Student Score
```
PUT /course/student/<student_id>
Content-Type: application/json

{
    "studentID": "S12345",
    "score": 92.0
}
```
Updates the score for a specific student. Score must be between 0 and 100.

### 5. Home Page
```
GET /
```
Returns a welcome message.

---

## Setup Instructions

### Prerequisites
- Python 3.x
- pip

### Installation

1. Install required packages:
```bash
pip install -r requirements.txt
```

2. Create the database:
```bash
python create_db.py
```

3. Run the application:
```bash
python api.py
```

The API will be available at `http://localhost:5000`

---

## Database Schema

**StudentModel**
- `id` (Integer, Primary Key)
- `studentName` (String, Required, Unique)
- `studentID` (String, Required, Unique)
- `score` (Float, Required)
- `grade` (String, Required)

---

## Error Handling

The API includes validation for:
- **404 Not Found**: When a student ID doesn't exist
- **400 Bad Request**: When score is outside the valid range (0-100)
- **Required Fields**: All fields are validated on creation

---

## Technologies Used

- **Flask**: Web framework
- **Flask-SQLAlchemy**: ORM for database operations
- **Flask-RESTful**: REST API framework
- **SQLite**: Database

---

## Notes

- The API runs in debug mode by default
- Database file is stored in `instance/studentgrades.db`
- All student names and IDs must be unique
