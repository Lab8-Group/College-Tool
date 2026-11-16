from secure import Hashing
from secure import Verifier
from flask_sqlalchemy import SQLAlchemy
db = SQLAlchemy()


class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, unique=True, nullable=False)
    grade = db.Column(db.Integer, nullable = False)
    hash_password = db.Column(db.String(255), nullable = False)
    #course = db.Column(db.String, nullable=False)

    def set_password(self, user_password: str):
       self.hash_password = Hashing(user_password)

    def check_password(self, user_password: str) -> bool:
        return Verifier(self.hash_password, user_password)

    def __repr__(self):
     return f"<Student {self.id!r}, {self.name!r}: {self.grade!r} >"


    
class Teacher(db.Model):
   id = db.Column(db.Integer, primary_key=True)
   name = db.Column(db.String, unique=True, nullable=False)
   hash_password = db.Column(db.String(255), nullable = False)
   courses = db.relationship("Course", backref="instructor", lazy=True)

   #def __repr__(self):
    #return f"<Student {self.id!r}, {self.name!r}: {self.grade!r} >"

   def set_password(self, user_password: str):
        self.hash_password = Hashing(user_password)

   def check_password(self, user_password: str) -> bool:
    return Verifier(self.hash_password, user_password)        
class Admin(db.Model):
   id = db.Column(db.Integer, primary_key=True)
   name = db.Column(db.String, unique=True, nullable=False)
   hash_password = db.Column(db.String(255), nullable = False)

   def set_password(self, user_password: str):
       self.hash_password = Hashing(user_password)

   def check_password(self, user_password: str) -> bool:
    return Verifier(self.hash_password, user_password)
   #def __repr__(self):
    #return f"<Student {self.id!r}, {self.name!r}: {self.grade!r} >"

enrollments = db.Table('enrollments',db.Column('student_id', db.Integer, db.ForeignKey('student.id'), primary_key=True), db.Column('course_id', db.Integer, db.ForeignKey('course.id'), primary_key=True))

class Course(db.Model):
   id =  db.Column(db.Integer, primary_key =True)
   name = db.Column(db.String, unique = True, nullable = False)
   max = db.Column(db.Integer, nullable = False)
   time = db.Column(db.Integer, nullable = False)
   teacher = db.Column(db.Integer, db.ForeignKey("teacher.id"), nullable=False)

   students = db.relationship('Student', secondary=enrollments, backref='courses')

   @property
   def enrolled_count(self)-> int:
       return len(self.students)

   @property 
   def is_full(self) -> bool:
       return self.enrolled_count >= self.max

   @property
   def capacity(self) -> str:
       return f"{self.enrolled_count}/{self.max}"






   #def __repr__(self):
   # return f"<Course {self.id!r}, {self.name!r}: {self.students!r} >"

