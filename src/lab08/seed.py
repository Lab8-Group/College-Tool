"""Seed the database from 'Enrollment example data for Lab8.xlsx'.

Workbook layout: course fields (name / teacher / time / capacity) appear only on
the first row of each course block; following rows only have student + grade.
Blank separator rows are skipped and names are trimmed ("Mindy Norris ").

Demo logins (local/dev only - the workbook has no passwords):
    every student  -> password  student123
    every teacher  -> password  teacher123
    admin          -> name "Admin", password admin123
"""
from pathlib import Path

from openpyxl import load_workbook

from .secure import Hashing
from .users import db, Student, Teacher, Admin, Course, Enrollment

WORKBOOK = Path(__file__).resolve().parents[2] / "Enrollment example data for Lab8.xlsx"

STUDENT_PASSWORD = "student123"
TEACHER_PASSWORD = "teacher123"
ADMIN_NAME, ADMIN_PASSWORD = "Admin", "admin123"


def _clean(value) -> str:
    return str(value).strip() if value is not None else ""


def seed_from_workbook(path: Path = WORKBOOK) -> None:
    ws = load_workbook(path, read_only=True, data_only=True).active

    teachers, students = {}, {}
    course = None

    for row in ws.iter_rows(min_row=2, values_only=True):
        cname, tname, time, cap, sname, grade = (list(row) + [None] * 6)[:6]
        cname, tname, time, sname = map(_clean, (cname, tname, time, sname))

        if cname:  # first row of a new course block
            teacher = teachers.get(tname)
            if teacher is None:
                teacher = Teacher(name=tname, hash_password=Hashing(TEACHER_PASSWORD))
                teachers[tname] = teacher
                db.session.add(teacher)
            course = Course(name=cname, time=time, max=int(cap), instructor=teacher)
            db.session.add(course)

        if not sname:  # blank separator row
            continue
        if course is None:
            raise ValueError("Workbook has a student row before any course row.")

        student = students.get(sname)
        if student is None:
            student = Student(name=sname, hash_password=Hashing(STUDENT_PASSWORD))
            students[sname] = student
            db.session.add(student)

        db.session.add(
            Enrollment(
                student=student,
                course=course,
                grade=float(grade) if grade not in (None, "") else None,
            )
        )

    db.session.add(Admin(name=ADMIN_NAME, hash_password=Hashing(ADMIN_PASSWORD)))
    db.session.commit()


def seed_if_empty() -> bool:
    """Seed only when the database has no users/courses. Returns True if it seeded."""
    if Course.query.first() or Student.query.first() or Teacher.query.first():
        return False
    if not WORKBOOK.is_file():
        print(f"[seed] Workbook not found at {WORKBOOK}; database left empty.")
        return False
    seed_from_workbook()
    return True


def reset_and_seed() -> None:
    """DROP every table, recreate them, and seed from the workbook."""
    db.drop_all()
    db.create_all()
    seed_from_workbook()
