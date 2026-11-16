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


with app.app_context():
    
    db.create_all()

    
    if not Course.query.first():
        
        initial_courses = [
            Course(name="CSE 100", time=1000, teacher="Dr. Smith", max=12),
            Course(name="CSE 108", time=1300, teacher="Prof. Jones", max=12),
            Course(name="WRI 120", time=1500, teacher="Dr. Lee", max=12),
        ]
        
        # 4. Stage and commit to disk
        db.session.add_all(initial_courses)
        db.session.commit()

    if not Student.query.first():
            
            initial_students = [
                Student(name="Johnny Test", grade=95.0, hash_password = Hashing("Zebra")),
                Student(name="Dog Test", grade=82.5, hash_password = Hashing("Meow")),
                Student(name="Rebecca", grade=78.0,  hash_password = Hashing("Wings")),
            ]
            # 4. Stage and commit to disk
            db.session.add_all(initial_students)
            db.session.commit()




   #def __repr__(self):
   # return f"<Course {self.id!r}, {self.name!r}: {self.students!r} >"

