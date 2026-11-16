from flask import Flask
from secure import Hashing
from secure import Verifier
from flask_sqlalchemy import SQLAlchemy
app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///example.sqlite"
db = SQLAlchemy(app)


class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, unique=True, nullable=False)
    grade = db.Columb(db.Integer, nullable = False)
    hash_password = db.Column(db.String(255), nullable = False)
    course = db.Column(db.String, nullable=False)

    def set_password(self, user_password: str):
       self.hash_password = Hashing(user_password)

    def __repr__(self):
     return f"<Student {self.id!r}, {self.name!r}: {self.grade!r} >"

    
class Teacher(db.Model):
   id = db.Column(db.Integer, primary_key=True)
   name = db.Column(db.String, unique=True, nullable=False)
   hash_password = db.Column(db.String(255), nullable = False)
   course = db.Column(db.String, nullable=False)

   #def __repr__(self):
    #return f"<Student {self.id!r}, {self.name!r}: {self.grade!r} >"

   def set_password(self, user_password: str):
        self.hash_password = Hashing(user_password)
        
class Admin(db.Model):
   id = db.Column(db.Integer, primary_key=True)
   name = db.Column(db.String, unique=True, nullable=False)
   hash_password = db.Column(db.String(255), nullable = False)

def set_password(self, user_password: str):
       self.hash_password = Hashing(user_password)
   #def __repr__(self):
    #return f"<Student {self.id!r}, {self.name!r}: {self.grade!r} >"

class Course(db.Model):
   id =  db.Column(db.Integer, primary_key =True)
   name = db.Column(db.String, unique = True, nullable = False)
   students = db.column(db.Integer, nullable = False)
   time = db.column(db.Integer, nullable = False)
   teacher = db.column(db.String, nullable = False)

   #def __repr__(self):
   # return f"<Course {self.id!r}, {self.name!r}: {self.students!r} >"

