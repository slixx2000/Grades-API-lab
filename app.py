from flask import Flask, request, render_template
from flask_restful import Resource, Api, abort
from flask_sqlalchemy import SQLAlchemy

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
    grade = db.Column(db.Float, nullable=False)

    def to_dict(self):
        return {
            "id": self.id,
            "student_id": self.student_id,
            "grade": self.grade
        }


# Create tables
with app.app_context():
    db.create_all()


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


# -------------------
# Resources
# -------------------
class StudentGrades(Resource):
    def get(self, student_id):
        grades = Grade.query.filter_by(student_id=student_id).all()

        if not grades:
            abort(404, message="Student not found")

        return {
            "student_id": student_id,
            "grades": [g.grade for g in grades]
        }, 200

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

        return {
            "message": "Grade added",
            "student_id": student_id,
            "grade": grade_value
        }, 201


class StudentAverage(Resource):
    def get(self, student_id):
        grades = Grade.query.filter_by(student_id=student_id).all()

        if not grades:
            abort(404, message="No grades found for student")

        average = sum(g.grade for g in grades) / len(grades)

        return {
            "student_id": student_id,
            "average": round(average, 2)
        }, 200

class Students(Resource):
    def get(self):
        results = db.session.query(Grade.student_id).distinct().all()

        if not results:
            abort(404, message="No students found")

        students = [row.student_id for row in results]

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
    return render_template("index.html")



if __name__ == "__main__":
    app.run(debug=True)
