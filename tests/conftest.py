import pytest
from app import create_app, db
from app.models import User, Session, Participant, Response
from datetime import datetime
import json


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
    #----------------------------
    db.create_all()

    # Insert user data
    #----------------------------
    user1 = User(
                id = 1,
                first_name = 'Carmen',
                last_name = 'Leong',
                username = 'Superadmin',
                orcid = 'H1234',
                institution = 'UWA',
                email = 'test@gmail.com',
                reason = "dummy reasons",
                approved = True
                )
    user1.set_password('1234')
    user2 = User(
                id = 2,
                first_name = 'Carmen',
                last_name = 'Leong',
                username = 'CarmenKW',
                orcid = 'H1234',
                institution = 'UWA',
                email = 'clkw@gmail.com',
                reason = "dummy reasons",
                approved = True
                )
    user2.set_password('1234')
    user3 = User(
                id = 3,
                first_name = 'Carmen',
                last_name = 'Leong',
                username = 'Superadmin',
                orcid = 'H1234',
                institution = 'UWA',
                email = 'emotionappmoodtrack@gmail.com',
                reason = "dummy reasons",
                approved = True)
    user3.set_password('1234')
    user4 = User(
                id = 4,
                first_name = 'Carmen',
                last_name = 'Leong',
                username = 'Superadmin',
                orcid = 'H1234',
                institution = 'UWA',
                email = 'notapprovedtest@gmail.com',
                reason = "dummy reasons",
                approved = False)
    user4.set_password('1234')
    db.session.add(user1)
    db.session.add(user2)
    db.session.add(user3)
    db.session.add(user4)

    # Insert sessions data
    #----------------------------
    session1 = Session(
                    id = 1,
                    published = True,
                    session_title = "Test Session1",
                    consent = "Please agree with consent",
                    emotions = "Happy\nSad\nAngry\nSuprised",
                    intensity = 10,
                    pre_ques = json.dumps(['firstq(open)','secondq(mcq)\nno\nyes']),
                    post_ques = json.dumps(['firstq(open)(postsession)','secondq(mcq)(postsession)\nno\nyes']),
                    user_id = 1
                    )
    db.session.add(session1)

    session2 = Session(
                    id = 2,
                    published = True,
                    session_title = "Test Session2",
                    consent = "Please agree with consent",
                    emotions = "Happy\nSad\nAngry\nSuprised",
                    intensity = 10,
                    pre_ques = ["firstq(open)","secondq(mcq)\nno\nyes"],
                    post_ques = ["firstq(open)(postsession)","secondq(mcq)(postsession)\nno\nyes"],
                    user_id = 3
                    )
    db.session.add(session2)

    session3 = Session(
                    id = 3,
                    published = False,
                    session_title = "Test Session2",
                    consent = "Please agree with consent",
                    emotions = "Happy\nSad\nAngry\nSuprised",
                    intensity = 10,
                    pre_ques = ["firstq(open)","secondq(mcq)\nno\nyes"],
                    post_ques = ["firstq(open)(postsession)","secondq(mcq)(postsession)\nno\nyes"],
                    user_id = 1
                    )
    db.session.add(session3)

    # Insert Participation data
    #-------------------------------
    participant1 = Participant(
                    id = 1,
                    stage_num = 1,
                    session_id = 1, 
                    pre_ques_ans = [],
                    post_ques_ans = [],
                    )
    participant2 = Participant(
                    id = 2,
                    stage_num = 4,
                    session_id = 1, 
                    pre_ques_ans = ["answer1","no"],
                    post_ques_ans = [],
                    )
    participant3 = Participant(
                    id = 3,
                    stage_num = 4,
                    session_id = 1, 
                    pre_ques_ans = ["answer1","no"],
                    post_ques_ans = [],
                    )
    participant4 = Participant(
                    id = 4,
                    stage_num = 5,
                    session_id = 1, 
                    pre_ques_ans = ["answer1","no"],
                    post_ques_ans = ["ye","nah","answer1","no"],
                    )
    db.session.add(participant1)
    db.session.add(participant2)
    db.session.add(participant3)
    db.session.add(participant4)

    # Insert Response data
    response1 = Response(
                id = 1,
                emotion = "Happy\nSad",
                intensity = 5,
                participant_id = 1,
                session_id = 1
                )
    db.session.add(response1)
    

    # Commit the changes
    db.session.commit()

    yield  # this is where the testing happens!

    db.drop_all()


@pytest.fixture(scope='function')
def login_default_user(test_client):
    test_client.post('/login',
                     data=dict(email='test@gmail.com', password='1234'),
                     follow_redirects=True)

    yield  # this is where the testing happens!

    test_client.get('/logout', follow_redirects=True)


@pytest.fixture(scope='function')
def login_superadmin(test_client):
    test_client.post('/login',
                     data=dict(email='emotionappmoodtrack@gmail.com', password='1234'),
                     follow_redirects=True)

    yield  # this is where the testing happens!

    test_client.get('/logout', follow_redirects=True)


@pytest.fixture(scope='function')
def user_token(test_client,init_database):
    user = User.query.filter_by(email="test@gmail.com").first()
    token = user.get_reset_password_token()
    return token