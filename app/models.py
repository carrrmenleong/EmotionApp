from app import db, login, app
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from time import time
import jwt


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
    
    def get_reset_password_token(self, expires_in=600):
        return jwt.encode(
            {'reset_password': self.id, 'exp': time() + expires_in}, app.config['SECRET_KEY'], algorithm='HS256')

    @staticmethod
    def verify_reset_password_token(token):
        try:
            id = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])['reset_password']
        except:
            return
        return User.query.get(id)


# Each row in this table represent a survey session
class Session(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    published = db.Column(db.Boolean)
    session_title = db.Column(db.String(128))
    consent = db.Column(db.String()) 
    emotions = db.Column(db.String(128)) # Represent all emotion options separated by '\n'
    intensity = db.Column(db.Integer)
    pre_ques = db.Column(db.JSON)
    post_ques = db.Column(db.JSON)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id')) # Foreign key. Represent the reseacher that created this session

    participants = db.relationship('Participant', backref='session',lazy='dynamic')

    def __repr__(self):
        return '<Id: {}, published: {}, session_title: {}, consent: {}, emotions: {}, intensity: {}, pre_ques: {}, post_ques: {}, user_id: {}>' \
            .format(self.id,self.published,self.session_title,self.consent,self.emotions,self.intensity,self.pre_ques,self.post_ques,self.user_id)

    def to_dict(self):
        data = {
            'id': self.id,
            'published': self.published,
            'session_title':self.session_title,
            'consent':self.consent,
            'emotions':self.emotions,
            'intensity':self.intensity,
            'pre_ques':self.pre_ques,
            'post_ques':self.post_ques,
            'user_id':self.user_id
            }
        return data

# Each row in this table represent a participant of a survey session
class Participant(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    stage_num = db.Column(db.Integer) # Represent the stage that the participant has reached thorughout the session
    session_id = db.Column(db.Integer, db.ForeignKey('session.id')) # Foreign key. Represent the session that the participant participate in
    pre_ques_ans = db.Column(db.JSON)
    post_ques_ans = db.Column(db.JSON)

    responses = db.relationship('Response', backref='participant',lazy='dynamic')

    def __repr__(self):
        return '<Id: {}, stage_num: {}, session_id:{} pre_ques_ans:{}, post_ques_ans:{}>'.format(self.id,self.stage_num, self.session_id, self.pre_ques_ans, self.post_ques_ans)


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