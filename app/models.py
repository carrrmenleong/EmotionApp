from app import db, login
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin


# Each row in this table represent an Admin(Researcher) or a Superadmin
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    fist_name = db.Column(db.String(64))
    last_name = db.Column(db.String(64))
    username = db.Column(db.String(64))
    orcid = db.Column(db.String(64))
    institution = db.Column(db.String(120))
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    reason = db.Column(db.String)
    approved = db.Column(db.Boolean)

    sessions = db.relationship('Session', backref='creator',lazy='dynamic')

    def __repr__(self):
        return '<Id: {}, Username: {}, Email: {}>'.format(self.id, self.username, self.email)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    @login.user_loader
    def load_user(id):
        return User.query.get(int(id))


# Each row in this table represent a survey session
class Session(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    published = db.Column(db.Boolean)
    consent = db.Column(db.String()) 
    emotions = db.Column(db.String(128)) # Represent all emotion options separated by '\n'
    intensity = db.Column(db.Integer)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id')) # Foreign key. Represent the reseacher that created this session

    questions = db.relationship('Question', backref='session',lazy='dynamic')
    participants = db.relationship('Participant', backref='session',lazy='dynamic')

    def __repr__(self):
        return '<Id: {}, published: {}>'.format(self.id,self.published)


# Each row in this table represent a question (either pre-measuring and post-measuring quesiton)
class Question(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    question = db.Column(db.String()) # Represent the question (for multiple choice question, the question & it's options will be separated with '\n')
    is_open_ended = db.Column(db.Boolean) # Represent whether the question is open ended (True) or multiple choice (False)
    sequence_num = db.Column(db.Integer) # Represent the seqence number of the question in the pre-measuring questions or post-measuring questions
    is_pre = db.Column(db.Boolean) # Represent whether the question is pre-measuring (True) or post-measuring (False) question
    session_id = db.Column(db.Integer, db.ForeignKey('session.id')) # Foreign key. Represent the session that the question belongs to

    answers = db.relationship('Answer', backref='question',lazy='dynamic')

    def __repr__(self):
        return '<Id: {}, question: {}>'.format(self.id,self.question)


# Each row in this table represent a participant of a survey session
class Participant(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    stage_num = db.Column(db.Integer) # Represent the stage that the participant has reached thorughout the session
    session_id = db.Column(db.Integer, db.ForeignKey('session.id')) # Foreign key. Represent the session that the participant participate in

    answers = db.relationship('Answer', backref='participant',lazy='dynamic')
    responses = db.relationship('Response', backref='participant',lazy='dynamic')

    def __repr__(self):
        return '<Id: {}, stage_num: {}, session_id:{}>'.format(self.id,self.stage_num, self.session_id)


# Each row in this table represent an answer of a participant to a question
class Answer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    answer = db.Column(db.String())
    participant_id = db.Column(db.Integer, db.ForeignKey('participant.id'))
    question_id = db.Column(db.Integer, db.ForeignKey('question.id'))
    
    def __repr__(self):
        return '<Id: {}, answer: {}, participant_id: {}, question_id: {}>'.format(self.id,self.answer, self.participant_id, self.question_id)


# Each row in this table represent an emotion response of a participant
class Response(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    emotion = db.Column(db.String)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    intensity = db.Column(db.Integer)
    participant_id = db.Column(db.Integer, db.ForeignKey('participant.id'))
    session_id = db.Column(db.Integer, db.ForeignKey('session.id'))

    
    def __repr__(self):
        return '<Id: {}, emotion: {}, timestamp:{}, intensity:{}>'.format(self.id,self.emotion,self.timestamp, self.intensity)