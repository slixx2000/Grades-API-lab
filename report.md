# Technical Report: Student Grades RESTful API

**Module:** Web Application Development  
**Report Type:** Technical Analysis  
**Date:** March 2026  

---

## Abstract

This report presents a detailed technical analysis of a Student Grades RESTful API implemented using the Python Flask framework. The application exposes HTTP endpoints for managing student grade records and is formally described using an OpenAPI 3.0 specification. The report examines the application architecture, database design, API endpoint behaviour, input validation strategy, error handling, and the alignment between the implementation (`app.py`) and its formal specification (`openapi.yaml`). Strengths and areas for improvement are identified and discussed.

---

## Table of Contents

1. [Introduction](#1-introduction)  
2. [Technology Stack](#2-technology-stack)  
3. [Application Architecture](#3-application-architecture)  
4. [Database Design](#4-database-design)  
5. [API Implementation – `app.py`](#5-api-implementation--apppy)  
   - 5.1 [Input Validation](#51-input-validation)  
   - 5.2 [Resource: `StudentGrades`](#52-resource-studentgrades)  
   - 5.3 [Resource: `StudentAverage`](#53-resource-studentaverage)  
   - 5.4 [Resource: `Students`](#54-resource-students)  
   - 5.5 [Route Configuration and Home Page](#55-route-configuration-and-home-page)  
6. [API Specification – `openapi.yaml`](#6-api-specification--openapiyaml)  
   - 6.1 [Endpoint: `GET /students/{student_id}/grades`](#61-endpoint-get-studentsstudent_idgrades)  
   - 6.2 [Endpoint: `POST /students/{student_id}/grades`](#62-endpoint-post-studentsstudent_idgrades)  
   - 6.3 [Endpoint: `GET /students/{student_id}/average`](#63-endpoint-get-studentsstudent_idaverage)  
7. [Alignment Between Implementation and Specification](#7-alignment-between-implementation-and-specification)  
8. [Error Handling and HTTP Status Codes](#8-error-handling-and-http-status-codes)  
9. [Critical Evaluation](#9-critical-evaluation)  
   - 9.1 [Strengths](#91-strengths)  
   - 9.2 [Limitations and Areas for Improvement](#92-limitations-and-areas-for-improvement)  
10. [Conclusion](#10-conclusion)  
11. [References](#11-references)  

---

## 1. Introduction

RESTful APIs (Representational State Transfer Application Programming Interfaces) have become the de facto standard for building web services that are interoperable, stateless, and scalable (Fielding, 2000). This report analyses a Student Grades API — a lightweight web service designed to record and retrieve academic grade data for individual students.

The application is built with Python and the Flask micro-framework, persists data in an SQLite relational database via Flask-SQLAlchemy, and is formally described using an OpenAPI 3.0 YAML specification. The project demonstrates foundational concepts of RESTful design, including resource-oriented URL design, appropriate use of HTTP verbs, and standardised JSON response structures.

The objectives of this report are to:

- Describe the architecture and technology choices underpinning the application.
- Analyse the implementation in `app.py` in terms of structure, logic, and correctness.
- Examine the formal API contract defined in `openapi.yaml`.
- Evaluate the consistency between the implementation and the specification.
- Identify strengths, limitations, and potential improvements.

---

## 2. Technology Stack

| Component | Technology | Version / Notes |
|-----------|-----------|-----------------|
| Language | Python | 3.x |
| Web Framework | Flask | Latest stable |
| REST Extension | Flask-RESTful | Latest stable |
| ORM / Database | Flask-SQLAlchemy + SQLite | File-based (`grades.db`) |
| API Specification | OpenAPI 3.0.3 (YAML) | Machine-readable contract |
| Frontend | Jinja2 HTML Template | Single informational page |

**Flask** is a minimalist WSGI micro-framework that provides request routing, templating, and extension hooks without imposing a rigid project structure (Ronacher, 2010). **Flask-RESTful** builds on Flask to provide class-based resource definitions with automatic request dispatching. **Flask-SQLAlchemy** integrates the SQLAlchemy ORM, abstracting raw SQL into Python model classes. **SQLite** is used as the persistence layer, making the application self-contained and easy to run locally without an external database server.

---

## 3. Application Architecture

The application follows a single-file, layered architecture as illustrated below:

```
┌───────────────────────────────────────┐
│              HTTP Client              │
│     (browser / curl / Postman)        │
└───────────────────┬───────────────────┘
                    │ HTTP Request
┌───────────────────▼───────────────────┐
│           Flask + Flask-RESTful       │
│         (routing & dispatching)       │
├───────────────────────────────────────┤
│   Resource Classes (business logic)   │
│  StudentGrades │ StudentAverage       │
│  Students                             │
├───────────────────────────────────────┤
│      Flask-SQLAlchemy ORM Layer       │
├───────────────────────────────────────┤
│         SQLite Database (grades.db)   │
└───────────────────────────────────────┘
```

The application is entirely contained within `app.py`. All configuration, model definitions, helper functions, resource classes, and route registration reside in this single module. While this is acceptable for a small project or prototype, larger applications would typically separate these concerns across multiple modules or packages.

---

## 4. Database Design

The application uses a single database table, `grade`, mapped to the `Grade` SQLAlchemy model class:

```python
class Grade(db.Model):
    id         = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.String(50), nullable=False)
    grade      = db.Column(db.Float, nullable=False)
```

**Table: `grade`**

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | INTEGER | PRIMARY KEY, auto-increment | Unique record identifier |
| `student_id` | VARCHAR(50) | NOT NULL | Identifier for the student (string) |
| `grade` | FLOAT | NOT NULL | Numeric grade value (0–100) |

The schema is intentionally minimal. There is no dedicated `Student` table; a student is implicitly identified by their `student_id` string. This denormalised approach simplifies the data model but means that the same student identifier can be re-used without any uniqueness enforcement at the database level.

The `to_dict()` method serialises a `Grade` instance to a Python dictionary, facilitating JSON responses. The database tables are created automatically at application startup using `db.create_all()` within the Flask application context.

---

## 5. API Implementation – `app.py`

### 5.1 Input Validation

A shared helper function, `validate_grade`, is responsible for validating grade values before they are stored:

```python
def validate_grade(value):
    try:
        value = float(value)
    except (ValueError, TypeError):
        abort(400, message="Grade must be a number")

    if value < 0 or value > 100:
        abort(400, message="Grade must be between 0 and 100")

    return value
```

The function performs two checks:

1. **Type coercion:** The input is cast to `float`. If this fails (e.g., a non-numeric string is provided), a `400 Bad Request` response is returned immediately.
2. **Range validation:** The numeric value must be within the closed interval [0, 100]. Values outside this range also result in a `400` response.

This centralised validation promotes the DRY (Don't Repeat Yourself) principle and ensures consistent error messages across all endpoints that accept grade data.

### 5.2 Resource: `StudentGrades`

This resource class handles grade retrieval and creation for a specific student, mapped to the URL path `/students/<string:student_id>/grades`.

**GET `/students/{student_id}/grades`**

Queries the `Grade` table for all records matching the provided `student_id`. If no records are found, the endpoint aborts with a `404` error. On success, it returns a JSON object containing the `student_id` and a list of all grade values.

```python
def get(self, student_id):
    grades = Grade.query.filter_by(student_id=student_id).all()
    if not grades:
        abort(404, message="Student not found")
    return {"student_id": student_id, "grades": [g.grade for g in grades]}, 200
```

**POST `/students/{student_id}/grades`**

Parses the JSON request body, validates the presence and value of the `grade` field, creates a new `Grade` record, commits it to the database, and returns a `201 Created` response.

```python
def post(self, student_id):
    if not request.is_json:
        abort(400, message="Request body must be JSON")
    data = request.get_json()
    if "grade" not in data:
        abort(400, message="Missing 'grade' field")
    grade_value = validate_grade(data["grade"])
    grade = Grade(student_id=student_id, grade=grade_value)
    db.session.add(grade)
    db.session.commit()
    return {"message": "Grade added", "student_id": student_id, "grade": grade_value}, 201
```

Notably, the `POST` handler checks for a JSON `Content-Type` header before attempting to parse the body, preventing a potential `TypeError` if the request body is empty or malformed.

### 5.3 Resource: `StudentAverage`

Mapped to `/students/<string:student_id>/average`, this resource computes the arithmetic mean of all grades for a given student.

```python
def get(self, student_id):
    grades = Grade.query.filter_by(student_id=student_id).all()
    if not grades:
        abort(404, message="No grades found for student")
    average = sum(g.grade for g in grades) / len(grades)
    return {"student_id": student_id, "average": round(average, 2)}, 200
```

The average is rounded to two decimal places before being returned, which provides a clean numeric output suitable for display or further processing.

### 5.4 Resource: `Students`

Mapped to `/students`, this resource returns a distinct list of all student identifiers currently in the database.

```python
def get(self):
    results = db.session.query(Grade.student_id).distinct().all()
    if not results:
        abort(404, message="No students found")
    students = [row.student_id for row in results]
    return {"students": students}, 200
```

The use of `DISTINCT` in the SQL query avoids duplicate entries in the response, which would otherwise occur because each grade is stored as a separate row with the same `student_id`.

### 5.5 Route Configuration and Home Page

Routes are registered using Flask-RESTful's `api.add_resource` method:

```python
api.add_resource(Students,       "/students")
api.add_resource(StudentGrades,  "/students/<string:student_id>/grades")
api.add_resource(StudentAverage, "/students/<string:student_id>/average")
```

A standard Flask route serves an informational HTML landing page (`index.html`) at the application root (`/`), rendered via Jinja2 templating. This provides a human-readable overview of the available endpoints without requiring a dedicated API documentation tool.

---

## 6. API Specification – `openapi.yaml`

The `openapi.yaml` file provides a formal, machine-readable contract for the API, conforming to the OpenAPI Specification (OAS) version 3.0.3. Machine-readable API contracts enable automatic documentation generation, client SDK generation, and automated contract testing.

```yaml
openapi: 3.0.3
info:
  title: Student Grades API
  version: 1.0.0
  description: A simple REST API for managing student grades
servers:
  - url: http://localhost:5000
```

The document declares a single server at `http://localhost:5000`, matching the default Flask development server address.

### 6.1 Endpoint: `GET /students/{student_id}/grades`

Specifies a required path parameter `student_id` of type `string`. Defines two response codes:

- **200:** Returns a JSON object with `student_id` (string) and `grades` (array of numbers), fully described using an inline JSON Schema.
- **404:** Returned when the student is not found (response body schema not specified).

### 6.2 Endpoint: `POST /students/{student_id}/grades`

Requires `student_id` as a path parameter. The request body is declared as required with `Content-Type: application/json`. The body schema enforces:

- A required `grade` field of type `number`.
- A `minimum` of `0` and `maximum` of `100`, mirroring the server-side validation in `validate_grade`.

Response codes defined:

- **201:** Grade added successfully.
- **400:** Invalid input (no response body schema provided).

### 6.3 Endpoint: `GET /students/{student_id}/average`

Specifies the same `student_id` path parameter. Defines two response codes:

- **200:** Returns a JSON object with `student_id` (string) and `average` (number).
- **404:** Returned when the student or grades are not found.

---

## 7. Alignment Between Implementation and Specification

A comparison of the implemented routes in `app.py` and the paths defined in `openapi.yaml` reveals the following:

| Endpoint | Implemented in `app.py` | Documented in `openapi.yaml` |
|----------|------------------------|------------------------------|
| `GET /students` | ✅ Yes | ❌ No |
| `GET /students/{student_id}/grades` | ✅ Yes | ✅ Yes |
| `POST /students/{student_id}/grades` | ✅ Yes | ✅ Yes |
| `GET /students/{student_id}/average` | ✅ Yes | ✅ Yes |
| `GET /` (home page) | ✅ Yes | ❌ No |

The most significant discrepancy is that the `GET /students` endpoint — which returns a list of all students — is fully implemented in `app.py` (via the `Students` resource class) but is absent from `openapi.yaml`. This means any consumer relying solely on the specification would be unaware of this endpoint. The home page route (`/`) is appropriately omitted from the spec, as it serves HTML rather than a JSON API resource.

For all three documented endpoints, the HTTP methods, path parameters, request body schemas, and response schemas in the YAML file correctly reflect the behaviour of the corresponding Python code.

---

## 8. Error Handling and HTTP Status Codes

The application uses Flask-RESTful's `abort` function to return structured JSON error responses. The following status codes are used:

| HTTP Status Code | Meaning | When Used |
|-----------------|---------|-----------|
| 200 OK | Successful retrieval | GET endpoints returning data |
| 201 Created | Resource created | POST `/grades` after successful insertion |
| 400 Bad Request | Invalid input | Non-JSON body, missing `grade` field, invalid grade value |
| 404 Not Found | Resource absent | No grades found for a student; no students in database |

Flask-RESTful's `abort` automatically serialises the `message` keyword argument into a JSON response body (e.g., `{"message": "Student not found"}`), ensuring consistent error payloads throughout the API.

A notable absence is explicit handling of `500 Internal Server Error`. Unhandled exceptions (e.g., a database connection failure) would result in a Flask default error response rather than a custom JSON error, which could expose internal stack traces in a development environment.

---

## 9. Critical Evaluation

### 9.1 Strengths

- **Clarity and Readability:** The code is well-structured and readable, with logical separation between the database model, validation helpers, resource classes, and route configuration. Inline comments mark each section clearly.
- **Centralised Validation:** The `validate_grade` helper function avoids duplication and ensures consistent validation behaviour. This is a sound application of the DRY principle.
- **Appropriate HTTP Semantics:** The application correctly uses `POST` to create resources and `GET` to retrieve them. The response code `201` is correctly used for creation, and `404` is correctly used when a resource is not found.
- **OpenAPI Documentation:** The inclusion of an `openapi.yaml` specification demonstrates awareness of API contract design and industry standards, enabling future integration with tooling such as Swagger UI, Redoc, or client code generators.
- **Input Safety:** The `POST` handler validates the `Content-Type` header before attempting to parse the body, preventing runtime errors from malformed requests.

### 9.2 Limitations and Areas for Improvement

1. **Incomplete OpenAPI Specification:** The `GET /students` endpoint is implemented but not documented in `openapi.yaml`. The specification should be updated to include this endpoint for completeness and to maintain an accurate API contract.

2. **No Authentication or Authorisation:** The API is fully open; any client can read or write any student's grades. For a production system, authentication (e.g., JWT tokens or API keys) and role-based authorisation would be essential.

3. **No Student Entity:** The data model lacks a dedicated `Student` table. Student identifiers are stored as plain strings without referential integrity constraints. This means it is possible to add grades for students that do not formally exist in the system, and there is no way to store additional student metadata (e.g., name, email).

4. **Limited Error Response Schemas:** The `openapi.yaml` specification does not define response body schemas for `400` and `404` error responses, reducing the utility of the specification for client developers who need to handle error cases programmatically.

5. **No Pagination:** The `GET /students/{student_id}/grades` endpoint returns all grades for a student in a single response. For students with large numbers of grade records, this could lead to performance issues. Pagination (e.g., via `limit` and `offset` query parameters) would address this.

6. **Development-Only Server Configuration:** The application is started with `debug=True`, which is appropriate for development but must not be used in production, as it exposes a debugger that can execute arbitrary code. A production deployment would require a WSGI server such as Gunicorn or uWSGI.

7. **No Unit or Integration Tests:** The repository contains no automated tests. A robust test suite using `pytest` and Flask's test client would improve reliability and facilitate safe refactoring.

8. **Grade Update and Deletion:** The API provides no mechanism to update or delete an existing grade record. A complete CRUD (Create, Read, Update, Delete) interface would require additional `PUT`/`PATCH` and `DELETE` endpoints.

---

## 10. Conclusion

The Student Grades API is a functional and well-structured RESTful web service that successfully demonstrates core concepts of API development with Flask, including resource-oriented design, ORM-backed persistence, input validation, and formal API specification. The implementation is clean and readable, and the choice of technology stack is appropriate for the scale and purpose of the project.

The principal areas for improvement relate to completeness (the missing `GET /students` endpoint in `openapi.yaml`), security (absence of authentication), and extensibility (no student entity, no pagination, incomplete CRUD). Addressing these concerns would be necessary before deploying the application in any production or multi-user environment.

Overall, the project provides a solid foundation that demonstrates a good understanding of RESTful principles and modern API development practices, while offering clear opportunities for further development.

---

## 11. References

- Fielding, R. T. (2000). *Architectural Styles and the Design of Network-based Software Architectures*. Doctoral dissertation, University of California, Irvine. Available at: https://www.ics.uci.edu/~fielding/pubs/dissertation/top.htm

- Flask Documentation (2024). *Flask – Web Development, one drop at a time*. Pallets Projects. Available at: https://flask.palletsprojects.com/

- Flask-RESTful Documentation (2024). *Flask-RESTful*. Available at: https://flask-restful.readthedocs.io/

- Flask-SQLAlchemy Documentation (2024). *Flask-SQLAlchemy*. Available at: https://flask-sqlalchemy.palletsprojects.com/

- OpenAPI Initiative (2021). *OpenAPI Specification v3.0.3*. Available at: https://spec.openapis.org/oas/v3.0.3

- Ronacher, A. (2010). *Introducing Flask*. Pallets Projects Blog. Available at: https://flask.palletsprojects.com/

- SQLAlchemy Documentation (2024). *SQLAlchemy – The Database Toolkit for Python*. Available at: https://docs.sqlalchemy.org/

---

*Word count (approximate): 1,800 words*
