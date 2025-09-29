import os
from flask import Flask, request, redirect
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

# instantiate SQLAlchemy
db = SQLAlchemy()

def create_app():
    # Application factory function
    app = Flask(__name__)

    # Hardcode configuration for local development
    app.config['SECRET_KEY'] = 'your_secret_key' 
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///your_local_database.db'  
    app.config['MAIL_SERVER'] = 'smtp.gmail.com'  # Change for your SMTP provider
    app.config['MAIL_PORT'] = 587
    app.config['MAIL_USE_TLS'] = True
    app.config['MAIL_USE_SSL'] = False
    app.config['MAIL_USERNAME'] = 'jim@piassistance.com'
    app.config['MAIL_PASSWORD'] = 'xzitvsmnjtaxoeaw'  
    app.config['MAIL_DEFAULT_SENDER'] = 'jim@piassistance.com'
    # Setup database connection
    db.init_app(app)

    # Configure Flask-Login
    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    from .models import Member

    @login_manager.user_loader
    def load_user(member_id):
        return Member.query.get(member_id)

    from .auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint)

    from .autoadjuster import autoadjuster as autoadjuster_blueprint
    app.register_blueprint(autoadjuster_blueprint)

    from .firstpartyclaim import firstpartyclaim as firstpartyclaim_blueprint
    app.register_blueprint(firstpartyclaim_blueprint)

    from .autoinsurance import autoinsurance as autoinsurance_blueprint
    app.register_blueprint(autoinsurance_blueprint)

    from .casefile import casefile as casefile_blueprint
    app.register_blueprint(casefile_blueprint)

    from .client import client as client_blueprint
    app.register_blueprint(client_blueprint)

    from .healthadjuster import healthadjuster as healthadjuster_blueprint
    app.register_blueprint(healthadjuster_blueprint)

    from .healthclaim import healthclaim as healthclaim_blueprint
    app.register_blueprint(healthclaim_blueprint)

    from .healthinsurance import healthinsurance as healthinsurance_blueprint
    app.register_blueprint(healthinsurance_blueprint)

    from .intake import intake as intake_blueprint
    app.register_blueprint(intake_blueprint)

    from .intakemini import intakemini as intakemini_blueprint
    app.register_blueprint(intakemini_blueprint)

    from .medicalbill import medicalbill as medicalbill_blueprint
    app.register_blueprint(medicalbill_blueprint)

    from .medprovider import medprovider as medprovider_blueprint
    app.register_blueprint(medprovider_blueprint)

    from .thirdpartyclaim import thirdpartyclaim as thirdpartyclaim_blueprint
    app.register_blueprint(thirdpartyclaim_blueprint)

    from .drive_integration import drive_integration as drive_integration_blueprint
    app.register_blueprint(drive_integration_blueprint)

    from .jinja_filters import jinja_filters as jinja_filters_blueprint
    app.register_blueprint(jinja_filters_blueprint)

    # # Force SSL
    # @app.before_request
    # def before_request():
    #     if not request.is_secure:
    #         url = request.url.replace('http://', 'https://', 1)
    #         code = 301
    #         return redirect(url, code=code)

    # Click command for Test Case
    from .testcase import create_multi
    app.cli.add_command(create_multi)

    return app