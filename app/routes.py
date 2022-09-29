from app import app,db
from flask import render_template, flash, redirect, url_for, request, jsonify
from flask_login import current_user, login_user,login_required,logout_user
from app.models import User, Session, Participant, Response
from werkzeug.urls import url_parse
from app.forms import SignupForm, LoginForm, ResetPasswordForm, ResetPasswordRequestForm
from sqlalchemy import func 
from app.api.errors import bad_request
from app.email import send_password_reset_email, send_sign_up_req_email, send_req_result_email
import flask_excel as excel

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
        return render_template("superadmin_viewsession.html", title='View Session', is_view=True, sessions = sessions, is_superadmin=True)
    userId = current_user.id
    sessions = Session.query.filter_by(user_id = userId).all()
    return render_template("viewsession.html", title='View Session', is_view=True, sessions = sessions)


# View a Session 
#----------------------------------------------------------
@app.route('/viewsession/<int:sessionid>', methods=['GET'])
@login_required
def viewSession(sessionid):
    session = Session.query.filter_by(id=sessionid).first_or_404()

    # Restrict access to superadmin and creator of the current session only
    if current_user.email != "emotionappmoodtrack@gmail.com" and session.user_id != current_user.id:
        return render_template("404.html")
    
    participants = Participant.query.filter_by(session_id = session.id).all()
    if current_user.email == "emotionappmoodtrack@gmail.com":
        return render_template("viewresult.html", title='View Participants Results', is_view=True, session = session, participants = participants, is_superadmin=True)
    else:
        return render_template("viewresult.html", title='View Participants Results', is_view=True, session = session, participants = participants)


# Download a participant result
#----------------------------------------------------------
@app.route("/download/<int:sessionid>/<int:participantid>", methods=['GET'])
def downloadFile(sessionid, participantid):
    session = Session.query.filter_by(id=sessionid).first_or_404()

    # Restrict access to superadmin and creator of the current session only
    if current_user.email != "emotionappmoodtrack@gmail.com" and session.user_id != current_user.id:
        return render_template("404.html")
    
    participant = Participant.query.filter_by(id = participantid).first_or_404()

    # Throw error if participant hasn't complete the session survey
    if participant.stage_num != 5:
        return bad_request("Participant hasn't complete the session survey")

    responses = Response.query.filter_by(participant_id = participant.id).all()
    result = [['Questions','Answer']]
    preques = json.loads(session.pre_ques)
    preans = participant.pre_ques_ans
    postques = json.loads(session.post_ques)
    postans = participant.post_ques_ans

    for i in range(len(preques)):
        result.append([preques[i],preans[i]])
    
    result.append([])
    result.append(['Timestamp','Emotion','Intensity'])

    for r in responses:
        result.append([r.timestamp,r.emotion,r.intensity])

    result.append([])
    result.append(['Questions','Answer'])
    for i in range(len(postques)):
        result.append([postques[i],postans[i]])

    return excel.make_response_from_array(result, "csv", file_name=f"participant{participant.id} result")


# Bulk download participant results (Questions)
#----------------------------------------------------------
@app.route("/download/ans/<int:sessionid>", methods=['GET'])
def bulkDownloadAns(sessionid):
    session = Session.query.filter_by(id=sessionid).first_or_404()

    # Restrict access to superadmin and creator of the current session only
    if current_user.email != "emotionappmoodtrack@gmail.com" and session.user_id != current_user.id:
        return render_template("404.html")

    preques = json.loads(session.pre_ques)
    postques = json.loads(session.post_ques)
    participants = Participant.query.filter_by(session_id = sessionid).all()

    result = [['Question','Answer','Participant ID']]

    for participant in participants:
        preans = participant.pre_ques_ans
        if participant.stage_num == 5:
            for i in range(len(preques)):
                result.append([preques[i],preans[i],participant.id])
    
    result.append([])

    for participant in participants:
        postans = participant.post_ques_ans
        if participant.stage_num == 5:
            for i in range(len(postans)):
                result.append([postques[i],postans[i],participant.id])

    return excel.make_response_from_array(result, "csv", file_name="Bulk Results (Questions)")


