# import os
# import base64
# from datetime import datetime
# from cryptography.fernet import Fernet
# from cryptography.hazmat.primitives import hashes
# from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
# from flask_login import login_required
# from flask import Blueprint, render_template, request, redirect, url_for, flash , session , abort
# from piassist.models import Client , Tenant
# from . import db

# client = Blueprint('client', __name__)

# def validate_tenant(tenant_name):
#     tenant = Tenant.query.filter_by(name=tenant_name).first()
#     if tenant:
#         session['tenant_id'] = tenant.id
#         session['tenant_name'] = tenant.name
#     else:
#         flash("Invalid tenant specified in URL.", "is-warning")
#         abort(404, description=f"Invalid tenant: '{tenant_name}'")

# # Client Detail Route
# @client.route('/<tenant_name>/client/casefile/<int:casefile_id>', methods=['GET', 'POST'])
# @login_required
# def details(casefile_id , tenant_name):
#     validate_tenant(tenant_name)
    
#     client = Client.query.filter_by(id=casefile_id, tenant_id=session['tenant_id']).first_or_404()
#     # client = db.get_or_404(Client, client_id)
#     if request.method == 'POST':
#         client.first_name = request.form.get('first_name')
#         client.middle_name = request.form.get('middle_name')
#         client.last_name = request.form.get('last_name')
#         client.is_driver = request.form.get('is_driver')
#         client.marital_status = request.form.get('marital_status')
#         ssn = request.form.get('ssn') # Hash this
#         if ssn:
#             crystal_key = os.environ.get("CRYSTAL_KEY").encode()
#             if not client.nacl:
#                 nacl = os.urandom(16)
#                 client.nacl = nacl
#             else:
#                 nacl = client.nacl
#             kdf = PBKDF2HMAC(
#                 algorithm=hashes.SHA256(),
#                 length=32,
#                 salt=nacl,
#                 iterations=480000
#             )
#             f_key = base64.urlsafe_b64encode(kdf.derive(crystal_key))
#             f = Fernet(f_key)
#             client.physical_identifier = f.encrypt(ssn.encode())
#         else:
#             client.physical_identifier = None
#             client.nacl = None
#         client.street_address = request.form.get('street_address')
#         client.city = request.form.get('city')
#         client.state = request.form.get('state')
#         client.zip_code = request.form.get('zip_code')
#         client.primary_phone = request.form.get('primary_phone')
#         client.secondary_phone = request.form.get('secondary_phone')
#         client.email = request.form.get('email')
#         client.referrer = request.form.get('referrer')
#         client.referrer_relationship = request.form.get('referrer_relationship')
#         client.notes = request.form.get('notes')
#         client.injuries = request.form.get('injuries')
#         client.rode_ambulance = request.form.get('rode_ambulance')
#         client.visited_hospital = request.form.get('visited_hospital')
#         client.had_prior_injury = request.form.get('had_prior_injury')
#         client.prior_injury_notes = request.form.get('prior_injury_notes')
#         client.had_prior_accident = request.form.get('had_prior_accident')
#         client.prior_accident_notes = request.form.get('prior_accident_notes')
#         client.was_work_impacted = request.form.get('was_work_impacted')
#         client.work_impacted_notes = request.form.get('work_impacted_notes')
        
#         try:
#             client.dob = datetime.strptime(request.form.get('dob'), '%Y-%m-%d').date()
#         except:
#             flash(f"Couldn't save date of birth for client, {client.full_name}", "is-warning")

#         db.session.commit()
#         flash(f"The Client, {client.full_name}, has been updated successfully", "is-success")
#         return redirect(url_for('casefile.details', casefile_id = casefile_id , tenant_name=tenant_name))

#     return render_template('client/client-details.html', client=client , tenant_name=tenant_name)

