import os
from dotenv import load_dotenv
from flask import Flask, render_template, request, jsonify, foreignkey
from flask_sqlalchemy import SQLAlchemy
from users import db, Student, Teacher, Admin, Course
from secure import Hashing, Verifier

# Load variables from .env file into os.environ
load_dotenv()

app = Flask(__name__)

# Fetch the Neon URL from the environment (with a local fallback if needed)
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)

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


'''
# Define your routes
@app.route("/")
def index():
    return render_template("index.html")


@app.route("/health")
def health():
    return jsonify({"status": "healthy"}), 200


def main():
    with app.app_context():
        db.create_all()
    app.run(debug=True, port=5000)


if __name__ == "__main__":
    main()
    '''