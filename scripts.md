# Thunder Client Test Scripts

Base URL:

- `http://127.0.0.1:5000`

If your API is running on a different port, replace `5000` in all requests.

## 1) Add grade for a new student

Request:

- Method: `POST`
- URL: `/students/S001/grades`
- Headers: `Content-Type: application/json`
- Body:

```json
{
  "student_name": "Alice Johnson",
  "grade": 88
}
```

Expected:

- Status: `201`
- Response includes:
  - `message: "Grade added"`
  - `student.student_id`
  - `student.student_name`
  - `student.grade`
  - `student.average`

## 2) Add another grade to same student

Request:

- Method: `POST`
- URL: `/students/S001/grades`
- Headers: `Content-Type: application/json`
- Body:

```json
{
  "student_name": "Alice Johnson",
  "grade": 94
}
```

Expected:

- Status: `201`
- `student.average` should update based on all grades.

## 3) Get all grades for a student

Request:

- Method: `GET`
- URL: `/students/S001/grades`

Expected:

- Status: `200`
- Response includes:
  - `student_id`
  - `student_name`
  - `average`
  - `grades` array with each grade entry (`id`, `grade`)

## 4) Update a student's grade (PUT)

Request:

- Method: `PUT`
- URL: `/students/S001/grades`
- Headers: `Content-Type: application/json`
- Body (updates the latest grade for that student):

```json
{
  "grade": 96
}
```

Optional body to target a specific grade record:

```json
{
  "grade_id": 2,
  "grade": 96
}
```

Expected:

- Status: `200`
- Response includes:
  - `message: "Grade updated"`
  - `student.student_id`
  - `student.student_name`
  - `student.grade`
  - `student.average`
  - `student.updated_grade_id`

## 5) Get average for a student

Request:

- Method: `GET`
- URL: `/students/S001/average`

Expected:

- Status: `200`
- Response includes:
  - `student_id`
  - `student_name`
  - `average`

## 6) Delete all grades for a student

Request:

- Method: `DELETE`
- URL: `/students/S001/grades`

Expected:

- Status: `200`
- Response includes:
  - `message: "Student grades deleted"`
  - `student.student_id`
  - `student.student_name`
  - `student.deleted_grades`

After this, `GET /students/S001/grades` should return `404` unless new grades are added again.

## 7) Get all students

Request:

- Method: `GET`
- URL: `/students`

Expected:

- Status: `200`
- Response includes `students` array.
- Each student object includes:
  - `student_id`
  - `student_name`
  - `average`

## 8) Validation test: missing student_name for a new student

Request:

- Method: `POST`
- URL: `/students/S999/grades`
- Headers: `Content-Type: application/json`
- Body:

```json
{
  "grade": 72
}
```

Expected:

- Status: `400`
- Message indicates missing `student_name`.

## 9) Validation test: mismatched name for existing student_id

First create student `S050`:

- `POST /students/S050/grades`

```json
{
  "student_name": "Brian Lee",
  "grade": 80
}
```

Then send a mismatched name:

- `POST /students/S050/grades`

```json
{
  "student_name": "Different Name",
  "grade": 85
}
```

Expected:

- Status: `400`
- Message indicates `student_name` does not match existing `student_id`.

## 10) Validation test: PUT with invalid grade_id

Request:

- Method: `PUT`
- URL: `/students/S001/grades`
- Headers: `Content-Type: application/json`
- Body:

```json
{
  "grade_id": "abc",
  "grade": 90
}
```

Expected:

- Status: `400`
- Message indicates `grade_id` must be an integer.

## 11) Verify homepage data table

Open in browser:

- `http://127.0.0.1:5000/`

Expected columns:

- Student ID
- Student Name
- Grade
- Average

The table should reflect new grades after refreshing the page.
