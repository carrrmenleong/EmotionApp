import json
from app.models import Session
from flask import url_for

def test_logged_in_as_superadmin(test_client, init_database, login_superadmin):
    """
    GIVEN a Flask application configured for testing
    WHEN the '/login' page is requested (GET) when the superadmin is already logged in
    THEN check superadmin is redirected to viewsession or viewusers page
    """
    response = test_client.get('/login',follow_redirects=True)
    assert response.status_code == 200
    assert b'View Users' in response.data
    assert b'Logout' in response.data

    """
    GIVEN a Flask application configured for testing
    WHEN the '/superadmin_viewsessions' page is requested (GET)
    THEN check the response is valid
    """
    response = test_client.get('/viewsessions', follow_redirects=True)
    assert response.status_code == 200
    assert b'View Sessions' in response.data
    assert b'Logout' in response.data

    """
    GIVEN a Flask application configured for testing
    WHEN the '/viewsession/<int:sessionid>' page is requested (GET)
    THEN check the response is valid
    """
    response = test_client.get('/viewsession/2')
    assert response.status_code == 200
    assert b'View Sessions' in response.data
    assert b'Logout' in response.data

    """
    GIVEN a Flask application configured for testing
    WHEN the '/signupreq' page is requested (GET)
    THEN check the response is valid
    """
    response = test_client.get('/signupreq')
    assert response.status_code == 200
    assert b'Sign Up Requests' in response.data
    assert b'Logout' in response.data

    """ 
    GIVEN a Flask application configured for testing
    WHEN the '/logout' page is requested (GET)
    THEN check the response is valid
    """
    response = test_client.get('/logout', follow_redirects=True)
    assert response.status_code == 200
    assert b'Login' in response.data
    assert b'Email' in response.data
    assert b'Password' in response.data




def test_logged_in_as_admin(test_client,init_database,login_default_user):
    """
    GIVEN a Flask application configured for testing
    WHEN the '/viewsessions' page is requested (GET)
    THEN check the response is valid
    """
    response = test_client.get('/viewsessions')
    assert response.status_code == 200
    assert b'View Sessions' in response.data
    assert b'Logout' in response.data


    """
    GIVEN a Flask application configured for testing
    WHEN the '/viewsession/<int:sessionid>' page is requested (GET)
    THEN check the response is valid
    """
    response = test_client.get('/viewsession/1')
    assert response.status_code == 200
    assert b'View Sessions' in response.data
    assert b'Logout' in response.data

    """
    GIVEN a Flask application configured for testing
    WHEN the '/createsession' page is posted (POST)
    THEN check the response is valid
    """
    response = test_client.post('/createsession',
                                json={'id':1,
                                    'sessionTitle':'session1a',
                                    'consent': True,
                                    'emotions':'Anxious',
                                    'intensity':10,
                                    'preQuestions': 'preQues1',
                                    'postQuestions': 'postQues1'
                                    })
    assert response.status_code == 200
    assert b'Successully created session' in response.data

def test_approve_user(test_client, init_database, login_superadmin):
    """
    GIVEN a Flask application configured for testing
    WHEN the '/approveUser' page is posted (POST)
    WHEN superadmin click the 'Approve' button
    THEN check the response is valid
    """
    response = test_client.post('/approveUser', json="4", follow_redirects=True)
    assert response.status_code == 200
    assert b'Sign Up Requests' in response.data


def test_deny_user(test_client, init_database, login_superadmin):
    """
    GIVEN a Flask application configured for testing
    WHEN the '/denyUser' page is posted (POST)
    WHEN superadmin click the 'Deny' button
    THEN check the response is valid
    """
    response = test_client.post('/denyUser', json="4", follow_redirects=True)
    assert response.status_code == 200
    assert b'Sign Up Requests' in response.data


def test_delete_user(test_client, init_database, login_superadmin):
    """
    GIVEN a Flask application configured for testing
    WHEN the '/deleteUser' page is posted (POST)
    WHEN superadmin click the 'Delete' button
    THEN check the response is valid
    """
    response = test_client.post('/deleteUser', json="2", follow_redirects=True)
    assert response.status_code == 200
    assert b'success' in response.data


def test_modify_session(test_client, init_database, login_default_user):
    """
    GIVEN a Flask application configured for testing
    WHEN the '/copySession/<int:id>' page is requested (GET)
    THEN check the response is valid
    """
    response = test_client.get('/copySession/1')
    assert response.status_code == 200
    assert b'Create Session' in response.data
    

    """
    GIVEN a Flask application configured for testing
    WHEN the '/editSession/<int:id>' page is requested (GET)
    THEN check the response is valid
    """
    response = test_client.get('/editSession/1')
    assert response.status_code == 200
    assert b'Edit Session' in response.data


def test_publish_session(test_client, init_database, login_default_user):
    """
    GIVEN a Flask application configured for testing
    WHEN the '/publishsession' page is posted (POST)
    THEN check the response is valid
    """
    response = test_client.post('/publishsession',
                                json={'sessionId':3})
    assert response.status_code == 200
    assert b"Successfully published session" in response.data
    

def test_update_session(test_client, init_database, login_default_user):
    """
    GIVEN a Flask application configured for testing
    WHEN the '/updateSession' page is posted (POST)
    THEN check the response is valid
    """
    response = test_client.post('/updateSession',
                                json=json.dumps({'id':2,
                                    'sessionTitle':'session1a',
                                    'consent': True,
                                    'emotions':'Anxious',
                                    'intensity':'10',
                                    'preQuestions': 'preQues1',
                                    'postQuestions': 'postQues1'
                                    }),
                                follow_redirects = True
                                )
    assert response.status_code == 200
    assert b'View Session' in response.data


def test_delete_session(test_client, init_database, login_superadmin):
    """
    GIVEN a Flask application configured for testing
    WHEN the '/deleteSession' page is posted (POST)
    THEN check the response is valid
    """
    response = test_client.post('/deleteSession',
                                json="2",
                                follow_redirects = True
                                )
    assert response.status_code == 200
    assert b'success' in response.data


def test_delete_result(test_client, init_database, login_superadmin):
    """
    GIVEN a Flask application configured for testing
    WHEN the '/deleteresult' page is posted (POST)
    THEN check the response is valid
    """
    response = test_client.post('/deleteresult',
                                json=json.dumps({'sessionid':1,'participantid':1}),
                                follow_redirects = True
                                )
    assert response.status_code == 200
    assert b'success' in response.data


def test_bulk_download(test_client, init_database, login_default_user):
    """
    GIVEN a Flask application configured for testing
    WHEN the '/download/emotions/<int:sessionid>' page is requested (GET)
    THEN check the response is valid
    """
    response = test_client.get('/download/emotions/1')
    assert b'Timestamp,Emotion,Intensity,Participant ID\r\n' in response.data


    """
    GIVEN a Flask application configured for testing
    WHEN the '/download/ans/<int:sessionid>' page is requested (GET)
    THEN check the response is valid
    """
    
    response = test_client.get('/download/ans/1')
    assert response.status_code == 200
    assert b'Question,Answer,Participant ID' in response.data


def test_download_a_participant_result(test_client, init_database, login_superadmin):
    """
    GIVEN a Flask application configured for testing
    WHEN the '/download/<int:sessionid>/<int:participantid>' page is requested (GET)
    THEN check the response is valid
    """
    response = test_client.get('/download/1/4')
    assert response.status_code == 200
    assert b'Questions,Answer' in response.data
