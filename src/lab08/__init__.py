import os
from dotenv import load_dotenv
from flask import Flask, render_template, request, jsonify, foreignkey
from flask_sqlalchemy import SQLAlchemy
from users import db, Student, Teacher, Admin, Course
from secure import jwt, Hashing, Verifier
from admin import init_admin
from flask_jwt_extended import set_access_cookies, jwt_required, get_jwt_identity, get_jwt, create_access_token, unset_jwt_cookies

# Load variables from .env file into os.environ
load_dotenv()

app = Flask(__name__)

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

with app.app_context():
    
    db.create_all()


    if not Student.query.first():
            
            initial_students = [
                Student(name="Johnny Test", grade=95.0, hash_password = Hashing("Zebra")),
                Student(name="Dog Test", grade=82.5, hash_password = Hashing("Meow")),
                Student(name="Rebecca", grade=78.0,  hash_password = Hashing("Wings")),
            ]
            # 4. Stage and commit to disk
            db.session.add_all(initial_students)
            db.session.commit()


    if not Teacher.query.first():
                
               
                stone = Teacher(name="Dr. Stone", hash_password = Hashing("Hello World")),
                gate = Teacher(name="Dr. Gate", hash_password = Hashing("Time Travel")),
                doom = Teacher(name="Dr. Doom", hash_password = Hashing("Four")),
                
                # 4. Stage and commit to disk
                db.session.add_all(stone, gate, doom)
                db.session.commit()

    if not Course.query.first():
            
            initial_courses = [
                Course(name="CSE 100", time=1000, teacher=stone, max=12),
                Course(name="CSE 108", time=1300, teacher=gate, max=12),
                Course(name="WRI 120", time=1500, teacher=doom, max=12),
            ]
            
            # 4. Stage and commit to disk
            db.session.add_all(initial_courses)
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

##JWT parts

@app.route("/login", methods=["POST"])
def login():
    data = request.json

    if not data or "name" not in data or "password" not in data:
        return jsonify({"error": "Missing name or password"}), 400

    
    
    user,role = find_username(data["name"])

    if not user or not user.check.password(data["password"]):
        return jsonify({"error": "Bad credentials"}), 401
   
    access_token = create_access_token(identity=str(user.id), additional_claims= {"role": role})
    response = jsonify({"msg": "Login successful"})
    set_access_cookies(response, access_token)
    return response


@app.route("/logout", methods=["POST"])
def logout():
    response = jsonify({"message": "Logged out"})
    unset_jwt_cookies(response)
    return response, 200


##Student grades 


@app.route('/grades', methods=['GET', 'POST'])
def handle_grades():
    if request.method == 'GET':
        students = Student.query.all()
        return jsonify({s.name: s.grade for s in students}), 200

    if request.method == 'POST':
        data = request.get_json()
        if not data or 'name' not in data or 'grade' not in data:
            return jsonify({"error": "Missing name or grade"}), 400


    name = data['name']
    grade = data['grade']
    password = data['hash_password']
    
    existing_student = Student.query.filter_by(name=name).first()
    if existing_student:
        return jsonify({"error": "Student already exists"}), 400

    
    new_student = Student(name = name, grade = grade, password = password)

    db.session.add(new_student)
    db.session.commit()
    return jsonify({name: grade}), 201

@app.route('/grades/<name>', methods=['GET', 'PUT', 'DELETE'])
def handle_student(name):
    student = Student.query.filter_by(name=name).first()

    if request.method == 'GET':
        if not student:
            return jsonify({"error": f"Student '{name}' not found"}), 404
            
    
        return jsonify({student.name: student.grade}), 200
        
    elif request.method == 'PUT':
        if not student:
            return jsonify({"error": f"Student '{name}' not found"}), 404

        data = request.get_json()
        if not data or 'grade' not in data:
            return jsonify({"error": "Missing grade"}), 400

        student.grade = data["grade"]
        db.session.commit()
        return jsonify({student.name: student.grade}), 200

    elif request.method == 'DELETE':
        if not student:
            return jsonify({"error": f"Student '{name}' not found"}), 404

        deleted_grade = student.grade
        db.session.delete(student)
        db.session.commit()
        return jsonify({name: deleted_grade}), 200
    

@app.route("/courses", methods=["PUT", "POST"])
@jwt_required
def enroll_student(course_id):
    student = get_current_user
    if not isinstance(student, Student):
        return jsonify({"error": "Only students can enroll in courses"}), 403

   
    course = db.session.get(Course, course_id)

    if student in course.students:
        return jsonify({"error": "Already enrolled"}), 400
    if course.is_full:
        return jsonify({"error": "Course is full"}), 400

    course.students.append(student)
    db.session.commit()
    return jsonify({"msg": f"Enrolled in {course.name}", "capacity": course.capacity}), 200

@app.route("/courses", methods=["Delete"])
@jwt_required
def un_enroll(course_id):
        student = get_current_user
        if not isinstance(student, Student):
             return jsonify({"error": "Only students can unenroll in courses"}), 403
     
        
        course = db.session.get(Course, course_id)
     
        if student in course.students:
             return jsonify({"error": "Already enrolled"}), 400
     
        course.students.delete(student)
        db.session.commit()
        return jsonify({"msg": f"Unenrolled in {course.name}", "capacity": course.capacity}), 200


def main():
    with app.app_context():
        db.create_all()
    app.run(debug=True, port=5000)


if __name__ == "__main__":
    main()
    