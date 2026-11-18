import os
from pathlib import Path
from flask import Flask, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from users import db, Student, Teacher, Admin, Course, Enrollment
from secure import jwt, Hashing, Verifier
from admin import init_admin
from flask_jwt_extended import set_access_cookies, jwt_required, get_jwt_identity, get_jwt, create_access_token, unset_jwt_cookies

# Load variables from .env file if python-dotenv is installed.
try:
    from dotenv import load_dotenv
except ImportError:
    def load_dotenv():
        env_path = os.path.join(os.path.dirname(__file__), ".env")
        if not os.path.isfile(env_path):
            return False

        with open(env_path, encoding="utf-8") as env_file:
            for line in env_file:
                line = line.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue

                key, value = line.split("=", 1)
                key = key.strip()
                value = value.strip().strip("\"'")
                os.environ.setdefault(key, value)
        return True

load_dotenv()

app = Flask(
    __name__,
    template_folder=str(Path(__file__).resolve().parents[2] / "HTML"),
)


#ADMIN
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")

## JWT
app.config["JWT_SECRET_KEY"] = os.getenv("JWT_KEY") # store in secrets manager
app.config["JWT_TOKEN_LOCATION"] = ["cookies", "headers"]
app.config["JWT_COOKIE_SECURE"] = False # True in production
app.config["JWT_COOKIE_CSRF_PROTECT"] = False


# Fetch the Neon URL from the environment (with a local fallback if needed)
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)
jwt.init_app(app)
init_admin(app)

with app.app_context():
    
    db.create_all()


    if not Student.query.first():
            
            initial_students = [
                Student(name="Johnny Test", hash_password = Hashing("Zebra")),
                Student(name="Dog Test", hash_password = Hashing("Meow")),
                Student(name="Rebecca",  hash_password = Hashing("Wings")),
            ]
            # 4. Stage and commit to disk
            db.session.add_all(initial_students)
            db.session.commit()


    if not Teacher.query.first():
                
               
                stone = Teacher(name="Dr. Stone", hash_password = Hashing("Hello World"))
                gate = Teacher(name="Dr. Gate", hash_password = Hashing("Time Travel"))
                doom = Teacher(name="Dr. Doom", hash_password = Hashing("Four"))
                
                # 4. Stage and commit to disk
                db.session.add_all([stone, gate, doom])
                db.session.commit()

    if not Course.query.first():

            stone = Teacher.query.filter_by(name="Dr. Stone").first()
            gate = Teacher.query.filter_by(name="Dr. Gate").first()
            doom = Teacher.query.filter_by(name="Dr. Doom").first()
            
            initial_courses = [
                Course(name="CSE 100", time="MWF 5:00-6:45pm", instructor=stone, max=12),
                Course(name="CSE 108", time="TR 1:00-3:35pm", instructor=gate, max=12),
                Course(name="WRI 120", time="MWF 9:00-10:1am", instructor=doom, max=12),
            ]
            
            # 4. Stage and commit to disk
            db.session.add_all(initial_courses)
            db.session.commit()

    if not Admin.query.first():
            initial_Admins = [
                 Admin(name="Ifu C", hash_password = Hashing("Jollof Rice")),
                 Admin(name="Amir Walker", hash_password = Hashing("Goodbye World")),
                 Admin(name="Test Dummy", hash_password = Hashing("Smart Dummy"))
            ]
            db.session.add_all(initial_Admins)
            db.session.commit()


ROLE = {
    "student": Student,
    "teacher": Teacher,
    "admin": Admin,
}

def get_current_user():
    user_id = int(get_jwt_identity())
    role = get_jwt().get("role")
    type = ROLE.get(role)
    if not type:
        return None
    return db.session.get(type, user_id)            

def find_username(name: str):
     for role, type in [("student", Student), ("teacher", Teacher), ("admin", Admin)]:
         user = type.query.filter_by(name=name).first()
         if user:
              return user,role
     return None, None
# Define your routes
@app.route("/")
def index():
    return render_template("index.html")

@app.route("/student")
def student_dashboard():
    return render_template("Student/Dashboard.html")

@app.route("/teacher")
def teacher_dashboard():
    return render_template("Teacher/Dashboard.html")

##JWT parts

@app.route("/login", methods=["POST"])
def login():
    data = request.json

    if not data or "name" not in data or "password" not in data:
        return jsonify({"error": "Missing name or password"}), 400

    
    
    user,role = find_username(data["name"])

    if not user or not user.check_password(data["password"]):
        return jsonify({"error": "Bad credentials"}), 401
   
    access_token = create_access_token(identity=str(user.id), additional_claims= {"role": role})
    response = jsonify({"msg": "Login successful", "role": role, "name": user.name})
    set_access_cookies(response, access_token)
    return response


