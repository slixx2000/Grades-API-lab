from flask import Flask
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
    grade = db.Column(db.String(10), nullable=False)

    def __repr__(self):
        return f"Student(Name={studentName}, studentID={studentID}, grade={grade})"

student_put_args = reqparse.RequestParser()
student_put_args.add_argument("studentName", type=str, help="Name of the student is required", required=True)
student_put_args.add_argument("studentID", type=str, help="ID of the student is required", required=True)
student_put_args.add_argument("grade", type=str, help="Grade of the student is required", required=True)

class Students(Resource):
    def get(self):
        students = StudentModel.query.all()
        return students

api.add_resource(Students, '/course/students')

@app.route('/')
def home():
    return '<h1>Welcome to the Student Grades API!</h1>'



if __name__ == '__main__':
    app.run(debug=True)