# # Client Input Route
# @client.route('/<tenant_name>/new/client/casefile/<int:casefile_id>', methods=['GET', 'POST'])
# @login_required
# def input(casefile_id , tenant_name):
#     validate_tenant(tenant_name)
#     if request.method == 'POST':
#         first_name = request.form.get('first_name')
#         middle_name = request.form.get('middle_name')
#         last_name = request.form.get('last_name')
#         is_driver = request.form.get('is_driver')
#         marital_status = request.form.get('marital_status')
#         ssn = request.form.get('ssn') # Hash this
#         if ssn:
#             crystal_key = os.environ.get("CRYSTAL_KEY").encode()
#             nacl = os.urandom(16)
#             kdf = PBKDF2HMAC(
#                 algorithm=hashes.SHA256(),
#                 length=32,
#                 salt=nacl,
#                 iterations=480000
#             )
#             f_key = base64.urlsafe_b64encode(kdf.derive(crystal_key))
#             f = Fernet(f_key)
#             physical_identifier = f.encrypt(ssn.encode())
#         else:
#             physical_identifier = None
#             nacl = None
#         street_address = request.form.get('street_address')
#         city = request.form.get('city')
#         state = request.form.get('state')
#         zip_code = request.form.get('zip_code')
#         primary_phone = request.form.get('primary_phone')
#         secondary_phone = request.form.get('secondary_phone')
#         email = request.form.get('email')
#         referrer = request.form.get('referrer')
#         referrer_relationship = request.form.get('referrer_relationship')
#         notes = request.form.get('notes')
#         injuries = request.form.get('injuries')
#         rode_ambulance = request.form.get('rode_ambulance')
#         visited_hospital = request.form.get('visited_hospital')
#         had_prior_injury = request.form.get('had_prior_injury')
#         prior_injury_notes = request.form.get('prior_injury_notes')
#         had_prior_accident = request.form.get('had_prior_accident')
#         prior_accident_notes = request.form.get('prior_accident_notes')
#         was_work_impacted = request.form.get('was_work_impacted')
#         work_impacted_notes = request.form.get('work_impacted_notes')
        
#         try:
#             dob = datetime.strptime(request.form.get('dob'), '%Y-%m-%d').date()
#         except:
#             dob = None
#             flash(f"Couldn't save date of birth for new client", "is-warning")
        
#         try:
#             new_client = Client(
#                 casefile_id = casefile_id,
#                 first_name = first_name,
#                 middle_name = middle_name,
#                 last_name = last_name,
#                 is_driver = is_driver,
#                 marital_status = marital_status,
#                 dob = dob,
#                 physical_identifier = physical_identifier,
#                 nacl = nacl,           
#                 street_address = street_address,
#                 city = city,
#                 state = state,
#                 zip_code = zip_code,
#                 primary_phone = primary_phone,
#                 secondary_phone = secondary_phone,
#                 email = email,
#                 referrer = referrer,
#                 referrer_relationship = referrer_relationship,
#                 notes = notes,
#                 injuries = injuries,
#                 rode_ambulance = rode_ambulance,
#                 visited_hospital = visited_hospital,
#                 had_prior_injury = had_prior_injury,
#                 prior_injury_notes = prior_injury_notes,
#                 had_prior_accident = had_prior_accident,
#                 prior_accident_notes = prior_accident_notes,
#                 was_work_impacted = was_work_impacted,
#                 work_impacted_notes = work_impacted_notes,
#                 tenant_id=session['tenant_id'],
#             )
#             db.session.add(new_client)
#             db.session.commit()
#             flash(f"The Client, {new_client.full_name}, has been created successfully", "is-success")
#         except:
#             flash("Failed to create new client", "is-danger")
#             # ADD ABORT
        
#         return redirect(url_for('casefile.details', casefile_id = casefile_id , tenant_name=tenant_name))
#     return render_template('client/client-input.html', casefile_id = casefile_id ,client=client, tenant_name=tenant_name)

