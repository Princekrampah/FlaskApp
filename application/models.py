from application import db, login_manager, app
from flask_login import UserMixin, current_user
from datetime import datetime
from flask import redirect, url_for,flash
from flask_admin import Admin, AdminIndexView, BaseView, expose
from flask_admin.contrib.sqla import ModelView



@login_manager.user_loader
def load_user(user_id):
    return Users.query.get(int(user_id))

class Users(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(30), unique=False, nullable=False)
    password = db.Column(db.String(60), unique=True, nullable=False)
    Class = db.Column(db.String(20), unique=False, nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    is_teacher = db.Column(db.Boolean, default=False)
    files = db.relationship('Files', backref = "author", lazy = True)

    def __repr__(self):
        return f"{self.username}"



class Files(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    title = db.Column(db.String(100), nullable = False)
    instructions = db.Column(db.Text, nullable = False)
    Class = db.Column(db.String(20), nullable = False)
    file_name = db.Column(db.String(20), nullable = False, unique = True)
    date_uploaded = db.Column(db.DateTime, nullable= False, default=datetime.utcnow)
    post_author = db.Column(db.Integer, db.ForeignKey("users.id"), nullable = False)

    def __repr__(self):
        return f"File('{self.title}', '{self.date_uploaded}')"


class StudentsQuestions(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    title = db.Column(db.String(20), nullable = False)
    content = db.Column(db.Text, nullable = False)
    target = db.Column(db.String(100), nullable = False)
    student = db.Column(db.String(100), nullable = False)
    Class = db.Column(db.String(20), nullable = False)
    date_uploaded = db.Column(db.DateTime, nullable= False, default=datetime.utcnow)
    viewed_count = db.Column(db.Integer, nullable = False, default = 0)


class TeachersReply(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    content = db.Column(db.Text, nullable = False)
    reply_author = db.Column(db.String(100), nullable = False)
    target_student = db.Column(db.String(100), nullable = False)
    date_uploaded = db.Column(db.DateTime, nullable= False, default=datetime.utcnow)
    viewed_count = db.Column(db.Integer, nullable = False, default = 0)

class MyModelView(ModelView):
    def is_accessible(self):
        page_size = 30
        return current_user.is_authenticated and current_user.is_admin
    
    def inaccessible_callback(self, name):
        flash("Please login to access that page" ,  "info")
        return redirect(url_for("login"))

class DocumentaionView(BaseView):
    @expose("/")
    def index(self):
        return self.render("admin/documentaion.html")

class MyAdminIndexView(AdminIndexView):
    def is_accessible(self):
        return current_user.is_authenticated and current_user.is_admin
    
    def inaccessible_callback(self, name):
        flash("Please login to access that page", "info")
        return redirect(url_for("login"))

admin = Admin(app, index_view=MyAdminIndexView())

admin.add_view(MyModelView(Users, db.session))
admin.add_view(MyModelView(StudentsQuestions, db.session))
admin.add_view(MyModelView(TeachersReply, db.session))
admin.add_view(MyModelView(Files, db.session))
admin.add_view(DocumentaionView(name="Documentation", endpoint="documentation"))