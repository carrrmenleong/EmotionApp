#from app import create_app, db

from app import create_app, db
from app.models import User, Session, Participant, Response

app = create_app()


@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'User': User, 'Session': Session, 'Participant':Participant, 'Response':Response}