# Bulk download participant results (Emotions)
#----------------------------------------------------------
@app.route("/download/emotions/<int:sessionid>", methods=['GET'])
def bulkDownloadEmotions(sessionid):
    session = Session.query.filter_by(id=sessionid).first_or_404()

    # Restrict access to superadmin and creator of the current session only
    if current_user.email != "emotionappmoodtrack@gmail.com" and session.user_id != current_user.id:
        return render_template("404.html")

    result = [['Timestamp','Emotion','Intensity','Participant ID']]

    responses = Response.query.filter_by(session_id=sessionid).all()
    for response in responses:
        result.append([response.timestamp,response.emotion,response.intensity,response.participant_id])

    return excel.make_response_from_array(result, "csv", file_name="Bulk Results (Emotions)")


# Delete participant results (Emotions)
# '{sessionid:<sessionid>,particiapntid:<participantid>}'
#----------------------------------------------------------
@app.route('/deleteresult', methods =['post'])
def deleteResult():
    temp = request.get_json()
    data = json.loads(temp)
    sessionId = data['sessionid']
    participantid = data['participantid']
    session = Session.query.filter_by(id=sessionId).first_or_404()

    # Restrict access to superadmin and creator of the current session only
    if current_user.email != "emotionappmoodtrack@gmail.com" and session.user_id != current_user.id:
        return bad_request("Action not allowed")

    # delete participants of the session from participant table
    delete_p = Participant.__table__.delete().where(Participant.id ==participantid)
    db.session.execute(delete_p)

    # delete response of the session from response table
    delete_r = Response.__table__.delete().where(Response.participant_id == participantid)
    db.session.execute(delete_r)

    db.session.commit()
    
    return('success')


# View Users
#----------------------------------------------------------
@app.route('/viewusers', methods=['GET'])
@login_required
def viewusers():
    if current_user.email == "emotionappmoodtrack@gmail.com":
        sessions = Session.query.all()
        users = User.query.all()
        admin = current_user
        return render_template("viewusers.html", title="View Users", is_viewuser = True, admin = admin, sessions = sessions, users = users, is_superadmin=True)
    else:
        return render_template("404.html")

# Sign up requests
#----------------------------------------------------------
@app.route('/signupreq', methods=['GET'])
@login_required
def signupreq():
    if current_user.email == "emotionappmoodtrack@gmail.com":
        users = User.query.all()
        return render_template("approve_users.html", title="Sign Up Requests", is_superadmin = True, is_signupreq = True, users = users)
    else:
        return render_template("404.html")


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

        #email superadmin about new sign up request
        send_sign_up_req_email(user)
        
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
        if user.email == "emotionappmoodtrack@gmail.com":
             login_user(user, remember=True)
             next_page = request.args.get('next')
        if user.approved == False:
             flash('Your sign up request is pending approval.')
             return render_template('login.html', title='Login', form=form, is_signin=True)
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
        if not session.published:
            return render_template("404.html")
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


# Check if participant ID is valid
#----------------------------------------------------------
@app.route('/session/<int:sessionid>/<int:participantid>/checkid', methods=['GET'])
def check_id(sessionid,participantid):
    participant = Participant.query.filter_by(id=participantid).first()
    if participant:
        return('validId')
    else:
        return('invalidId')


