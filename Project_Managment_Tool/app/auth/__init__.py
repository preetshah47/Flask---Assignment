from flask import Blueprint

auth = Blueprint('auth', __name__)

from . import routes  # Keep this last to avoid circular import