@app.route("/logout", methods=["POST"])
def logout():
    response = jsonify({"message": "Logged out"})
    unset_jwt_cookies(response)
    return response, 200


##Student grades 

@app.route('/grades/<int:course_id>/students', methods=['GET'])
@jwt_required()
def handle_students(course_id):
     user = get_current_user()
     course = db.session.get(Course,course_id)

     if not course:
          return jsonify({"error": "Course not found"}), 404

     if  not isinstance(user, Teacher) or course.instructor != user:
              return jsonify({"error": "Unauthorized access"}), 403
    
     roster = [
         {
            "id": e.student.id,
            "name": e.student.name,
            "grade": e.grade,
        }
        for e in course.enrollments
    ]
     return jsonify({"course_name": course.name, "students": roster}), 200


@app.route('/grades/<int:course_id>/students/<int:student_id>/grade', methods=['PUT'])
@jwt_required()
def edit_student(course_id,student_id):

     user = get_current_user()
     course = db.session.get(Course, course_id)

     if not course:
               return jsonify({"error": "Course not found"}), 404   

     if  not isinstance(user, Teacher) or course.instructor != user :
        return jsonify({"error": "Unauthorized access"}), 403


     enrollment = db.session.get(Enrollment, (student_id, course_id))

     if not enrollment:
          return jsonify({"error": "Student is not enrolled in this course"}), 404
            
     data = request.get_json()
     if not data or 'grade' not in data:
        return jsonify({"error": "Missing grade"}), 400
            
     enrollment.grade = data["grade"]
     db.session.commit()
     return jsonify({
                      "id": enrollment.student.id,
                      "name": enrollment.student.name,
                      "grade": enrollment.grade,
                  }), 200

@app.route('/me', methods=['GET'])
@jwt_required()
def save_user():
    user = get_current_user()

    if not user: return jsonify({"error": "User not found"}), 404

    return jsonify({"name": user.name, "role": get_jwt().get("role")})




@app.route("/courses/<int:course_id>/enrollment", methods=["PUT", "POST"])
@jwt_required()
def enroll_student(course_id):
    student = get_current_user()
    course = db.session.get(Course, course_id)
    if not isinstance(student, Student):
        return jsonify({"error": "Only students can enroll in courses"}), 403

   #handle_courses
    if not course:
         return jsonify({"error": "Course does not exist"}), 404
   
    

    if student in course.students:
        return jsonify({"error": "Already enrolled"}), 400
    if course.is_full:
        return jsonify({"error": "Course is full"}), 400

    course.students.append(student)
    db.session.commit()
    return jsonify({"msg": f"Enrolled in {course.name}", "capacity": course.capacity}), 200

@app.route("/courses/<int:course_id>/leaving", methods=["DELETE"])
@jwt_required()
def un_enroll(course_id):
        student = get_current_user()
        course = db.session.get(Course, course_id)

        if not isinstance(student, Student):
             return jsonify({"error": "Only students can unenroll in courses"}), 403
     
        if not course:
                 return jsonify({"error": "Course does not exist"}), 404
        
        
     
        if student not in course.students:
             return jsonify({"error": "Not enrolled"}), 400
     
        course.students.remove(student)
        db.session.commit()
        return jsonify({"msg": f"Unenrolled in {course.name}", "capacity": course.capacity}), 200


@app.route("/courses", methods=["GET"])
@jwt_required()
def handle_courses():
        user = get_current_user()
        courses = Course.query.all()

        result = [
            {
                "id": c.id,
                "name": c.name,
                "teacher": c.instructor.name if c.instructor else "TBA",
                "time": c.time,
                "capacity": c.capacity,
                "is_full": c.is_full,
                "enrolled": (user in c.students) if isinstance(user, Student) else False,
            }
            for c in courses
        ]

        return jsonify(result), 200

@app.route("/my-courses", methods=["GET"])
@jwt_required()
def your_courses():
        user = get_current_user()
        if not isinstance(user, (Student, Teacher)):
         return jsonify({"error": "Only students and teachers have courses"}), 403

        result = [
            {
                "id": c.id,
                "name": c.name,
                "teacher": c.instructor.name if c.instructor else "TBA",
                "time": c.time,
                "capacity": c.capacity,
            }
            for c in user.courses
        ]

        return jsonify(result), 200

def main():
    with app.app_context():
        db.create_all()
    app.run(debug=True, port=5000)


if __name__ == "__main__":
    main()
    