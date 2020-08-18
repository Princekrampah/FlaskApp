import os
import secrets
from application import app, bcrypt,db
from application.models import Users, Files, StudentsQuestions, TeachersReply
from flask import render_template,url_for, redirect, flash, request, abort
from flask_login import login_user, current_user,logout_user,login_required
from application.forms import RegistrationForm, LoginForm, TeacherPostForm, StudentQuestionForm

@app.route("/", methods=["POST", "GET"])
@app.route("/home")
def first_page():
    if current_user.is_authenticated:
        return redirect("logout")
    return render_template("home.html")


@app.route("/register", methods=["POST", "GET"])
def student_register():
    if current_user.is_authenticated:
        return redirect("content_page")
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_pwd = bcrypt.generate_password_hash(form.password.data).decode("utf-8")
        newStudent = Users(username = form.username.data, password = hashed_pwd, Class = form.Class.data, is_admin = False)
        db.session.add(newStudent)
        db.session.commit()
        flash("Account Created, You can now login", "success")
        return redirect(url_for('login'))
    return render_template("register.html", title = "Registration", form=form)




@app.route("/login", methods=["POST", "GET"])
def login():
    if current_user.is_authenticated:
        return redirect("content_page")
    form = LoginForm()
    if form.validate_on_submit():
        user = Users.query.filter_by(username = form.username.data).first()
        if(user and bcrypt.check_password_hash(user.password, form.password.data)):
            login_user(user)
            next_page = request.args.get("next")
            return redirect(next_page) if next_page else redirect("content_page")
        else:
            flash("Login unsuccessful, please check username and password.", "danger")
    return render_template("login.html", title = "login", form = form)


@app.route("/logout")
def logout():
    logout_user()
    return redirect("home")


@app.route("/content_page")
@login_required
def content_page():
    page = request.args.get('page', 1, type=int)
    posts = Files.query.order_by(Files.date_uploaded.desc()).paginate(per_page = 2, page=page)
    return render_template("content_page.html", title = "main", posts = posts)


def fileProcessor(fileName):
    random_hex = secrets.token_hex(10)
    _,  f_ext = os.path.splitext(fileName.filename)
    new_name = random_hex + f_ext.lower()
    location_name = os.path.join(app.root_path, 'static/pdf_files/', new_name)
    fileName.save(location_name)
    return new_name

@app.route("/teacher_post", methods=["POST", "GET"])
@login_required
def teacher_post():
    form = TeacherPostForm()
    if form.validate_on_submit():
        myfile = fileProcessor(form.content_file.data)
        files = Files(title=form.title.data, instructions=form.instructions.data, Class=form.Class.data, file_name=myfile, post_author=current_user.id)
        db.session.add(files)
        db.session.commit()
        flash("File successfully uploaded!", "success")
        return redirect("content_page")
    return render_template("teacher_post.html", title = "teacher_post", form = form)


@app.route("/student_question<int:post_id>", methods=["POST", "GET"])
@login_required
def student_question(post_id):
    form_title = "This question will be sent to the teacher who made this post."
    legend = "Ask for clarifications"
    post = Files.query.get_or_404(int(post_id))
    form = StudentQuestionForm()
    if form.validate_on_submit():
        new_student_post = StudentsQuestions(content = form.content.data, target = post.author.username, student = current_user.username, Class = current_user.Class, title = post.title)
        db.session.add(new_student_post)
        db.session.commit()
        flash("Clarification request sent, please check in the reply page for a responds.", "info")
        return redirect("content_page")
    return render_template("student_question.html", form = form, post = post, form_title=form_title, legend=legend)

@app.route("/specific_students_questions")
@login_required
def specific_students_questions():
    page = request.args.get('page', 1, type=int)
    posts = StudentsQuestions.query.filter_by(student = current_user.username)
    view_status(posts)
    posts = posts.order_by(StudentsQuestions.date_uploaded.desc()).paginate(per_page=2, page=page)
    return render_template("specific_students_questions.html",posts = posts, db = db)

# display students questions to the teacher
@app.route("/teacher_questions_view")
@login_required
def teacher_questions_view():
    page = request.args.get('page', 1, type=int)
    posts = StudentsQuestions.query.filter_by(target = current_user.username)
    view_status(posts)
    posts = posts.order_by(StudentsQuestions.date_uploaded.desc()).paginate(per_page=2, page=page)
    return render_template("teachers_view_questions.html",posts = posts, db = db)


# from here onward the teacher is the student and the student is the teacher. take care
@app.route("/teacher_reply<int:post_id>", methods=["POST", "GET"])
@login_required
def teacher_reply(post_id):
    form_title = "This will be sent to the student who asked the question."
    legend = "Reply to students questions"
    post = StudentsQuestions.query.get_or_404(int(post_id))
    form = StudentQuestionForm()
    if form.validate_on_submit():
        new_student_post = TeachersReply(content = form.content.data, reply_author = current_user.username, target_student = post.student)
        db.session.add(new_student_post)
        db.session.commit()
        flash("Reply sent successfully", "info")
        return redirect("content_page")
    return render_template("student_question.html", form = form, post = post, form_title=form_title, legend=legend)

@app.route("/teachers_reply")
@login_required
def teachers_reply():
    page = request.args.get('page', 1, type=int)
    posts = TeachersReply.query.filter_by(reply_author = current_user.username)
    view_status(posts)
    posts = posts.order_by(TeachersReply.date_uploaded.desc()).paginate(per_page = 2, page=page)
    return render_template("teachers_reply.html",posts = posts, db = db)


@app.route("/students_reply")
@login_required
def students_reply():
    page = request.args.get('page', 1, type=int)
    posts = TeachersReply.query.filter_by(target_student = current_user.username)
    view_status(posts)
    posts = posts.order_by(TeachersReply.date_uploaded.desc()).paginate(per_page=2, page=page)
    return render_template("students_reply_view.html",posts = posts, db = db)



def view_status(posts):
    for post in posts:
        post.viewed_count = post.viewed_count + 1
        db.session.commit()
  
@app.route("/delete_post/<int:post_id>", methods=["POST"])
def delete_post(post_id):
    post = Files.query.get_or_404(int(post_id))
    if post.author != current_user:
        abort(403)
    db.session.delete(post)
    db.session.commit()
    flash("Post delete successfully!", "success")
    return redirect(url_for("content_page"))


@app.errorhandler(404)
def error_404(error):
    message = "OOPS!! The requested URL was not found on the server. If you entered the URL manually please check your spelling and try again.  Error 404"
    return render_template('error_pages.html', message = message)

@app.errorhandler(403)
def error_403(error):
    message = "The action performed is strictly prohibited on this site. Error 403"
    return render_template('error_pages.html', message = message)

@app.errorhandler(500)
def error_405(error):
    message = "OOPS!! internal server error occured.  Error 500"
    return render_template('error_pages.html', message = message)