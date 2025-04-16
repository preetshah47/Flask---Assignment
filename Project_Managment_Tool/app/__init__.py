from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from .config import Config
from .models import db, User

# Initialize extensions (without app yet)
login_manager = LoginManager()
login_manager.login_view = 'auth.login'  # Redirects to login page if not logged in

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Initialize extensions with app
    db.init_app(app)
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # Blueprint registration (will define later)
    from .auth.routes import auth
    app.register_blueprint(auth)

    # register the project blueprint
    from .project.routes import project
    app.register_blueprint(project)

    # register the task blueprint
    from .task.routes import task_bp
    app.register_blueprint(task_bp)

    # Create DB + default admin
    with app.app_context():
        db.create_all()
        if not User.query.first():
            admin_user = User(
                name='Admin',
                phone='1111111111',
                email='admin@gmail.com',
                role='admin'
            )
            admin_user.set_password('admin')
            db.session.add(admin_user)
            db.session.commit()

    return app