# # DELETE CLIENT ROUTE
# @client.route('/<tenant_name>/delete/client/<int:client_id>')
# @login_required
# def delete(client_id , tenant_name):
#     client = Client.query.filter_by(id=client_id, tenant_id=session['tenant_id']).first_or_404()
#     # client = db.get_or_404(Client, client_id)
#     db.session.delete(client)
#     db.session.commit()
#     flash(f"Client {client.full_name} Deleted Successfully", "is-success")
#     return redirect(url_for('casefile.details', casefile_id=client.casefile_id , tenant_name=tenant_name))

import os
import base64
from datetime import datetime
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from flask_login import login_required
from flask import Blueprint, render_template, request, redirect, url_for, flash, session, abort
from piassist.models import Client, Tenant
from . import db

client = Blueprint('client', __name__)

def validate_tenant(tenant_name):
    tenant = Tenant.query.filter_by(name=tenant_name).first()
    if tenant:
        session['tenant_id'] = tenant.id
        session['tenant_name'] = tenant.name
    else:
        flash("Invalid tenant specified in URL.", "is-warning")
        abort(404, description=f"Invalid tenant: '{tenant_name}'")

@client.route('/<tenant_name>/clients')
def index(tenant_name):
    clients = Client.query.filter_by(tenant_id=session['tenant_id']).order_by(Client.last_name).all()
    return render_template('client/client_index.html', clients=clients, tenant_name=tenant_name)

@client.route('/<tenant_name>/client//<int:client_id>', methods=['GET', 'POST'])
@login_required
def details(client_id, tenant_name):
    validate_tenant(tenant_name)
    
    # Fetch client by `client_id` and `tenant_id`
    client = Client.query.filter_by(id=client_id, tenant_id=session['tenant_id']).first_or_404()
    
    if request.method == 'POST':
        client.first_name = request.form.get('first_name')
        client.middle_name = request.form.get('middle_name')
        client.last_name = request.form.get('last_name')
        client.is_driver = request.form.get('is_driver')
        client.marital_status = request.form.get('marital_status')
        
        ssn = request.form.get('ssn')  # Get SSN from form

        # Ensure SSN is not None or empty before processing
        # 
        if ssn:
            crystal_key = os.environ.get("CRYSTAL_KEY").encode()
            nacl = os.urandom(16)
            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=32,
                salt=nacl,
                iterations=480000
            )
            
            f_key = base64.urlsafe_b64encode(kdf.derive(crystal_key))
            f = Fernet(f_key)
            client.physical_identifier = f.encrypt(ssn.encode())  # Encrypt SSN
        else:
            client.physical_identifier = None  # Handle case where SSN is not provided
            client.nacl = None  # Reset the salt if no SSN is provided

        client.street_address = request.form.get('street_address')
        client.city = request.form.get('city')
        client.state = request.form.get('state')
        client.zip_code = request.form.get('zip_code')
        client.primary_phone = request.form.get('primary_phone')
        client.secondary_phone = request.form.get('secondary_phone')
        client.email = request.form.get('email')
        client.referrer = request.form.get('referrer')
        client.referrer_relationship = request.form.get('referrer_relationship')
        client.notes = request.form.get('notes')
        client.injuries = request.form.get('injuries')
        client.rode_ambulance = request.form.get('rode_ambulance')
        client.visited_hospital = request.form.get('visited_hospital')
        client.had_prior_injury = request.form.get('had_prior_injury')
        client.prior_injury_notes = request.form.get('prior_injury_notes')
        client.had_prior_accident = request.form.get('had_prior_accident')
        client.prior_accident_notes = request.form.get('prior_accident_notes')
        client.was_work_impacted = request.form.get('was_work_impacted')
        client.work_impacted_notes = request.form.get('work_impacted_notes')
        
        try:
            client.dob = datetime.strptime(request.form.get('dob'), '%Y-%m-%d').date()
        except:
            flash(f"Couldn't save date of birth for client, {client.full_name}", "is-warning")

        db.session.commit()
        flash(f"The Client, {client.full_name}, has been updated successfully", "is-success")
        return redirect(url_for('casefile.details',casefile_id=client.casefile_id, tenant_name=tenant_name))

    return render_template('client/client-details.html', client=client, client_id=client_id, tenant_name=tenant_name)

