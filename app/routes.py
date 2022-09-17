from app import app,db
from flask import render_template, flash, redirect, url_for, request, jsonify
from flask_login import current_user, login_user,login_required,logout_user
from app.models import User, Session, Participant, Response
from werkzeug.urls import url_parse
from app.forms import SignupForm, LoginForm, ResetPasswordForm, ResetPasswordRequestForm
from sqlalchemy import func 
from app.api.errors import bad_request
from app.email import send_password_reset_email

import json


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
        if current_user.email == "emotionappmoodtrack@gmail.com":
            return redirect(url_for('viewusers'))
        return render_template("createsession.html", title='Create Session', is_create=True)
    else:
        userId = current_user.id
        data = request.get_json() or {}
        # Check data
        if 'sessionTitle' not in data or 'consent' not in data or 'emotions' not in data or 'preQuestions' not in data or 'postQuestions' not in data:
            return bad_request('Must include consent, emotions, preQuestions and postQuestions')

        # Insert into session table
        session = Session(
            user_id=userId,
            published=False,
            session_title=data['sessionTitle'],
            consent=data['consent'],
            emotions=data['emotions'],
            intensity =data['intensity'],
            pre_ques=data['preQuestions'],
            post_ques=data['postQuestions'])
        db.session.add(session)
        db.session.commit()

        # Return response
        response = jsonify(session.to_dict())
        response.status_code = 201 
        response.headers['Location'] = url_for('createsession')
        return response


# View Sessions
#----------------------------------------------------------
@app.route('/viewsessions', methods=['GET'])
@login_required
def viewsessions():
    if current_user.email == "emotionappmoodtrack@gmail.com":
        sessions = db.session.query(Session, User).filter(Session.user_id == User.id).all()
        return render_template("superadmin_viewsession.html", title='View Session', is_view=True, sessions = sessions)
    userId = current_user.id
    sessions = Session.query.filter_by(user_id = userId).all()
    return render_template("viewsession.html", title='View Session', is_view=True, sessions = sessions)


# View Users
#----------------------------------------------------------
@app.route('/viewusers', methods=['GET'])
@login_required
def viewusers():
    sessions = Session.query.all()
    users = User.query.all()
    return render_template("viewusers.html", title="View Users", is_viewuser = True, sessions = sessions, users = users)



# Publish Session
#----------------------------------------------------------
@app.route('/publishsession', methods=['POST'])
@login_required
def publishsession():
    userId = current_user.id
    data = request.get_json() or {}
    session = Session.query.filter_by(id = data['sessionId']).first()

    # Return error if session doesn't exist or user is deleting other user's session 
    if not session:
        return bad_request('Session',data['sessionId'], "doesn't exists")

    if session.user_id != userId:
        return bad_request("Unauthorised action")
    
    # Publish the session
    session.published = True
    db.session.commit()

    # Return success
    response = jsonify(success=True)
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
            email=form.email.data.lower(), reason=form.reason.data, approved=False)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, your signup have been requested!')
        return redirect(url_for('login'))
    return render_template('signup.html', title='Sign up', form=form, is_signup=True, test ='pass')

# Login/Sign In
#----------------------------------------------------------
@app.route('/')
@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('createsession'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data.lower()).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        login_user(user, remember=True)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('createsession')
        return redirect(next_page)
    return render_template('login.html', title='Login', form=form, is_signin=True)

# Logout
#----------------------------------------------------------
@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('createsession'))


# Reset Password
#----------------------------------------------------------
@app.route('/reset_password_request', methods=['GET', 'POST'])
def reset_password_request():
    if current_user.is_authenticated:
        return redirect(url_for('login'))
    form = ResetPasswordRequestForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data.lower()).first()
        if user:
            send_password_reset_email(user)
        flash("Check your email for the instructions to reset your password. If you couldn't find the email in your inbox, please check your spam/junk folder ")
        return redirect(url_for('login'))
    return render_template('reset_password_request.html', title='Reset Password', form=form)


