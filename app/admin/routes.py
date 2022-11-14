from app import db
from app.admin import bp
from flask import render_template, flash, redirect, url_for, request, jsonify
from flask_login import current_user, login_user,login_required,logout_user
from app.models import User, Session, Participant, Response
from werkzeug.urls import url_parse
from app.api.errors import bad_request
from app.auth.email import send_password_reset_email, send_sign_up_req_email, send_req_result_email
import flask_excel as excel
import json


# Session Creation
#----------------------------------------------------------
# POST REQUEST JSON DATA FORMAT
# {sessionTitle:'',consent:'',preQuestions:['',''],emotions:'',intensity:'',postQuestions:['','']}
#----------------------------------------------------------
@bp.route('/createsession', methods=['GET', 'POST'])
@login_required
def createsession():
    if request.method == 'GET':
        if current_user.email == "emotionapp2022@gmail.com":
            return redirect(url_for('admin.viewusers'))
        return render_template("admin/createsession.html", title='Create Session', is_create=True)
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
        return "Successully created session"


# View Sessions
#----------------------------------------------------------
@bp.route('/viewsessions', methods=['GET'])
@login_required
def viewsessions():
    if current_user.email == "emotionapp2022@gmail.com":
        sessions = db.session.query(Session, User).filter(Session.user_id == User.id).all()
        return render_template("admin/superadmin_viewsession.html", title='View Sessions', is_view=True, sessions = sessions, is_superadmin=True)
    userId = current_user.id
    sessions = Session.query.filter_by(user_id = userId).all()
    return render_template("admin/viewsession.html", title='View Sessions', is_view=True, sessions = sessions)


# View a Session 
#----------------------------------------------------------
@bp.route('/viewsession/<int:sessionid>', methods=['GET'])
@login_required
def viewSession(sessionid):
    session = Session.query.filter_by(id=sessionid).first_or_404()

    # Restrict access to superadmin and creator of the current session only
    if current_user.email != "emotionapp2022@gmail.com" and session.user_id != current_user.id:
        return render_template("errors/404.html")
    
    participants = Participant.query.filter_by(session_id = session.id).all()
    if current_user.email == "emotionapp2022@gmail.com":
        return render_template("admin/viewresult.html", title='View Participant Results', is_view=True, session = session, participants = participants, is_superadmin=True)
    else:
        return render_template("admin/viewresult.html", title='View Participant Results', is_view=True, session = session, participants = participants)


# Download a participant result
#----------------------------------------------------------
@bp.route("/download/<int:sessionid>/<int:participantid>", methods=['GET'])
def downloadFile(sessionid, participantid):
    session = Session.query.filter_by(id=sessionid).first_or_404()

    # Restrict access to superadmin and creator of the current session only
    if current_user.email != "emotionapp2022@gmail.com" and session.user_id != current_user.id:
        return render_template("errors/404.html")
    
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
    for i in range(len(postques)+ 2):
        if i == 0:
            result.append(['Please comment on your highest frequency emotion(s).', postans[i]])
        elif i ==1: 
            result.append(['Please comment on your highest intensity emotion(s).', postans[i]])
        else:
            result.append([postques[i-2],postans[i]])

    return excel.make_response_from_array(result, "xlsx", file_name=f"participant{participant.id} result")


# Bulk download participant results (Questions)
#----------------------------------------------------------
@bp.route("/download/ans/<int:sessionid>", methods=['GET'])
def bulkDownloadAns(sessionid):
    session = Session.query.filter_by(id=sessionid).first_or_404()

    # Restrict access to superadmin and creator of the current session only
    if current_user.email != "emotionapp2022@gmail.com" and session.user_id != current_user.id:
        return render_template("errors/404.html")

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
                if i ==0:
                    result.append(['Please comment on your highest frequency emotion(s).', postans[i],participant.id])
                elif i == 1:
                    result.append(['Please comment on your highest intensity emotion(s).', postans[i],participant.id])
                else:
                    result.append([postques[i-2],postans[i],participant.id])

    return excel.make_response_from_array(result, "xlsx", file_name="Bulk Results (Questions)")


# Bulk download participant results (Emotions)
#----------------------------------------------------------
@bp.route("/download/emotions/<int:sessionid>", methods=['GET'])
def bulkDownloadEmotions(sessionid):
    session = Session.query.filter_by(id=sessionid).first_or_404()

    # Restrict access to superadmin and creator of the current session only
    if current_user.email != "emotionapp2022@gmail.com" and session.user_id != current_user.id:
        return render_template("errors/404.html")

    result = [['Timestamp','Emotion','Intensity','Participant ID']]

    responses = Response.query.filter_by(session_id=sessionid).all()
    for response in responses:
        result.append([response.timestamp,response.emotion,response.intensity,response.participant_id])

    return excel.make_response_from_array(result, "xlsx", file_name="Bulk Results (Emotions)")


