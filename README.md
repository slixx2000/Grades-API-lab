🎓 Student Grades API
A simple RESTful API built with Flask, Flask-RESTful, and Flask-SQLAlchemy for managing student grades.
📌 Features
Add grades for students
Retrieve all grades for a student
Calculate a student’s average grade
List all available students
Input validation and proper HTTP status codes
SQLite persistence
🛠 Tech Stack
Python 3
Flask
Flask-RESTful
Flask-SQLAlchemy
SQLite
OpenAPI 3.0 (Swagger)
🚀 Getting Started
1️⃣ Clone the Repository
Bash
Copy code
git clone https://github.com/your-username/student-grades-api.git
cd student-grades-api
2️⃣ Install Dependencies
Bash
Copy code
pip install flask flask-restful flask-sqlalchemy
3️⃣ Run the Server
Bash
Copy code
python app.py
Server runs at:
Copy code

http://127.0.0.1:5000
📄 OpenAPI Specification (YAML)
Yaml
Copy code
openapi: 3.0.3
info:
  title: Student Grades API
  version: 1.0.0
  description: REST API for managing student grades
servers:
  - url: http://localhost:5000

paths:
  /students:
    get:
      summary: Get all students
      responses:
        "200":
          description: List of students
        "404":
          description: No students found

  /students/{student_id}/grades:
    get:
      summary: Get grades for a student
      parameters:
        - name: student_id
          in: path
          required: true
          schema:
            type: string
      responses:
        "200":
          description: List of grades
        "404":
          description: Student not found

    post:
      summary: Add a grade for a student
      parameters:
        - name: student_id
          in: path
          required: true
          schema:
            type: string
      requestBody:
        required: true
        content:
          application/json:
            schema:
              type: object
              required:
                - grade
              properties:
                grade:
                  type: number
                  minimum: 0
                  maximum: 100
      responses:
        "201":
          description: Grade added successfully
        "400":
          description: Invalid input

  /students/{student_id}/average:
    get:
      summary: Get average grade for a student
      parameters:
        - name: student_id
          in: path
          required: true
          schema:
            type: string
      responses:
        "200":
          description: Average grade
        "404":
          description: No grades found
📚 API Endpoints Documentation
🔹 GET /students
Returns all available students.
Response (200)
Json
Copy code
{
  "students": ["123", "456"]
}
Error (404)
Json
Copy code
{
  "message": "No students found"
}
🔹 POST /students/{student_id}/grades
Adds a new grade for a student.
Request Body
Json
Copy code
{
  "grade": 85
}
Response (201)
Json
Copy code
{
  "message": "Grade added",
  "student_id": "123",
  "grade": 85.0
}
Validation Rules
grade must be a number
Range: 0 ≤ grade ≤ 100
🔹 GET /students/{student_id}/grades
Returns all grades for a student.
Response (200)
Json
Copy code
{
  "student_id": "123",
  "grades": [85.0, 90.0]
}
Error (404)
Json
Copy code
{
  "message": "Student not found"
}
🔹 GET /students/{student_id}/average
Returns the average grade for a student.
Response (200)
Json
Copy code
{
  "student_id": "123",
  "average": 87.5
}
Error (404)
Json
Copy code
{
  "message": "No grades found for student"
}
❗ Error Handling
Status Code
Meaning
200
Successful request
201
Resource created
400
Invalid input
404
Resource not found
500
Server error
🧪 Testing
The API can be tested using:
Thunder Client (VS Code)
Postman
curl
Example:
Bash
Copy code
curl -X POST http://127.0.0.1:5000/students/123/grades \
-H "Content-Type: application/json" \
-d '{"grade": 90}'
📦 Future Improvements
Add Student table (name, email, etc.)
JWT authentication
Pagination
Swagger UI at /docs
Docker support
📜 License
MIT License

HTTP Status Codes Summary
This API uses standard HTTP status codes to clearly communicate the result of each request.
Status Code
Name
Meaning in This API
200
OK
Request was successful and data was returned
201
Created
A new resource (grade) was successfully created
400
Bad Request
The request body is invalid (missing or incorrect data)
404
Not Found
The requested resource does not exist
500
Internal Server Error
An unexpected server-side error occurred
Notes
400 errors are returned for validation failures (e.g. grade out of range).
404 is returned when a student or grades cannot be found.
201 is only used when a grade is successfully added.