# Get corresponding session page base on participant's stage, store participant response in databse
#----------------------------------------------------------
@app.route('/session/<int:sessionid>/<int:participantid>', methods=['GET','POST'])
def session(sessionid,participantid):
    participant = Participant.query.filter_by(id=participantid).first_or_404()
    session = Session.query.filter_by(id = sessionid).first_or_404()
    if participant is None:
        return bad_request("Participant Id doesn't exists")
    stage_num = participant.stage_num

    # Split consent
    consenttexts = session.consent.split('\n')
    emotions = session.emotions.split('\n')
    if request.method == 'GET':
        if stage_num == 1:
            return render_template("session_124.html", session = session, participant = participant, stage=1, consenttexts = consenttexts)
        elif stage_num == 2:
            return render_template("session_124.html", session = session, participant = participant, stage=2)
        elif stage_num == 3:
            return render_template("session_3.html", session = session, participant = participant, stage=3, emotions = emotions)
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
            
            if data['endStage']:
                participant.stage_num = 4
            else:
                # Add each emotion response to database
                for emotion in data['emotions']:
                    response = Response(
                    emotion = emotion,
                    intensity = data['emotions'][emotion],
                    participant_id = participant.id,
                    session_id = session.id)
                    db.session.add(response)
            
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
    session = Session.query.filter_by(id=selectedId).first_or_404()

    # Restrict access to superadmin and creator of the current session only
    if current_user.email != "emotionappmoodtrack@gmail.com" and session.user_id != current_user.id:
        return bad_request("Action not allowed")

    # delete session from session table
    target = Session.query.get(selectedId)
    db.session.delete(target)

    # delete participants of the session from participant table
    delete_p = Participant.__table__.delete().where(Participant.session_id == selectedId)
    db.session.execute(delete_p)

    # delete response of the session from response table
    delete_r = Response.__table__.delete().where(Response.session_id == selectedId)
    db.session.execute(delete_r)

    db.session.commit()
    
    return('success')


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


# Copy Session
#---------------------------------------------------------------
@app.route('/copySession/<int:id>', methods= ['GET', 'POST'])
def copySession(id):
    session = Session.query.get(id)
    return render_template('editsession.html', session = session, is_create=True)



# Superadmin delete user and all sessions created by that user
#----------------------------------------------------------
@app.route('/deleteUser', methods=['GET','POST'])
@login_required
def deleteUser():
    temp = request.get_json()
    selectedUserId = json.loads(temp)

    # Restrict access to superadmin only
    if current_user.email != "emotionappmoodtrack@gmail.com":
        return bad_request("Action not allowed")

    sessions = Session.query.filter_by(user_id = selectedUserId).all()
    for session in sessions:
        sessionId = session.id
        # delete participants of the session from participant table
        delete_p = Participant.__table__.delete().where(Participant.session_id == sessionId)
        db.session.execute(delete_p)

        # delete response of the session from response table
        delete_r = Response.__table__.delete().where(Response.session_id == sessionId)
        db.session.execute(delete_r)
    
    # delete sessions created by the user
    delete_s = Session.__table__.delete().where(Session.user_id == selectedUserId)
    db.session.execute(delete_s)

    # delete user from user table
    target = User.query.get(selectedUserId)
    db.session.delete(target)

    db.session.commit()
    return ('success')


# Superadmin deny user sign up requests
#----------------------------------------------------------
@app.route('/denyUser', methods=['GET','POST'])
@login_required
def denyUser():
    temp = request.get_json()
    userId = json.loads(temp)

    # Restrict access to superadmin only
    if current_user.email != "emotionappmoodtrack@gmail.com":
        return bad_request("Action not allowed")
    
    # email sign up review results to user
    user = User.query.get(userId)
    send_req_result_email(user, results=False)

    # delete user in database
    target = User.query.get(userId)
    db.session.delete(target)
    db.session.commit()
    
    return redirect(url_for('signupreq'))



# Superadmin approve user sign up requests
#----------------------------------------------------------
@app.route('/approveUser', methods=['GET','POST'])
@login_required
def approveUser():
    temp = request.get_json()
    userId = json.loads(temp)

    # Restrict access to superadmin only
    if current_user.email != "emotionappmoodtrack@gmail.com":
        return bad_request("Action not allowed")
    
    # email sign up review results to user
    user = User.query.get(userId)
    send_req_result_email(user, results=True)

    # approve user
    target = User.query.get(userId)
    target.approved = True
    db.session.commit()
    
    return redirect(url_for('signupreq'))