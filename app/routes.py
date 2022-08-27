from app import app,db
from flask import render_template, flash, redirect, url_for, request, jsonify
from flask_login import current_user, login_user,login_required,logout_user
from app.models import User, Session, Participant, Response
from werkzeug.urls import url_parse
from app.forms import SignupForm, LoginForm
from sqlalchemy import func 
from app.api.errors import bad_request


@app.route('/user')
@login_required
def user():
    return render_template("user.html", title='Home Page')

# Session Creation
#----------------------------------------------------------
# POST REQUEST JSON DATA FORMAT
# {sessionTitle:'',consent:'',preQuestions:['',''],emotions:'',intensity:'',postQuestions:['','']}
#----------------------------------------------------------
@app.route('/createsession', methods=['GET', 'POST'])
@login_required
def createsession():
    if request.method == 'GET':
        return render_template("createsession.html", title='Create Session')
    else:
        userId = current_user.id
        data = request.get_json() or {}
        # Check data
        if 'sessionTitle' not in data or 'consent' not in data or 'emotions' not in data or 'preQuestions' not in data or 'postQuestions' not in data:
            return bad_request('Must include consent, emotions, preQuestions and postQuestions')

        # Insert into session table
        sessionid = 0
        lastSession = Session.query.order_by(Session.id.desc()).first()
        if lastSession is not None:
            sessionid = lastSession.id + 1
        session = Session(id=sessionid,published=False,session_title=data['sessionTitle'],consent=data['consent'],emotions=data['emotions'],user_id=userId,pre_ques=data['preQuestions'],post_ques=data['postQuestions'])
        db.session.add(session)
        db.session.commit()

        # Return response
        response = jsonify(session.to_dict())
        response.status_code = 201 
        response.headers['Location'] = url_for('createsession')
        return response

# Signup
#----------------------------------------------------------
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if current_user.is_authenticated:
        return redirect(url_for('createsession'))
    form = SignupForm()
    if form.validate_on_submit():
        user = User(fist_name=form.firstname.data, last_name=form.lastname.data, username=form.username.data, orcid=form.orcid.data, institution=form.institution.data, \
            email=form.email.data, reason=form.reason.data, approved=False)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, your signup have been requested!')
        return redirect(url_for('login'))
    return render_template('signup.html', title='Sign up', form=form)

# Login 
#----------------------------------------------------------
@app.route('/')
@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('createsession'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        login_user(user, remember=True)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('createsession')
        return redirect(next_page)
    return render_template('login.html', title='Login', form=form)

# Logout
#----------------------------------------------------------
@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('login'))