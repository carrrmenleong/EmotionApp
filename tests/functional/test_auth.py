def test_login_page(test_client):
    """
    GIVEN a Flask application configured for testing
    WHEN the '/login' page is requested (GET)
    THEN check the response is valid
    """
    response = test_client.get('/login')
    assert response.status_code == 200
    assert b'Login' in response.data
    assert b'Email' in response.data
    assert b'Password' in response.data


def test_valid_login_logout(test_client, init_database):
    """
    GIVEN a Flask application configured for testing
    WHEN the '/login' page is posted to (POST)
    THEN check the response is valid
    """
    response = test_client.post('/login',
                                data=dict(email='test@gmail.com', password='1234'),
                                follow_redirects=True)
    assert response.status_code == 200
    assert b'View Sessions' in response.data
    assert b'Log Out' in response.data

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


def test_invalid_login(test_client, init_database):
    """
    GIVEN a Flask application configured for testing
    WHEN the '/login' page is posted to with invalid credentials (POST)
    THEN check an error message is returned to the user
    """
    response = test_client.post('/login',
                                data=dict(email='patkennedy79@gmail.com', password='FlaskIsNotAwesome'),
                                follow_redirects=True)
    assert response.status_code == 200
    assert b'Invalid email or password, please check your email and password.' in response.data
    assert b'Log In' in response.data
    assert b'Email' in response.data
    assert b'Password' in response.data


def test_login_already_logged_in(test_client, init_database, login_default_user):
    """
    GIVEN a Flask application configured for testing
    WHEN the '/login' page is requested (GET) when the user is already logged in
    THEN check user is redirected to createsession or viewuser page
    """
    response = test_client.get('/login',follow_redirects=True)
    assert response.status_code == 200
    assert b'View Sessions' in response.data
    assert b'Log Out' in response.data

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


def test_valid_registration(test_client, init_database):
    """
    GIVEN a Flask application configured for testing
    WHEN the '/register' page is posted to (POST)
    THEN check the response is valid and user is redirected to login page
    """
    response = test_client.post('/signup',
                                data = dict(firstname = 'Carmen',
                                            lastname = 'Leong',
                                            username = 'CarmenKW',
                                            orcid = 'H1234',
                                            institution = 'UWA',
                                            email = 'test1@gmail.com',
                                            email2 = 'test1@gmail.com',
                                            password = '1234',
                                            password2 = '1234',
                                            reason = "dummyreasonsdummyreasonsdummyreasonsdummyreasonsdummyreasonsdummyreasonsdummyreasonsdummyreasonsdummyreasonsdummyreasons"),
                                follow_redirects=True)
    assert response.status_code == 200
    assert b'Congratulations, your signup has been requested!' in response.data
    assert b'Log In' in response.data
    assert b'Email' in response.data
    assert b'Password' in response.data


def test_invalid_registration(test_client, init_database):
    """
    GIVEN a Flask application configured for testing
    
    WHEN the '/register' page is posted to with mismatch password and confirm password (POST)
    THEN check an error message is returned to the user

    WHEN the '/register' page is posted to (POST) using an email address already registered
    THEN check an error message is returned to the user
    """
    response = test_client.post('/signup',
                                data = dict(firstname = 'Carmen',
                                            lastname = 'Leong',
                                            username = 'CarmenKW',
                                            orcid = 'H1234',
                                            institution = 'UWA',
                                            email = 'test@gmail.com',
                                            email2 = 'test@gmail.com',
                                            password = '1234',
                                            password2 = '123', # does not match
                                            reason = "dummyreasonsdummyreasonsdummyreasonsdummyreasonsdummyreasonsdummyreasonsdummyreasonsdummyreasonsdummyreasonsdummyreasons"),
                                follow_redirects=True)
    assert response.status_code == 200
    assert b'Field must be equal to password.' in response.data
    assert b'Please use a different email address.' in response.data
    assert b'Log In' in response.data
    assert b'Not Yet Registered? Create New Account' in response.data


def test_reset_password_request_page(test_client):
    """
    GIVEN a Flask application configured for testing
    WHEN the '/reset_password_request' page is requested (GET)
    THEN check the response is valid
    """
    response = test_client.get('/reset_password_request')
    assert response.status_code == 200
    assert b'Reset Password' in response.data
    assert b'Email' in response.data


def test_valid_reset_password_request(test_client,init_database):
    """
    GIVEN a Flask application configured for testing
    WHEN the '/reset_password_request' page is posted to (POST) with valid email
    THEN check the response is valid
    """
    response = test_client.post('/reset_password_request',
                                data = dict(email="test@gmail.com"),
                                follow_redirects=True)
    assert response.status_code == 200
    assert b"Check your email for the instructions to reset your password" in response.data
    assert b'Login' in response.data
    assert b'Email' in response.data
    assert b'Password' in response.data


def test_reset_password_page(test_client,init_database,user_token):
    """
    GIVEN a Flask application configured for testing
    WHEN the '/reset_password/<token>' page is requested (GET) with valid token
    THEN check the response is valid
    """
    response = test_client.get('/reset_password/'+user_token)
    assert response.status_code == 200
    assert b"Reset Your Password" in response.data
    assert b'Password' in response.data
    assert b'Repeat Password' in response.data


def test_valid_reset_password(test_client,init_database,user_token):
    """
    GIVEN a Flask application configured for testing
    WHEN the '/reset_password/<token>' page is posted to (POST) with valid token
    THEN check the response is valid
    """
    response = test_client.post('/reset_password/'+user_token, 
                                    data=dict(password="1122",password2='1122'),
                                    follow_redirects=True)
    assert response.status_code == 200
    assert b"Your password has been reset." in response.data
    assert b'Login' in response.data
    assert b'Email' in response.data
    assert b'Password' in response.data

    '''
    THEN check user can login with new password
    '''
    response = test_client.post('/login',
                        data=dict(email='test@gmail.com', password='1122'),
                        follow_redirects=True)
    assert response.status_code == 200
    assert b'View Sessions' in response.data
    assert b'Log Out' in response.data


