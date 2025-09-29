from flask import Blueprint, redirect, url_for, render_template, request, flash, abort,session
from flask_login import login_user, logout_user, current_user, login_required
from piassist.models import Member,Tenant
from werkzeug.security import generate_password_hash, check_password_hash
from oauthlib.oauth2 import WebApplicationClient
from functools import wraps
from . import db
import os, secrets, requests
from datetime import datetime, timedelta
from sqlalchemy.exc import IntegrityError


GOOGLE_CLIENT_ID = os.environ.get("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.environ.get("GOOGLE_CLIENT_SECRET")
auth_endpoint = "https://accounts.google.com/o/oauth2/v2/auth"
token_endpoint = "https://oauth2.googleapis.com/token"
client = WebApplicationClient(GOOGLE_CLIENT_ID)

auth = Blueprint('auth', __name__)

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        remember = True if request.form.get('remember') else False
        
        member = Member.query.filter_by(email=email).first()

        # check if the member actually exists
        # take the member-supplied password, hash it, and compare it to the hashed password in the database
        if not member or not check_password_hash(member.password, password):
            flash('Please check your login details and try again.', 'is-info')
            return redirect(url_for('auth.login'))
             # if the member doesn't exit or password is wrong, reload the page
        session['tenant_id'] = member.tenant_id
        session['tenant_name'] = member.name
        # check that they registered with Google OAUTH
        if not member.access_token or not member.refresh_token:
            db.session.delete(member)
            db.session.commit()
            flash('There was a problem with your registration. Please re-register. Note: if problem persists, try revoking access in google account before registering.', 'is-danger')
            return redirect(url_for('auth.register'))

        # if the above check passes, then we know the member has the right credentials and is bonafide
        login_user(member, remember=remember)
        flash(f'{member.name} has successfully logged in', 'is-success')
        return redirect(url_for('casefile.index', tenant_name=session['tenant_name']))

    return render_template('auth/login.html')
@auth.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        # Form validation logic...
        email = request.form.get('email')
        name = request.form.get('name')
        password = request.form.get('password')
        invitation = request.form.get('invitation')

        # Validate form fields
        error = None
        if not email:
            error = "Email is empty"
            flash(error)
            return redirect(url_for('auth.register'))
        elif not name:
            error = "Name is empty"
            flash(error)
            return redirect(url_for('auth.register'))
        elif not password:
            error = "Password is empty"
            flash(error)
            return redirect(url_for('auth.register'))
        elif not invitation:
            error = "Invitation Code is required"
            flash(error)
            return redirect(url_for('auth.register'))

        # Check if the email already exists
        member = Member.query.filter_by(email=email).first()
        if member:
            error = "Email address already exists"
            flash(error)
            return redirect(url_for('auth.register'))

        # Check the invitation code
        access_code = generate_password_hash(os.environ.get('INVITATION_CODE'), method='pbkdf2:sha256')
        is_invited = check_password_hash(access_code, invitation)
        if not is_invited:
            error = 'Invalid Invitation Code'
            flash(error)
            return redirect(url_for('auth.register'))
        # Create new tenant
        new_tenant = Tenant(name=name, folder_id="1oSSE1VnNNoaRv728Fi7itfi_KGQZmAQL" )
        db.session.add(new_tenant)
        db.session.commit()

        if error is None:
            try:
                # Generate member ID
                secret = secrets.token_urlsafe(16)
                new_member = Member(   id=secret, 
            email=email, 
            name=name, 
            tenant_id=new_tenant.id, 
            is_admin=False,
            role='user',
            password=generate_password_hash(password, method='pbkdf2:sha256'))
            # access_token=None,
            # refresh_token=None,
            # token_expiration=None)
                db.session.add(new_member)
                db.session.commit()
            except IntegrityError as e:
                db.session.rollback()  # Rollback on error
                error = f"Database Integrity Error: {str(e)}"
                flash(error)
                return redirect(url_for('auth.register'))  # Redirect to the registration page
            else:
                request_uri = client.prepare_request_uri(
                    auth_endpoint,
                    redirect_uri=request.base_url + "/callback",
                    scope="https://www.googleapis.com/auth/drive",
                    access_type="offline",
                    state=secret,
                    login_hint=email
                )
                return redirect(request_uri)  # Redirect to external authentication

        return render_template('auth/register.html')

    return render_template('auth/register.html')


@auth.route('/register/callback', methods=['POST', 'GET'])
def callback():
    # catch the authorization code
    code = request.args.get("code")
    state_secret = request.args.get("state")

    # prepare and send a request to get tokens!
    token_url, headers, body = client.prepare_token_request(
        token_endpoint,
        authorization_response=request.url,
        redirect_url=request.base_url,
        code=code
    )
    token_response = requests.post(
        token_url,
        headers=headers,
        data=body,
        auth=(GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET)
    )

    response = token_response.json()
    print("Json REsponse", response)
    if response:
        new_member = Member.query.get_or_404(state_secret)
        # new_member = Member.query.filter_by(id=state_secret).first()
        if not new_member:
            flash("Member not found. Please try again.", "is-danger")
            return redirect(url_for("auth.register"))
        
        new_member.access_token = response["access_token"] 
        new_member.refresh_token = response["refresh_token"]
        # new_member.access_token = response.get("access_token")
        # new_member.refresh_token = response.get("refresh_token") 
        new_member.token_expiration = datetime.utcnow() + timedelta(seconds=response["expires_in"])

        db.session.add(new_member)
        db.session.commit()

    return redirect(url_for('auth.login'))

@auth.route('/refresh')
@login_required
def refresh():
    # prepare data payloads for request
    token_url, headers, body = client.prepare_refresh_token_request(
        token_endpoint,
        refresh_token=current_user.refresh_token,
        scope="https://www.googleapis.com/auth/drive"
    )

    print("Client ID: ", GOOGLE_CLIENT_ID, "\nClient Secret: ", GOOGLE_CLIENT_SECRET)
    refresh_response = requests.post(
        token_url,
        headers=headers,
        data=body,
        auth=(GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET)
    )

    print("Refresh Response:")
    print(refresh_response)

    response = refresh_response.json()

    print("Response JSON:")
    print(response)

    if response:
        try:
            current_user.access_token = response["access_token"]
            current_user.token_expiration = datetime.utcnow() + timedelta(seconds=response["expires_in"])
            db.session.commit()
        except:
            print("Couldn't commit changes to current user")
    
    return redirect(url_for('auth.profile'))
@auth.route('/')
@login_required
def home():
    return render_template('home.html')
@auth.route('/logout')
@login_required
def logout():
    flash(f'{current_user.name} has been successfully logged out', 'is-success')
    logout_user()
    return redirect(url_for('auth.login'))

@auth.route('/profile')
@login_required
def profile():
    return render_template('auth/profile.html', member = current_user)

def inline_refresh():
    # prepare data payloads for request
    token_url, headers, body = client.prepare_refresh_token_request(
        token_endpoint,
        refresh_token=current_user.refresh_token,
        scope="https://www.googleapis.com/auth/drive"
    )
    print("Token URL: ", token_url)
    refresh_response = requests.post(
        token_url,
        headers=headers,
        data=body,
        auth=(GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET)
    )
    print("Client ID: ", GOOGLE_CLIENT_ID, "\nClient Secret: ", GOOGLE_CLIENT_SECRET)
    print("Refresh Response:")
    print(refresh_response)

    response = refresh_response.json()

    print("Response JSON:")
    print(response)

    if response:
        try:
            current_user.access_token = response["access_token"]
            current_user.token_expiration = datetime.utcnow() + timedelta(seconds=response["expires_in"])
            db.session.commit()
        except:
            print("Couldn't commit changes to current user")
    
    return

def is_admin(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            if not current_user.is_authenticated:
                return redirect(url_for('auth.login'))
            else:
                abort(403)
        return func(*args, **kwargs)
    return wrapper
