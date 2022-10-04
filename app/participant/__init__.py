from flask import Blueprint

bp = Blueprint('participant', __name__)

from app.participant import routes