import os
from pathlib import Path

from dotenv import load_dotenv
from flask import Flask, render_template, request, jsonify, redirect
from flask_jwt_extended import (
    set_access_cookies,
    jwt_required,
    verify_jwt_in_request,
    get_jwt_identity,
    get_jwt,
    create_access_token,
    unset_jwt_cookies,
)
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from .users import db, Student, Teacher, Admin, Course, Enrollment
from .secure import jwt
from .admin import init_admin
from .seed import seed_if_empty, reset_and_seed

load_dotenv()


def _require_env(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise RuntimeError(f"{name} is missing - copy .env.example to .env and fill it in.")
    return value


app = Flask(
    __name__,
    template_folder=str(Path(__file__).resolve().parents[2] / "HTML"),
)

app.config["SECRET_KEY"] = _require_env("SECRET_KEY")          # Flask-Admin sessions/flash
app.config["JWT_SECRET_KEY"] = _require_env("JWT_KEY")
app.config["JWT_TOKEN_LOCATION"] = ["cookies", "headers"]
app.config["JWT_COOKIE_SECURE"] = False        # set True when served over HTTPS
app.config["JWT_COOKIE_CSRF_PROTECT"] = False  # set True in production (teacher.js already sends X-CSRF-TOKEN)
app.config["SQLALCHEMY_DATABASE_URI"] = _require_env("DATABASE_URL")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)
jwt.init_app(app)
init_admin(app)

with app.app_context():
    db.create_all()
    seed_if_empty()  # loads Enrollment example data for Lab8.xlsx into an empty DB


ROLE = {"student": Student, "teacher": Teacher, "admin": Admin}


def get_current_user():
    user_id = int(get_jwt_identity())
    model = ROLE.get(get_jwt().get("role"))
    if not model:
        return None
    return db.session.get(model, user_id)


def find_username(name: str):
    for role, model in (("student", Student), ("teacher", Teacher), ("admin", Admin)):
        user = model.query.filter_by(name=name).first()
        if user:
            return user, role
    return None, None


def role_page(role: str, template: str):
    """Serve an HTML dashboard only to a logged-in user with the right role;
    everyone else is sent back to the login page."""
    try:
        verify_jwt_in_request()
    except Exception:
        return redirect("/")
    if get_jwt().get("role") != role:
        return redirect("/")
    return render_template(template)


# ---------- pages ----------

@app.route("/")
def index():
    return render_template("index.html")


@app.route("/student")
def student_dashboard():
    return role_page("student", "Student/Dashboard.html")


@app.route("/teacher")
def teacher_dashboard():
    return role_page("teacher", "Teacher/Dashboard.html")


@app.route("/admin-dashboard")
def admin_dashboard():
    return role_page("admin", "Admin/Dashboard.html")


# ---------- auth ----------

@app.route("/login", methods=["POST"])
def login():
    data = request.get_json(silent=True)
    if not data or "name" not in data or "password" not in data:
        return jsonify({"error": "Missing name or password"}), 400

    user, role = find_username(str(data["name"]).strip())
    if not user or not user.check_password(str(data["password"])):
        return jsonify({"error": "Bad credentials"}), 401

    token = create_access_token(identity=str(user.id), additional_claims={"role": role})
    response = jsonify({"msg": "Login successful", "role": role, "name": user.name})
    set_access_cookies(response, token)
    return response


@app.route("/logout", methods=["POST"])
def logout():
    if request.form.get("return_to_home") == "1":
        response = redirect("/")
    else:
        response = jsonify({"message": "Logged out"})
    unset_jwt_cookies(response)
    return response


@app.route("/me", methods=["GET"])
@jwt_required()
def save_user():
    user = get_current_user()
    if not user:
        return jsonify({"error": "User not found"}), 404
    return jsonify({"name": user.name, "role": get_jwt().get("role")})


# ---------- teacher: roster + grades ----------

def _teacher_course_or_error(course_id):
    """Returns (course, None) or (None, (json, status))."""
    user = get_current_user()
    course = db.session.get(Course, course_id)
    if not course:
        return None, (jsonify({"error": "Course not found"}), 404)
    if not isinstance(user, Teacher) or course.instructor != user:
        return None, (jsonify({"error": "Unauthorized access"}), 403)
    return course, None


@app.route("/grades/<int:course_id>/students", methods=["GET"])
@jwt_required()
def handle_students(course_id):
    course, error = _teacher_course_or_error(course_id)
    if error:
        return error

    roster = [
        {"id": e.student.id, "name": e.student.name, "grade": e.grade}
        for e in sorted(course.enrollments, key=lambda e: e.student.name)
    ]
    return jsonify({"course_name": course.name, "students": roster}), 200