@app.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for('createsession'))
    user = User.verify_reset_password_token(token)
    if not user:
        return redirect(url_for('login'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        user.set_password(form.password.data)
        db.session.commit()
        flash('Your password has been reset.')
        return redirect(url_for('login'))
    return render_template('reset_password.html', form=form)


# Get Session homepage
#----------------------------------------------------------
@app.route('/session/<int:sessionid>', methods=['GET','POST'])
def session_home(sessionid):
        session = Session.query.filter_by(id = sessionid).first_or_404()
        return render_template('session.html', title='Session', session = session)


# Get new participant ID
#----------------------------------------------------------
@app.route('/session/<int:sessionid>/getid', methods=['GET'])
def get_participant_id(sessionid):
    participant = Participant(
    stage_num = 1,
    session_id = sessionid)

    db.session.add(participant)
    db.session.commit()
    return(str(participant.id))


    # else:
    #     data = request.get_json() or {}

    #     if 'participantId' not in data:
    #         participantId = 0
    #         # Assign a new participantId
    #         lastParticipant = Participant.query.order_by(id.desc()).first()
    #         if lastParticipant is not None:
    #             participantId = lastParticipant.id + 1
            
    #         participant = Participant(
    #         id = participantId,
    #         stage_num = 0,
    #         session_id = sessionid)

    #         db.session.add(participant)
    #         db.session.commit()
    #         return redirect(url_for(f'/session/{sessionid}/{participantId}'))

    #     else:
    #         participantId = data["participantId"]
            
    #     db.session.add(session)
    #     db.session.commit()

@app.route('/session/<int:sessionid>/<int:participantid>', methods=['GET','POST'])
def session(sessionid,participantid):
    participant = Participant.query.filter_by(id=participantid).first_or_404()
    session = Session.query.filter_by(id = sessionid).first_or_404()
    stage_num = participant.stage_num

    if request.method == 'GET':
        if stage_num == 1:
            return render_template("session_124.html", session = session, participant = participant, stage=1)
        elif stage_num == 2:
            return render_template("session_124.html", session = session, participant = participant, stage=2)
        elif stage_num == 3:
            return render_template("session_3.html", session = session, participant = participant, stage=3)
        elif stage_num == 4:
            return render_template("session_124.html", session = session, participant = participant, stage=4)
        else:
            return render_template("session_5.html", session = session, participant = participant, stage=5)
    
    else:
        data = request.get_json() or {}
        if 'stage' not in data:
            return bad_request('Must include stage number')

        if data['stage'] == 1 and data['consent']:
            participant.stage_num = 2
            db.session.commit()
            return ('Successfully recorded consent')

        elif data['stage'] == 2:
            if 'ans' not in data:
                return bad_request('Must include ans')
            participant.pre_ques_ans = data['ans']
            participant.stage_num = 3
            db.session.commit()
            return ('Successfully recorded answers for pre-session questions')

        elif data['stage'] == 3:
            if 'emotions' not in data:
                return bad_request('Must include emotions and endStage')
            
            # Add each emotion response to database
            for emotion in data['emotions']:
                response = Response(
                emotion = emotion,
                intensity = data['emotions'][emotion],
                participant_id = participant.id,
                session_id = session.id)
                db.session.add(response)

            if data['endStage']:
                participant.stage_num = 4
            
            db.session.commit()
            return ('Successfully recorded emotions response')

        elif data['stage'] == 4:
            if 'ans' not in data:
                return bad_request('Must include ans')
            participant.post_ques_ans = data['ans']
            participant.stage_num = 5
            db.session.commit()
            return ('Successfully recorded answers for post-session questions')
        
        else:
            return 'Error: No operation is done'
        
        

# Delete Session
#----------------------------------------------------------------
@app.route('/deleteSession', methods =['post'])
def deleteSession():
    temp = request.get_json()
    selectedId = json.loads(temp)
    
    target = Session.query.get(selectedId)
    db.session.delete(target)
    db.session.commit()
    
    return redirect(url_for('viewsessions'))

# Edit Session
#---------------------------------------------------------------
@app.route('/editSession/<int:id>', methods= ['GET', 'POST'])
def editSession(id):
    session = Session.query.get(id)
    return render_template('editsession.html', session = session,edit = True)

# Update Session
#----------------------------------------------------------------
@app.route('/updateSession', methods = ['POST'])
def updateSession():
    #getting json data
    jsonData = request.get_json()
    newData = json.loads(jsonData)
    
    #retrieving specific session
    selectedSession = newData['id']
    session = Session.query.get(selectedSession)
    
    #updating session
    session.session_title = newData['sessionTitle']
    session.consent = newData['consent']
    session.emotions = newData['emotions']
    session.intensity = newData['intensity']
    session.pre_ques = newData['preQuestions']
    session.post_ques = newData['postQuestions']
    db.session.commit()
    
    
    return redirect(url_for('viewsessions'))