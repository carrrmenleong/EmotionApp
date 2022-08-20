from app import app,db
from flask import render_template, flash, redirect, url_for, request
from flask_login import current_user, login_user,login_required
from app.models import User
from werkzeug.urls import url_parse
from app.forms import SignupForm, LoginForm


@app.route('/user')
@login_required
def user():
    return render_template("user.html", title='Home Page')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if current_user.is_authenticated:
        return redirect(url_for('user'))
    form = SignupForm()
    if form.validate_on_submit():
        user = User(fist_name=form.firstname.data, last_name=form.lastname.data, username=form.username.data, orcid=form.orcid.data, institution=form.institution.data, \
            email=form.email.data, reason=form.reaon.data, approved=False)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, your signup have been requested!')
        return redirect(url_for('login'))
    return render_template('signup.html', title='Login', form=form)

@app.route('/')
@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('user'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('user')
        return redirect(next_page)
    return render_template('login.html',title='Login', form=form)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('login'))