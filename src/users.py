from secure import Hashing
from secure import Verifier
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.ext.associationproxy import association_proxy
db = SQLAlchemy()


class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, unique=True, nullable=False)
    hash_password = db.Column(db.String(255), nullable = False)
    
    enrollments = db.relationship(
        "Enrollment", back_populates="student", cascade="all, delete-orphan"
    )
    courses = association_proxy("enrollments", "course")

    def set_password(self, user_password: str):
       self.hash_password = Hashing(user_password)

    def check_password(self, user_password: str) -> bool:
        return Verifier(self.hash_password, user_password)

    def __repr__(self):
     return f"<Student {self.id!r}, {self.name!r}>"


    
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

   def __repr__(self):
       return f"<Teacher {self.id!r}, {self.name!r}>"     
class Admin(db.Model):
   id = db.Column(db.Integer, primary_key=True)
   name = db.Column(db.String, unique=True, nullable=False)
   hash_password = db.Column(db.String(255), nullable = False)
   

   
   def set_password(self, user_password: str):
       self.hash_password = Hashing(user_password)

   def check_password(self, user_password: str) -> bool:
    return Verifier(self.hash_password, user_password)
   
   def __repr__(self):
    return f"<Admin {self.id!r}, {self.name!r}>"

class Enrollment(db.Model):
    __tablename__ = "enrollments"
    student_id = db.Column(db.Integer, db.ForeignKey("student.id"), primary_key=True)
    course_id = db.Column(db.Integer, db.ForeignKey("course.id"), primary_key=True)
    grade = db.Column(db.Float, nullable=False, default=100.0)

    student = db.relationship("Student", back_populates="enrollments")
    course = db.relationship("Course", back_populates="enrollments")

    def __repr__(self):
        return f"<Enrollment student={self.student_id} course={self.course_id} grade={self.grade}>"
class Course(db.Model):
   id =  db.Column(db.Integer, primary_key =True)
   name = db.Column(db.String, unique = True, nullable = False)
   max = db.Column(db.Integer, nullable = False)
   time = db.Column(db.String, nullable = False)
   teacher = db.Column(db.Integer, db.ForeignKey("teacher.id"), nullable=False)

   enrollments = db.relationship(
        "Enrollment", back_populates="course", cascade="all, delete-orphan"
    )
    
   students = association_proxy(
        "enrollments",
        "student",
        creator=lambda student_obj: Enrollment(student=student_obj),
    )

   @property
   def enrolled_count(self)-> int:
       return len(self.students)

   @property 
   def is_full(self) -> bool:
       return self.enrolled_count >= self.max

   @property
   def capacity(self) -> str:
       return f"{self.enrolled_count}/{self.max}"

   def __repr__(self):
        return f"<Course {self.id!r}, {self.name!r}>"




   #def __repr__(self):
   # return f"<Course {self.id!r}, {self.name!r}: {self.students!r} >"