# Client Input Route without `casefile_id`
@client.route('/<tenant_name>/new/client/casefile/<int:casefile_id>', methods=['GET', 'POST'])
@login_required
def input(tenant_name,casefile_id):
    validate_tenant(tenant_name)
    if request.method == 'POST':
        first_name = request.form.get('first_name')
        middle_name = request.form.get('middle_name')
        last_name = request.form.get('last_name')
        is_driver = request.form.get('is_driver')
        marital_status = request.form.get('marital_status')
        
        ssn = request.form.get('ssn')  # Hash this
        if ssn:
            crystal_key = os.environ.get("CRYSTAL_KEY").encode()
            nacl = os.urandom(16)
            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=32,
                salt=nacl,
                iterations=480000
            )
            f_key = base64.urlsafe_b64encode(kdf.derive(crystal_key))
            f = Fernet(f_key)
            physical_identifier = f.encrypt(ssn.encode())
        else:
            physical_identifier = None
            nacl = None

        street_address = request.form.get('street_address')
        city = request.form.get('city')
        state = request.form.get('state')
        zip_code = request.form.get('zip_code')
        primary_phone = request.form.get('primary_phone')
        secondary_phone = request.form.get('secondary_phone')
        email = request.form.get('email')
        referrer = request.form.get('referrer')
        referrer_relationship = request.form.get('referrer_relationship')
        notes = request.form.get('notes')
        injuries = request.form.get('injuries')
        rode_ambulance = request.form.get('rode_ambulance')
        visited_hospital = request.form.get('visited_hospital')
        had_prior_injury = request.form.get('had_prior_injury')
        prior_injury_notes = request.form.get('prior_injury_notes')
        had_prior_accident = request.form.get('had_prior_accident')
        prior_accident_notes = request.form.get('prior_accident_notes')
        was_work_impacted = request.form.get('was_work_impacted')
        work_impacted_notes = request.form.get('work_impacted_notes')
        dob = datetime.strptime(request.form.get('dob'), '%Y-%m-%d').date()
        new_client = Client(
                first_name=first_name,
                middle_name=middle_name,
                last_name=last_name,
                is_driver=is_driver,
                marital_status=marital_status,
                dob=dob,
                physical_identifier=physical_identifier,
                nacl=nacl,           
                street_address=street_address,
                city=city,
                state=state,
                zip_code=zip_code,
                primary_phone=primary_phone,
                secondary_phone=secondary_phone,
                email=email,
                referrer=referrer,
                referrer_relationship=referrer_relationship,
                notes=notes,
                injuries=injuries,
                rode_ambulance=rode_ambulance,
                visited_hospital=visited_hospital,
                had_prior_injury=had_prior_injury,
                prior_injury_notes=prior_injury_notes,
                had_prior_accident=had_prior_accident,
                prior_accident_notes=prior_accident_notes,
                was_work_impacted=was_work_impacted,
                work_impacted_notes=work_impacted_notes,
                tenant_id=session['tenant_id'],
            )
        db.session.add(new_client)
        db.session.commit()
        flash(f"The Client, {new_client.last_name}, has been created successfully", "is-success")
        
        return redirect(url_for('casefile.details', casefile_id=casefile_id, tenant_name=tenant_name))
    return render_template('client/client-input.html',casefile_id=casefile_id, tenant_name=tenant_name)

# DELETE CLIENT ROUTE
@client.route('/<tenant_name>/delete/client/<int:client_id>')
@login_required
def delete(client_id, tenant_name):
    validate_tenant(tenant_name)
    client = Client.query.filter_by(id=client_id, tenant_id=session['tenant_id']).first_or_404()
    db.session.delete(client)
    db.session.commit()
    flash(f"Client {client.full_name} Deleted Successfully", "is-success")
    return redirect(url_for('casefile.details', casefile_id=client.casefile_id, tenant_name=tenant_name))
