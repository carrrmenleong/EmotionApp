from app.models import User, Session

def test_session_home(test_client,init_database):
    """
    GIVEN a Flask application configured for testing
    WHEN the '/session/<int:sessionid>' page is requested (GET)
    THEN check the response is valid
    """
    session = Session.query.first()
    id = str(session.id)
    response = test_client.get('/session/'+id)
    assert response.status_code == 200
    assert b'Start Session' in response.data
    assert b'Continue Session' in response.data
    assert b'Welcome to Emotion App!' in response.data


def test_new_participant_id(test_client,init_database):
    """
    GIVEN a Flask application configured for testing
    WHEN the '/session/<int:sessionid>/getid' page is requested (GET)
    THEN check the response is valid
    """
    session = Session.query.first()
    id = str(session.id)
    response = test_client.get('/session/'+id+'/getid')
    assert response.status_code == 200
    assert b'5' in response.data

def test_participant_id_validity(test_client,init_database):
    """
    GIVEN a Flask application configured for testing
    WHEN the '/session/<int:sessionid>/<int:participantid>/checkid' page is requested (GET)
    THEN check the response is valid
    """
    response = test_client.get('/session/1/50/checkid')
    assert response.status_code == 200
    assert b'invalidId' in response.data

    response = test_client.get('/session/1/1/checkid')
    assert response.status_code == 200
    assert b'validId' in response.data


def test_participant_stage12345(test_client,init_database):
    """
    GIVEN a Flask application configured for testing
    WHEN the '/session/<int:sessionid>/<int:participantid>' page is requested (GET) AND
    WHEN participant is in stage 1 (agree consent stage)
    THEN check the response is valid
    """
    response = test_client.get('/session/1/1')
    assert response.status_code == 200
    assert b'Participant Information and Consent' in response.data

    """
    WHEN the '/session/<int:sessionid>/<int:participantid>' page is posted (POST) AND
    WHEN participant is in stage 1 (agree consent stage)
    THEN check the response is valid
    """
    response = test_client.post('/session/1/1',
                                json={"stage":1, "consent":True}
                                )
    assert response.status_code == 200
    assert b'Successfully recorded consent' in response.data

    '''
    WHEN the '/session/<int:sessionid>/<int:participantid>' page is requested (GET) AND
    WHEN participant is in stage 2 (preqestion session stage)
    THEN check the response is valid
    '''
    response = test_client.get('/session/1/1')
    assert response.status_code == 200
    assert b'Pre-Session Survey' in response.data
    assert b'firstq(open)' in response.data
    assert b'secondq(mcq)' in response.data

    '''
    WHEN the '/session/<int:sessionid>/<int:participantid>' page is posted (POST) AND
    WHEN participant is in stage 2 (presession questions stage)
    THEN check the response is valid
    '''
    response = test_client.post('/session/1/1',
                                json={"stage":2, "ans":["answer1","no"]}
                                )
    assert response.status_code == 200
    assert b'Successfully recorded answers for pre-session questions' in response.data

    response = test_client.post('/session/1/1',
                                json={"ans":["answer1","no"]}
                                )
    assert response.status_code == 400
    assert b'Must include stage number' in response.data

    '''
    WHEN the '/session/<int:sessionid>/<int:participantid>' page is requested (GET) AND
    WHEN participant is in stage 3 (emotion session stage)
    THEN check the response is valid
    '''
    response = test_client.get('/session/1/1')
    assert response.status_code == 200
    assert b"Click on the emotion(s) you are feeling right now and indicate their intensity." in response.data
    assert b"Happy" in response.data
    assert b"Sad" in response.data
    assert b"Angry" in response.data

    '''
    WHEN the '/session/<int:sessionid>/<int:participantid>' page is posted (POST) AND
    WHEN participant is in stage 3 (emotion session stage) and click "Submit Present Emotion(s)"
    THEN check the response is valid
    '''
    response = test_client.post('/session/1/1',
                                json={"stage":3, "endStage":False,'emotions':{"Happy":3,"Sad":6}}
                                )
    response = test_client.post('/session/1/1',
                                json={"stage":3, "endStage":False,'emotions':{"Happy":2,"Angry":3}}
                                )
    assert response.status_code == 200
    assert b"Successfully recorded emotions response" in response.data

    '''
    WHEN the '/session/<int:sessionid>/<int:participantid>' page is posted (POST) AND
    WHEN participant is in stage 3 (emotion session stage) and click "Finish Session"
    THEN check the response is valid
    '''
    response = test_client.post('/session/1/1',
                                json={"stage":3, "endStage":True,'emotions':{}}
                                )
    assert response.status_code == 200
    assert b"Successfully recorded emotions response" in response.data

    '''
    WHEN the '/session/<int:sessionid>/<int:participantid>' page is requested (GET) AND
    WHEN participant is in stage 4 (postsession questions stage)
    THEN check the response is valid
    '''
    response = test_client.get('/session/1/1')
    assert response.status_code == 200
    assert b"Post-Session Survey" in response.data
    assert b"Your highest frequency emotion(s) are as shown below:" in response.data
    assert b"Your highest intensity emotion(s) are as shown below:" in response.data
    assert b"Sad" in response.data
    assert b"Happy" in response.data
    assert b"firstq(open)(postsession)" in response.data

    '''
    WHEN the '/session/<int:sessionid>/<int:participantid>' page is posted (POST) AND
    WHEN participant is in stage 4 (postsession questions stage)
    THEN check the response is valid
    '''
    response = test_client.post('/session/1/1',
                                json={"stage":4, "ans":["I'm feeling sad more","I feel sad and happy","answer1","no"]}
                                )
    assert response.status_code == 200
    assert b"Successfully recorded answers for post-session questions" in response.data

    '''
    WHEN the '/session/<int:sessionid>/<int:participantid>' page is requested (GET) AND
    WHEN participant is in stage 5 (End of session)
    THEN check the response is valid
    '''
    response = test_client.get('/session/1/1')
    assert response.status_code == 200
    assert b"Thank you for your participation!" in response.data

    '''
    WHEN the '/session/<int:sessionid>/<int:participantid>' page is requested (GET) AND
    WHEN participant is in stage 4 (postsession questions stage) without any emotions submitted
    THEN check the response is valid
    '''
    response = test_client.get('/session/1/2')
    assert response.status_code == 200
    assert b"Post-Session Survey" in response.data
    assert b"Your highest frequency emotion(s) are as shown below:" in response.data
    assert b"-" in response.data

