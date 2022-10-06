from app.models import User

"""
GIVEN a User model
WHEN a new User is created
THEN check the all the fields (firstname, lastname, username, orcid, institution, email, reason, password, approved) 
are defined correctly
"""
def test_new_user():
    user = User(first_name = 'Carmen',
                last_name = 'Leong',
                username = 'CarmenKW',
                orcid = 'H1234',
                institution = 'UWA',
                email = 'test@gmail.com',
                reason = "dummy reasons")
    user.set_password('caty123')
    assert user.first_name == 'Carmen'
    assert user.last_name == 'Leong'
    assert user.username == 'CarmenKW'
    assert user.orcid == 'H1234'
    assert user.institution == 'UWA'
    assert user.reason == "dummy reasons"
    assert user.email == 'test@gmail.com'
    assert user.password_hash != 'caty123'

"""
GIVEN a User model
WHEN a new User is created
THEN check the password are hashed correctly
"""
def test_password_hashing():
    u = User(username='susan')
    u.set_password('cat')
    assert u.password_hash != 'caty123'
