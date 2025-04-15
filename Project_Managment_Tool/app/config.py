class Config:
    SECRET_KEY = 'f8d685b4a9be0c18611f9e4f57587507'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///app.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

# To generate secret key commands are :
#   import secrets
#   secrets.token_hex(16)