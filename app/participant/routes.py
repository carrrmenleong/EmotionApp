from app import db
from flask import render_template, flash, redirect, url_for, request, jsonify
from app.models import User, Session, Participant, Response
from werkzeug.urls import url_parse
from app.api.errors import bad_request
from app.participant import bp


# Get Session homepage
#----------------------------------------------------------
@bp.route('/session/<int:sessionid>', methods=['GET','POST'])
def session_home(sessionid):
        session = Session.query.filter_by(id = sessionid).first_or_404()
        if not session.published:
            return render_template("errors/404.html")
        return render_template('participant/session.html', title='Session', session = session)


# Get new participant ID
#----------------------------------------------------------
@bp.route('/session/<int:sessionid>/getid', methods=['GET'])
def get_participant_id(sessionid):
    participant = Participant(
    stage_num = 1,
    session_id = sessionid)

    db.session.add(participant)
    db.session.commit()
    return(str(participant.id))


# Check if participant ID is valid
#----------------------------------------------------------
@bp.route('/session/<int:sessionid>/<int:participantid>/checkid', methods=['GET'])
def check_id(sessionid,participantid):
    participant = Participant.query.filter_by(id=participantid).first()
    if participant:
        return('validId')
    else:
        return('invalidId')


# Get corresponding session page base on participant's stage, store participant response in databse
#----------------------------------------------------------
@bp.route('/session/<int:sessionid>/<int:participantid>', methods=['GET','POST'])
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
            return render_template("participant/session_124.html", session = session, participant = participant, stage=1, consenttexts = consenttexts)
        elif stage_num == 2:
            return render_template("participant/session_124.html", session = session, participant = participant, stage=2)
        elif stage_num == 3:
            return render_template("participant/session_3.html", session = session, participant = participant, stage=3, emotions = emotions)
        elif stage_num == 4:
                        
            intensity_checker = {}
            emotion_checker = {}
            
            #filtering responses based on participant id
            temp = Response.query.filter_by(participant_id = participantid).all()
            
            
            for x in temp:
                #counting counts of emotions
                if x.emotion not in emotion_checker:
                    emotion_checker[x.emotion] = 1
                else:
                    emotion_checker[x.emotion] += 1
                #break down of scores for intensities
                if x.emotion not in intensity_checker:
                    intensity_checker[x.emotion] = x.intensity
                else:
                    intensity_checker[x.emotion] += x.intensity
                
            #finding highest frequency of emotions
            emotion_val = emotion_checker.values()
            #if user does nto have any emotions selected
            if temp == []:
                final_intensity = "-"
                final_emotions = "-"
                
                return render_template("participant/session_124.html", session = session, participant = participant, stage=4,
                                    max_emotions = final_emotions, max_intensity = final_intensity)
            else:
                
                max_emotion_val = max(emotion_val)
                emotion_list = []
                final_emotions = ''
                
                for key, value in emotion_checker.items():
                    if value == max_emotion_val:
                        emotion_list.append(key)
                if len(emotion_list) == 1:
                    final_emotions = emotion_list[0]
                elif len(emotion_list) == 2:
                    final_emotions = emotion_list[0] + ' and ' + emotion_list[1]
                else:
                    for i in range(len(emotion_list)):            
                        if i == len(emotion_list) -1:
                            final_emotions += 'and ' + emotion_list[i]
                        else:
                            final_emotions += emotion_list[i] + ', '

                #finding highest intensity
                intensity_val = intensity_checker.values()
                max_intensity_val = max(intensity_val)
                intensity_list = []
                final_intensity = ''
                
                for key, value in intensity_checker.items():
                    if value == max_intensity_val:
                        intensity_list.append(key)
                if len(intensity_list) == 1:
                    final_intensity = intensity_list[0]
                elif len(intensity_list) == 2:
                    final_intensity = intensity_list[0] + ' and ' + intensity_list[1]
                else: 
                    for i in range(len(intensity_list)):
                        if i == len(intensity_list) -1:
                            final_intensity += 'and ' + intensity_list[i]
                        else:
                            final_intensity += intensity_list[i] + ', '
                
                return render_template("participant/session_124.html", session = session, participant = participant, stage=4,
                                    max_emotions = final_emotions, max_intensity = final_intensity)
        else:
            return render_template("participant/session_5.html", session = session, participant = participant, stage=5)
    
    else:
        data = request.get_json() or {}
        if 'stage' not in data:
            return bad_request('Must include stage number')

        if data['stage'] == 1 and data['consent']:
            if session.pre_ques == '[]':
                participant.stage_num = 3
            else:
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