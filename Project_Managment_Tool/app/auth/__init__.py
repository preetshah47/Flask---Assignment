from flask import Blueprint

auth = Blueprint('auth', __name__)

from . import routes  # Keeping this last to avoid circular import