@app.route("/grades/<int:course_id>/students/<int:student_id>/grade", methods=["PUT"])
@jwt_required()
def edit_student(course_id, student_id):
    course, error = _teacher_course_or_error(course_id)
    if error:
        return error

    enrollment = db.session.get(Enrollment, (student_id, course_id))
    if not enrollment:
        return jsonify({"error": "Student is not enrolled in this course"}), 404

    data = request.get_json(silent=True)
    if not data or "grade" not in data:
        return jsonify({"error": "Missing grade"}), 400

    # FIX: validate on the server (previously stored whatever was sent)
    raw = data["grade"]
    if isinstance(raw, bool):
        return jsonify({"error": "Grade must be a number"}), 400
    try:
        grade = float(raw)
    except (TypeError, ValueError):
        return jsonify({"error": "Grade must be a number"}), 400
    if not 0 <= grade <= 100:  # also rejects NaN / infinity
        return jsonify({"error": "Grade must be between 0 and 100"}), 400

    enrollment.grade = grade
    db.session.commit()
    return jsonify(
        {"id": enrollment.student.id, "name": enrollment.student.name, "grade": enrollment.grade}
    ), 200


# ---------- student: enroll / drop ----------

@app.route("/courses/<int:course_id>/enrollment", methods=["PUT", "POST"])
@jwt_required()
def enroll_student(course_id):
    student = get_current_user()
    if not isinstance(student, Student):
        return jsonify({"error": "Only students can enroll in courses"}), 403

    # FIX: lock the course row so two students can't both take the last seat
    # (FOR UPDATE on Postgres; SQLite ignores it, which is fine for local dev).
    course = db.session.execute(
        select(Course).where(Course.id == course_id).with_for_update()
    ).scalar_one_or_none()
    if not course:
        return jsonify({"error": "Course does not exist"}), 404

    if db.session.get(Enrollment, (student.id, course.id)):
        db.session.rollback()
        return jsonify({"error": "Already enrolled"}), 400
    if course.is_full:
        db.session.rollback()
        return jsonify({"error": "Course is full"}), 400

    try:
        db.session.add(Enrollment(student=student, course=course, grade=None))
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return jsonify({"error": "Already enrolled"}), 400

    return jsonify({"msg": f"Enrolled in {course.name}", "capacity": course.capacity}), 200


@app.route("/courses/<int:course_id>/leaving", methods=["DELETE"])
@jwt_required()
def un_enroll(course_id):
    student = get_current_user()
    if not isinstance(student, Student):
        return jsonify({"error": "Only students can unenroll in courses"}), 403

    course = db.session.get(Course, course_id)
    if not course:
        return jsonify({"error": "Course does not exist"}), 404

    enrollment = db.session.get(Enrollment, (student.id, course.id))
    if not enrollment:
        return jsonify({"error": "Not enrolled"}), 400

    db.session.delete(enrollment)
    db.session.commit()
    return jsonify({"msg": f"Unenrolled in {course.name}", "capacity": course.capacity}), 200


# ---------- course lists ----------

@app.route("/courses", methods=["GET"])
@jwt_required()
def handle_courses():
    user = get_current_user()
    my_ids = {e.course_id for e in user.enrollments} if isinstance(user, Student) else set()

    result = [
        {
            "id": c.id,
            "name": c.name,
            "teacher": c.instructor.name if c.instructor else "TBA",
            "time": c.time,
            "capacity": c.capacity,
            "is_full": c.is_full,
            "enrolled": c.id in my_ids,
        }
        for c in Course.query.order_by(Course.name).all()
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
        for c in sorted(user.courses, key=lambda c: c.name)
    ]
    return jsonify(result), 200


# ---------- entry points ----------

def main():
    app.run(debug=True, port=5000)


def reseed():
    """`uv run lab08-reseed` - wipe the database and reload the workbook data."""
    shown = app.config["SQLALCHEMY_DATABASE_URI"].split("@")[-1]  # hide credentials
    answer = input(f"This DROPS ALL TABLES in '{shown}' and reseeds. Type YES to continue: ")
    if answer.strip() != "YES":
        print("Cancelled.")
        return
    with app.app_context():
        reset_and_seed()
    print("Database reset and seeded from the workbook.")


if __name__ == "__main__":
    main()