# Delete participant results (Emotions)
# '{sessionid:<sessionid>,particiapntid:<participantid>}'
#----------------------------------------------------------
@bp.route('/deleteresult', methods =['post'])
def deleteResult():
    temp = request.get_json()
    data = json.loads(temp)
    sessionId = data['sessionid']
    participantid = data['participantid']
    session = Session.query.filter_by(id=sessionId).first_or_404()

    # Restrict access to superadmin and creator of the current session only
    if current_user.email != "emotionapp2022@gmail.com" and session.user_id != current_user.id:
        return bad_request("Action not allowed")

    # delete participants of the session from participant table
    delete_p = Participant.__table__.delete().where(Participant.id ==participantid)
    db.session.execute(delete_p)

    # delete response of the session from response table
    delete_r = Response.__table__.delete().where(Response.participant_id == participantid)
    db.session.execute(delete_r)

    db.session.commit()
    
    return('success')

# About us
#----------------------------------------------------------
@bp.route('/aboutus', methods =['GET'])
@login_required
def aboutus():
    if current_user.email == "emotionapp2022@gmail.com":
        return render_template("admin/aboutus.html", title='About Us', is_aboutus =True,is_superadmin=True)
    else:
        return render_template("admin/aboutus.html", title='About Us', is_aboutus =True)

# View Users
#----------------------------------------------------------
@bp.route('/viewusers', methods=['GET'])
@login_required
def viewusers():
    if current_user.email == "emotionapp2022@gmail.com":
        sessions = Session.query.all()
        users = User.query.all()
        admin = current_user
        return render_template("admin/viewusers.html", title="View Users", is_viewuser = True, admin = admin, sessions = sessions, users = users, is_superadmin=True)
    else:
        return render_template("errors/404.html")

# Sign up requests
#----------------------------------------------------------
@bp.route('/signupreq', methods=['GET'])
@login_required
def signupreq():
    if current_user.email == "emotionapp2022@gmail.com":
        users = User.query.all()
        return render_template("admin/approve_users.html", title="Sign Up Requests", is_superadmin = True, is_signupreq = True, users = users)
    else:
        return render_template("errors/404.html")


# Publish Session
#----------------------------------------------------------
@bp.route('/publishsession', methods=['POST'])
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
    return "Successfully published session"


# Delete Session
#----------------------------------------------------------------
@bp.route('/deleteSession', methods =['post'])
def deleteSession():
    temp = request.get_json()
    selectedId = json.loads(temp)
    session = Session.query.filter_by(id=selectedId).first_or_404()

    # Restrict access to superadmin and creator of the current session only
    if current_user.email != "emotionapp2022@gmail.com" and session.user_id != current_user.id:
        return bad_request("Action not allowed")

    # delete session from session table
    target = Session.query.get(selectedId)
    db.session.delete(target)

    # delete response of the session from response table
    delete_r = Response.__table__.delete().where(Response.session_id == selectedId)
    db.session.execute(delete_r)


    # delete participants of the session from participant table
    delete_p = Participant.__table__.delete().where(Participant.session_id == selectedId)
    db.session.execute(delete_p)

    
    db.session.commit()
    
    return('success')


# Edit Session
#---------------------------------------------------------------
@bp.route('/editSession/<int:id>', methods= ['GET', 'POST'])
def editSession(id):
    session = Session.query.get(id)
    return render_template('admin/editsession.html', session = session,edit = True)


# Update Session
#----------------------------------------------------------------
@bp.route('/updateSession', methods = ['POST'])
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
    
    return redirect(url_for('admin.viewsessions'))


# Copy Session
#---------------------------------------------------------------
@bp.route('/copySession/<int:id>', methods= ['GET', 'POST'])
def copySession(id):
    session = Session.query.get(id)
    return render_template('admin/editsession.html', session = session, is_create=True)



# Superadmin delete user and all sessions created by that user
#----------------------------------------------------------
@bp.route('/deleteUser', methods=['GET','POST'])
@login_required
def deleteUser():
    temp = request.get_json()
    selectedUserId = json.loads(temp)

    # Restrict access to superadmin only
    if current_user.email != "emotionapp2022@gmail.com":
        return bad_request("Action not allowed")

    sessions = Session.query.filter_by(user_id = selectedUserId).all()
    for session in sessions:
        sessionId = session.id
        
        # delete response of the session from response table
        delete_r = Response.__table__.delete().where(Response.session_id == sessionId)
        db.session.execute(delete_r)
        
        # delete participants of the session from participant table
        delete_p = Participant.__table__.delete().where(Participant.session_id == sessionId)
        db.session.execute(delete_p)

    
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
@bp.route('/denyUser', methods=['GET','POST'])
@login_required
def denyUser():
    temp = request.get_json()
    userId = json.loads(temp)

    # Restrict access to superadmin only
    if current_user.email != "emotionapp2022@gmail.com":
        return bad_request("Action not allowed")
    
    # email sign up review results to user
    user = User.query.get(userId)
    send_req_result_email(user, results=False)

    # delete user in database
    target = User.query.get(userId)
    db.session.delete(target)
    db.session.commit()
    
    return redirect(url_for('admin.signupreq'))



# Superadmin approve user sign up requests
#----------------------------------------------------------
@bp.route('/approveUser', methods=['GET','POST'])
@login_required
def approveUser():
    temp = request.get_json()
    userId = json.loads(temp)

    # Restrict access to superadmin only
    if current_user.email != "emotionapp2022@gmail.com":
        return bad_request("Action not allowed")
    
    # email sign up review results to user
    user = User.query.get(userId)
    send_req_result_email(user, results=True)

    # approve user
    target = User.query.get(userId)
    target.approved = True
    db.session.commit()
    
    return redirect(url_for('admin.signupreq'))