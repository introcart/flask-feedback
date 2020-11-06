from flask import Flask, render_template, redirect, session, flash
from flask_debugtoolbar import DebugToolbarExtension
from models import connect_db, db, User, Feedback
from forms import RegisterForm, LoginForm, FeedbackForm

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "postgres:///feedback_db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_ECHO"] = True
app.config["SECRET_KEY"] = "abc123"
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False

connect_db(app)

toolbar = DebugToolbarExtension(app)

@app.route('/')
def home():
    return redirect('/register')

@app.route('/register', methods=['GET', 'POST'])
def show_registration():
    form = RegisterForm()
    if form.validate_on_submit():
        username = form.username.data 
        password = form.password.data 
        email = form.email.data
        first_name = form.first_name.data  
        last_name = form.last_name.data 
        new_user = User.register(username, password, email, first_name, last_name)    

        db.session.add(new_user)
        db.session.commit()
        session['username'] = new_user.username
        flash('Welcome! Successfully Created Your Account', "success")
        return redirect(f'/users/{new_user.username}')
    return render_template('register.html', form=form)

@app.route('/users/<username>')
def show_secret(username):
    if "username" not in session:
        flash("Please login first!", "danger")
        return redirect('/')
    user = User.query.get(username)
    feedbacks = Feedback.query.filter_by(username=username).all()
    return render_template('secret.html', user=user, feedbacks=feedbacks)

@app.route('/login', methods=['GET', 'POST'])
def login_user():
    form = LoginForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data

        user = User.authenticate(username, password)
        if user:
            flash(f"Welcome Back, {user.username}", "primary")
            session['username'] = user.username
            return redirect(f'/users/{user.username}')
        else:
            form.username.errors = ['Invalid username/password.']
    return render_template('login.html', form=form)

@app.route('/logout')
def logout_user():
    session.pop('username')
    flash('Goodbye', "info")
    return redirect('/')

@app.route('/users/<username>/feedback/add', methods=["POST", "GET"])
def add_feedback(username):
    if 'username' not in session:
        flash("Please login first!", "danger")
        return redirect('/')
    form = FeedbackForm()
    if form.validate_on_submit():
        title = form.title.data
        content = form.content.data
        fb = Feedback(title=title,content=content,username=session["username"])
        db.session.add(fb)
        db.session.commit()
        flash('Feedback Added!', "success")
        return redirect(f'/users/{username}')
    return render_template('add_feedback.html', form=form)

@app.route('/feedback/<int:id>/update', methods=["POST", "GET"])
def update_feedback(id):
        if 'username' not in session:
            flash("Please login first!", "danger")
            return redirect('/')
        fb = Feedback.query.get_or_404(id)
        form = FeedbackForm(obj=fb)

        if form.validate_on_submit():
            fb.title = form.title.data
            fb.content = form.content.data   
            db.session.commit()
            flash('Feedback Updated', "primary")
            return redirect(f"/users/{fb.user.username}")
        else:
            return render_template("add_feedback.html", form=form)

@app.route('/feedback/<int:id>/delete', methods=["POST"])
def delete_feedback(id):
        if 'username' not in session:
            flash("Please login first!", "danger")
            return redirect('/')
        fb = Feedback.query.get_or_404(id)
        username = fb.user.username
        Feedback.query.filter_by(id=id).delete()
        db.session.commit()
        return redirect(f'/users/{username}')

