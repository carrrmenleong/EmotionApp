def test_login_already_logged_in(test_client, init_database, login_superadmin):
    """
    GIVEN a Flask application configured for testing
    WHEN the '/login' page is requested (GET) when the superadmin is already logged in
    THEN check superadmin is redirected to viewsession or viewusers page
    """
    response = test_client.get('/auth/login',follow_redirects=True)
    assert response.status_code == 200
    assert b'View Sessions' in response.data
    assert b'Logout' in response.data

    """ 
    GIVEN a Flask application configured for testing
    WHEN the '/logout' page is requested (GET)
    THEN check the response is valid
    """
    response = test_client.get('/auth/logout', follow_redirects=True)
    assert response.status_code == 200
    assert b'Login' in response.data
    assert b'Email' in response.data
    assert b'Password' in response.data



