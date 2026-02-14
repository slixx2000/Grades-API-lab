from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_restful import Api, Resource, reqparse, abort, fields, marshal_with

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///studentgrades.db'
db = SQLAlchemy(app)
api = Api(app)

class StudentModel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    studentName = db.Column(db.String(100), nullable=False, unique=True)
    studentID = db.Column(db.String(20), nullable=False, unique=True)
    score = db.Column(db.Float, nullable=False)
    grade = db.Column(db.String(10), nullable=False)

    def __repr__(self):
        return f"Student(Name={self.studentName}, studentID={self.studentID}, score={self.score}, grade={self.grade})"

student_create_args = reqparse.RequestParser()
student_create_args.add_argument("studentName", type=str, help="Name of the student is required", required=True)
student_create_args.add_argument("studentID", type=str, help="ID of the student is required", required=True)
student_create_args.add_argument("grade", type=str, help="Grade of the student is required", required=True)
student_create_args.add_argument("score", type=float, help="Score of the student is required", required=True)

student_score_update_args = reqparse.RequestParser()
student_score_update_args.add_argument("score", type=float, help="Score of the student is required", required=True)

userFields = {
    'id':fields.Integer,
    'studentName':fields.String,
    'studentID':fields.String,
    'score':fields.Float,
    'grade':fields.String
}
gradeFields = {
    'studentID':fields.String,
    'score':fields.Float
}

class Students(Resource):
    @marshal_with(userFields)
    def get(self):
        students = StudentModel.query.all()
        return students

api.add_resource(Students, '/course/students')

class Student(Resource):
    @marshal_with(userFields)
    def get(self, student_id):
        student = StudentModel.query.filter_by(id=student_id).first()
        if not student:
            abort(404, message="Student not found")
        return student

    @marshal_with(userFields)
    def post(self):
        args = student_create_args.parse_args()
        if args['score'] < 0 or args['score'] > 100:
            abort(400, message="Score must be between 0 and 100")

        existing_student = StudentModel.query.filter(
            (StudentModel.studentName == args['studentName']) |
            (StudentModel.studentID == args['studentID'])
        ).first()
        if existing_student:
            abort(409, message="Student name or ID already exists")

        student = StudentModel(studentName=args['studentName'], studentID=args['studentID'], score=args['score'], grade=args['grade'])
        db.session.add(student)
        db.session.commit()
        return student, 201

    @marshal_with(gradeFields)
    def put(self, student_id):
        args = student_score_update_args.parse_args()
        student = StudentModel.query.filter_by(id=student_id).first()
        if not student:
            abort(404, message="Student not found")

        if args['score'] < 0 or args['score'] > 100:
            abort(400, message="Score must be between 0 and 100")

        student.score = args['score']
        db.session.commit()
        return student, 200

api.add_resource(Student, '/course/student', '/course/student/<int:student_id>')


@app.route('/')
def home():
    return render_template('index.html')



if __name__ == '__main__':
    app.run(debug=True)