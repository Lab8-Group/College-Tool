from flask import redirect
from flask_admin import Admin as FlaskAdmin, AdminIndexView
from flask_admin.theme import Bootstrap4Theme
from flask_admin.contrib.sqla import ModelView
from wtforms import PasswordField
from wtforms.validators import InputRequired, ValidationError
from flask_jwt_extended import verify_jwt_in_request, get_jwt

from .users import db, Student, Teacher, Admin, Course, Enrollment


def _is_admin() -> bool:
    try:
        verify_jwt_in_request(locations=["cookies"])
        return get_jwt().get("role") == "admin"
    except Exception:
        return False


class SecureIndex(AdminIndexView):
    """FIX: the /admin/ home page itself is now admin-only."""

    def is_accessible(self):
        return _is_admin()

    def inaccessible_callback(self, name, **kwargs):
        return redirect("/")


class SecureView(ModelView):
    column_exclude_list = ["hash_password"]
    form_excluded_columns = ["hash_password"]

    def is_accessible(self):
        return _is_admin()

    def inaccessible_callback(self, name, **kwargs):
        return redirect("/")


class UserView(SecureView):
    form_extra_fields = {"password": PasswordField("Password")}

    def create_form(self, obj=None):
        form = super().create_form(obj)
        form.password.validators = (*form.password.validators, InputRequired())
        return form

    def on_model_change(self, form, model, is_created):
        if form.password.data:
            model.set_password(form.password.data)

        # FIX: login looks users up by name across all three tables, so a name
        # must be unique across Student/Teacher/Admin, not just within one table.
        with db.session.no_autoflush:
            for table in (Student, Teacher, Admin):
                query = table.query.filter(table.name == model.name)
                if isinstance(model, table) and model.id is not None:
                    query = query.filter(table.id != model.id)
                if query.first():
                    raise ValidationError(
                        f'The name "{model.name}" is already used by another account.'
                    )


class EnrollmentView(SecureView):
    column_list = ("student", "course", "grade")


def init_admin(app):
    # Template paths use the exact folder case on disk (HTML/Admin/...), so this
    # works on case-sensitive filesystems (Linux) as well as Windows/macOS.
    theme = Bootstrap4Theme(base_template="Admin/portal_base.html")
    panel = FlaskAdmin(
        app,
        name="WVC School Portal",
        theme=theme,
        index_view=SecureIndex(template="Admin/index.html"),
    )
    panel.add_view(UserView(Student, db.session, endpoint="students"))
    panel.add_view(UserView(Teacher, db.session, endpoint="teachers"))
    panel.add_view(UserView(Admin, db.session, endpoint="admin_users"))
    panel.add_view(SecureView(Course, db.session, endpoint="courses"))
    panel.add_view(
        EnrollmentView(Enrollment, db.session, name="Enrollments", endpoint="enrollments")
    )
