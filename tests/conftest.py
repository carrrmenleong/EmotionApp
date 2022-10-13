import pytest
from app import create_app, db
from app.models import User


@pytest.fixture(scope='module')
def new_user():
    user = User(first_name = 'Carmen',
                    last_name = 'Leong',
                    username = 'CarmenKW',
                    orcid = 'H1234',
                    institution = 'UWA',
                    email = 'test@gmail.com',
                    reason = "dummy reasons")
    user.set_password('1234')
    return user


@pytest.fixture(scope='module')
def test_client():
    flask_app = create_app()
    flask_app.config.from_object('config.TestingConfig')

    # Create a test client using the Flask application configured for testing
    with flask_app.test_client() as testing_client:
        # Establish an application context
        with flask_app.app_context():
            yield testing_client  # this is where the testing happens!


@pytest.fixture(scope='module')
def init_database(test_client):
    # Create the database and the database table
    db.create_all()

    # Insert user data
    user1 = User(first_name = 'Carmen',
                    last_name = 'Leong',
                    username = 'Superadmin',
                    orcid = 'H1234',
                    institution = 'UWA',
                    email = 'test@gmail.com',
                    reason = "dummy reasons",
                    approved = True)
    user1.set_password('1234')
    user2 = User(first_name = 'Carmen',
                    last_name = 'Leong',
                    username = 'CarmenKW',
                    orcid = 'H1234',
                    institution = 'UWA',
                    email = 'clkw@gmail.com',
                    reason = "dummy reasons",
                    approved = True)
    user2.set_password('1234')
    user3 = User(first_name = 'Carmen',
                    last_name = 'Leong',
                    username = 'Superadmin',
                    orcid = 'H1234',
                    institution = 'UWA',
                    email = 'emotionappmoodtrack@gmail.com',
                    reason = "dummy reasons",
                    approved = True)
    user3.set_password('1234')
    db.session.add(user1)
    db.session.add(user2)
    db.session.add(user3)

    # Commit the changes for the users
    db.session.commit()

    yield  # this is where the testing happens!

    db.drop_all()


@pytest.fixture(scope='function')
def login_default_user(test_client):
    test_client.post('/auth/login',
                     data=dict(email='clkw@gmail.com', password='1234'),
                     follow_redirects=True)

    yield  # this is where the testing happens!

    test_client.get('/auth/logout', follow_redirects=True)


@pytest.fixture(scope='function')
def login_superadmin(test_client):
    test_client.get('/auth/login',
                     data=dict(email='emotionappmoodtrack@gmail.com', password='1234'),
                     follow_redirects=True)

    yield  # this is where the testing happens!

    test_client.get('/auth/logout', follow_redirects=True)


@pytest.fixture(scope='function')
def user_token(test_client,init_database):
    user = User.query.filter_by(email="test@gmail.com").first()
    token = user.get_reset_password_token()
    return token