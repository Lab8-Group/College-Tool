from flask import redirect, url_for
from flask_admin import Admin as FlaskAdmin
from flask_admin.contrib.sqla import ModelView
from wtforms import PasswordField
from flask_jwt_extended import verify_jwt_in_request, get_jwt
from users import db, Student, Teacher, Admin, Course



class SecureView(ModelView):
    
    column_exclude_list = ['hash_password'] 
    form_excluded_column = ['hash_password'] 

    def is_accessible(self):
        try:
            verify_jwt_in_request(locations=["cookies"])
            return get_jwt().get("role") == "admin"
        except Exception:
            return False

    def inaccessible_callback(self, name, **kwargs):
        return redirect("/")

class UserView(SecureView):
    
    form_extra_fields = {
        "password": PasswordField("Password")  
    }

    def on_model_change(self, form, model, is_created):
        if form.password.data:
            model.set_password(form.password.data)


def init_admin(app):
    admin_panel = FlaskAdmin(app, name="University Portal")
    admin_panel.add_view(UserView(Student, db.session))
    admin_panel.add_view(UserView(Teacher, db.session))
    admin_panel.add_view(UserView(Admin, db.session))
    admin_panel.add_view(SecureView(Course, db.session))