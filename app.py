from flask import Flask, request, render_template
from flask_restful import Resource, Api, abort
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import inspect, text

app = Flask(__name__)
api = Api(app)

# Database configuration (SQLite)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///grades.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)


# Database Model

class Grade(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.String(50), nullable=False)
    student_name = db.Column(db.String(100), nullable=True)
    grade = db.Column(db.Float, nullable=False)

    def to_dict(self):
        return {
            "id": self.id,
            "student_id": self.student_id,
            "student_name": self.student_name,
            "grade": self.grade
        }


# Create tables
with app.app_context():
    db.create_all()
    inspector = inspect(db.engine)
    grade_columns = {column["name"] for column in inspector.get_columns("grade")}

    if "student_name" not in grade_columns:
        db.session.execute(text("ALTER TABLE grade ADD COLUMN student_name VARCHAR(100)"))
        db.session.execute(text("UPDATE grade SET student_name = student_id WHERE student_name IS NULL"))
        db.session.commit()


# -------------------
# Helpers
# -------------------
def validate_grade(value):
    try:
        value = float(value)
    except (ValueError, TypeError):
        abort(400, message="Grade must be a number")

    if value < 0 or value > 100:
        abort(400, message="Grade must be between 0 and 100")

    return value


def build_student_summary(student_id, grades):
    if not grades:
        abort(404, message="Student not found")

    average = round(sum(g.grade for g in grades) / len(grades), 2)
    student_name = grades[0].student_name or student_id

    return {
        "student_id": student_id,
        "student_name": student_name,
        "average": average,
        "grades": [
            {
                "id": g.id,
                "grade": g.grade,
            }
            for g in grades
        ],
    }


# -------------------
# Resources
# -------------------
class StudentGrades(Resource):
    def get(self, student_id):
        grades = Grade.query.filter_by(student_id=student_id).order_by(Grade.id.asc()).all()
        return build_student_summary(student_id, grades), 200

    def post(self, student_id):
        if not request.is_json:
            abort(400, message="Request body must be JSON")

        data = request.get_json()

        if "grade" not in data:
            abort(400, message="Missing 'grade' field")

        grade_value = validate_grade(data["grade"])
        student_name = data.get("student_name")
        existing = Grade.query.filter_by(student_id=student_id).first()

        if existing:
            if not student_name:
                student_name = existing.student_name
            elif existing.student_name and student_name.strip() != existing.student_name:
                abort(400, message="student_name does not match the existing student_id")
        elif not student_name or not str(student_name).strip():
            abort(400, message="Missing 'student_name' field")

        student_name = str(student_name).strip()

        grade = Grade(student_id=student_id, student_name=student_name, grade=grade_value)
        db.session.add(grade)
        db.session.commit()

        grades = Grade.query.filter_by(student_id=student_id).order_by(Grade.id.asc()).all()
        summary = build_student_summary(student_id, grades)

        return {
            "message": "Grade added",
            "student": {
                "student_id": summary["student_id"],
                "student_name": summary["student_name"],
                "grade": grade_value,
                "average": summary["average"],
            }
        }, 201

    def put(self, student_id):
        if not request.is_json:
            abort(400, message="Request body must be JSON")

        data = request.get_json()

        if "grade" not in data:
            abort(400, message="Missing 'grade' field")

        grade_value = validate_grade(data["grade"])
        grades = Grade.query.filter_by(student_id=student_id).order_by(Grade.id.asc()).all()

        if not grades:
            abort(404, message="Student not found")

        target_grade = None
        target_grade_id = data.get("grade_id")

        if target_grade_id is not None:
            try:
                target_grade_id = int(target_grade_id)
            except (TypeError, ValueError):
                abort(400, message="grade_id must be an integer")

            target_grade = Grade.query.filter_by(id=target_grade_id, student_id=student_id).first()
            if not target_grade:
                abort(404, message="Grade record not found for this student")
        else:
            # Without grade_id, update the most recently added grade for this student.
            target_grade = grades[-1]

        target_grade.grade = grade_value
        db.session.commit()

        summary = build_student_summary(student_id, Grade.query.filter_by(student_id=student_id).order_by(Grade.id.asc()).all())

        return {
            "message": "Grade updated",
            "student": {
                "student_id": summary["student_id"],
                "student_name": summary["student_name"],
                "grade": target_grade.grade,
                "average": summary["average"],
                "updated_grade_id": target_grade.id,
            }
        }, 200

    def delete(self, student_id):
        grades = Grade.query.filter_by(student_id=student_id).all()

        if not grades:
            abort(404, message="Student not found")

        student_name = grades[0].student_name or student_id
        deleted_count = len(grades)

        for row in grades:
            db.session.delete(row)

        db.session.commit()

        return {
            "message": "Student grades deleted",
            "student": {
                "student_id": student_id,
                "student_name": student_name,
                "deleted_grades": deleted_count,
            }
        }, 200


class StudentAverage(Resource):
    def get(self, student_id):
        grades = Grade.query.filter_by(student_id=student_id).order_by(Grade.id.asc()).all()

        if not grades:
            abort(404, message="No grades found for student")

        summary = build_student_summary(student_id, grades)

        return {
            "student_id": summary["student_id"],
            "student_name": summary["student_name"],
            "average": summary["average"],
        }, 200

class Students(Resource):
    def get(self):
        rows = Grade.query.order_by(Grade.student_id.asc(), Grade.id.asc()).all()

        if not rows:
            abort(404, message="No students found")

        student_map = {}
        for row in rows:
            if row.student_id not in student_map:
                student_map[row.student_id] = {
                    "student_id": row.student_id,
                    "student_name": row.student_name or row.student_id,
                    "sum": 0,
                    "count": 0,
                }

            student_map[row.student_id]["sum"] += row.grade
            student_map[row.student_id]["count"] += 1

        students = []
        for data in student_map.values():
            students.append(
                {
                    "student_id": data["student_id"],
                    "student_name": data["student_name"],
                    "average": round(data["sum"] / data["count"], 2),
                }
            )

        return {
            "students": students
        }, 200



# -------------------
# Routes
# -------------------
api.add_resource(Students, "/students")
api.add_resource(StudentGrades, "/students/<string:student_id>/grades")
api.add_resource(StudentAverage, "/students/<string:student_id>/average")

@app.route("/")
def home():
    rows = Grade.query.order_by(Grade.student_id.asc(), Grade.id.asc()).all()

    student_totals = {}
    for row in rows:
        if row.student_id not in student_totals:
            student_totals[row.student_id] = {
                "sum": 0,
                "count": 0,
                "student_name": row.student_name or row.student_id,
            }
        student_totals[row.student_id]["sum"] += row.grade
        student_totals[row.student_id]["count"] += 1

    grade_rows = []
    for row in rows:
        totals = student_totals[row.student_id]
        grade_rows.append(
            {
                "student_id": row.student_id,
                "student_name": totals["student_name"],
                "grade": row.grade,
                "average": round(totals["sum"] / totals["count"], 2),
            }
        )

    return render_template("index.html", grade_rows=grade_rows)



if __name__ == "__main__":
    app.run(debug=True)
