import requests, os
from flask import Blueprint, redirect, url_for, flash, abort,session
from flask_login import current_user, login_required
from piassist.models import Casefile, MedicalBill, HealthClaim, ThirdPartyClaim, FirstPartyClaim,Tenant
from . import db
from datetime import datetime, date

def validate_tenant(tenant_name):
    tenant = Tenant.query.filter_by(name=tenant_name).first()
    if tenant:
        session['tenant_id'] = tenant.id
        session['tenant_name'] = tenant.name
    else:
        flash("Invalid tenant specified in URL.", "is-warning")
        abort(404, description=f"Invalid tenant: '{tenant_name}'")

def check_tenant_folder_exists(access_token: str, tenant_name: str, root_folder_id: str) -> str:
    """
    Check if the tenant folder exists under the root folder.
    If found, return its ID, otherwise return None.
    """
    # Perform a Google Drive API query to check if the folder already exists.
    response = requests.get(
        f"https://www.googleapis.com/drive/v3/files?q='{root_folder_id}'+in+parents+and+name='{tenant_name}'+and+mimeType='application/vnd.google-apps.folder'",
        headers={"Authorization": f"Bearer {access_token}"}
    )
    if response.status_code == 200:
        response_data = response.json()
        if response_data.get('files'):
            # Folder exists, return its ID.
            return response_data['files'][0]['id']
    return None  # Folder does not exist


def create_folder(access_token: str, folder_name: str, parent_id: str) -> str:
    '''
    Create A Folder In Google Drive
    Using Drive Api Version 3
    '''
    response = requests.post(
        url = f"https://www.googleapis.com/drive/v3/files?access_token={access_token}&supportsAllDrives=true",
        headers = {"Content-type": "application/json"},
        json = {
            "mimeType": "application/vnd.google-apps.folder",
            "description": "generated from pi assist app",
            "name": folder_name,
            "parents": [parent_id]
        }
    )
    if response.status_code == 200:
        response = response.json()
    else:
        raise Exception(f"{response.status_code} error from request")
    
    return response['id']

def copy_template(access_token: str, template_id:str, name: str, parent_id: str, mime_type="application/vnd.google-apps.document") -> str:
    '''
    Create A Copy Of A Template
    In Google Drive
    '''
    response = requests.post(
        url = f"https://www.googleapis.com/drive/v3/files/{template_id}/copy?access_token={access_token}&supportsAllDrives=true",
        headers = {"Content-type": "application/json"},
        json = {
            "mimeType": mime_type,
            "description": "generated from pi assist app",
            "name": name,
            "parents": [parent_id]
        }
    )
    if response.status_code == 200:
        response = response.json()
    else:
        raise Exception(f"{response.status_code} error from request")
    
    return response['id']



def batch_update_file(access_token: str, file_id: str, json_body: dict):
    '''
    Batch Update A File In
    Google Drive
    '''
    response = requests.post(
        url = f"https://docs.googleapis.com/v1/documents/{file_id}:batchUpdate?access_token={access_token}",
        headers = {"Content-type": "application/json"},
        json = json_body
    )
    return response.status_code

def build_json_body(*args):
    '''
    Function takes a list of
    tuples to find and replace
    in a Google Drive batch
    update request and returns
    a valid json body for the
    request
    '''
    json_body = {"requests":[]}
    for arg in args:
        json_body["requests"].append(
            {
                "replaceAllText": {
                    "containsText": {
                        "text": arg[0],
                        "matchCase": "true"
                    },
                    "replaceText": arg[1]
                }
            }
        )
    return json_body

def check_access_token(expiration: datetime):
    '''
    Check Drive Api Access Token
    Age and Refresh If Neccessary
    '''
    expiration_delta = expiration - datetime.utcnow()
    if expiration_delta.total_seconds() <= 600:
        try:
            from .auth import inline_refresh
            inline_refresh()
            flash("Google api access_token was refreshed successfully.", "is-info")
            return True
        except:
             flash("Failed to refresh google api access_token. Contact tech support for assistance.", "is-danger")
             return False
    return True


# Start Blueprint
drive_integration = Blueprint('drive_integration', __name__)

# # Generate Case Skeleton in Google Drive
# @drive_integration.route('/<tenant_name>/casefile/<int:casefile_id>/google/new/skeleton')
# @login_required
# def generate_case_skeleton(tenant_name,casefile_id):
#     validate_tenant(tenant_name)
#     # casefile = db.get_or_404(Casefile, casefile_id)
#     tenant = Tenant.query.filter_by(id=session['tenant_id']).first_or_404()
#     casefile = Casefile.query.filter_by(id=casefile_id,  tenant_id=session['tenant_id']).first_or_404()
#     root_folder_id = os.environ.get("CASES_ROOT_ID")

#     if check_access_token(current_user.token_expiration):
#              if tenant.folder_id:
#         # Use the existing tenant folder
#                  tenant_folder_id = tenant.folder_id
#                  flash(f"Using existing folder for tenant: {tenant.name}", "is-info")
#              else:
#                  tenant_folder_id = create_folder(current_user.access_token, tenant_name, root_folder_id)

#         # Create Main Folder
#     casefile.main_folder_id = create_folder(current_user.access_token, casefile.case_label, tenant_folder_id)
#         # Create Client Documentation Folder
#     casefile.client_documentation_folder_id = create_folder(current_user.access_token, "Client Documentation", casefile.main_folder_id)
#         # Create Subrogation Folder
#     casefile.subrogation_folder_id = create_folder(current_user.access_token, "Subrogation", casefile.main_folder_id)
#         # Create Medical Records Folder
#     casefile.medical_record_folder_id = create_folder(current_user.access_token, "Medical Records", casefile.main_folder_id)
#         # Create 1st Party Folder
#     casefile.first_party_folder_id = create_folder(current_user.access_token, "1st Party", casefile.main_folder_id)
#         # Create 3rd Party Folder
#     casefile.third_party_folder_id = create_folder(current_user.access_token, "3rd Party", casefile.main_folder_id)
#         # Create Checks Folder
#     casefile.checks_folder_id = create_folder(current_user.access_token, "Checks", casefile.main_folder_id)
#         # Create Litigation Folder
#     casefile.litigation_folder_id = create_folder(current_user.access_token, "Litigation", casefile.main_folder_id)
#         # Create Pics & Video Folder
#     casefile.pics_and_videos_folder_id = create_folder(current_user.access_token, "Pics and Videos", casefile.main_folder_id)
#         # Create Property Damage Folder
#     casefile.property_damage_folder_id = create_folder(current_user.access_token, "Property Damage", casefile.main_folder_id)
#         # Commit The Database
#     db.session.commit()
#     flash("Done generating case skeleton", "is-info")
#   else:
#     abort(400)
#   return redirect(url_for("casefile.details",tenant_name=tenant_name, casefile_id = casefile_id))
@drive_integration.route('/<tenant_name>/casefile/<int:casefile_id>/google/new/skeleton')
@login_required
def generate_case_skeleton(tenant_name, casefile_id):
    validate_tenant(tenant_name)
    
    # Fetch the tenant and casefile
    tenant = Tenant.query.filter_by(id=session['tenant_id']).first_or_404()
    casefile = Casefile.query.filter_by(id=casefile_id, tenant_id=session['tenant_id']).first_or_404()
    
    root_folder_id = os.environ.get("CASES_ROOT_ID")

    if not root_folder_id:
        flash("Root folder ID is not configured.", "is-danger")
        abort(400)

    # Ensure the access token is valid
    if not check_access_token(current_user.token_expiration):
        abort(400)

    # Check if the tenant folder already exists
    if tenant.folder_id:
        # Use the existing tenant folder
        tenant_folder_id = tenant.folder_id
        flash(f"Using existing folder for tenant: {tenant.name}", "is-info")
    else:
        # Create a new tenant folder and store its ID
        tenant_folder_id = create_folder(current_user.access_token, tenant_name, root_folder_id)
        tenant.folder_id = tenant_folder_id
        db.session.commit()
        flash(f"Created new folder for tenant: {tenant.name}", "is-info")

    # Check if the case folder already exists
    

    # Create Main Folder and Subfolders
    try:
        casefile.main_folder_id = create_folder(current_user.access_token, casefile.case_label, tenant_folder_id)
        casefile.client_documentation_folder_id = create_folder(current_user.access_token, "Client Documentation", casefile.main_folder_id)
        casefile.subrogation_folder_id = create_folder(current_user.access_token, "Subrogation", casefile.main_folder_id)
        casefile.medical_record_folder_id = create_folder(current_user.access_token, "Medical Records", casefile.main_folder_id)
        casefile.first_party_folder_id = create_folder(current_user.access_token, "1st Party", casefile.main_folder_id)
        casefile.third_party_folder_id = create_folder(current_user.access_token, "3rd Party", casefile.main_folder_id)
        casefile.checks_folder_id = create_folder(current_user.access_token, "Checks", casefile.main_folder_id)
        casefile.litigation_folder_id = create_folder(current_user.access_token, "Litigation", casefile.main_folder_id)
        casefile.pics_and_videos_folder_id = create_folder(current_user.access_token, "Pics and Videos", casefile.main_folder_id)
        casefile.property_damage_folder_id = create_folder(current_user.access_token, "Property Damage", casefile.main_folder_id)

        # Commit The Database
        db.session.commit()
        flash("Case skeleton generated successfully.", "is-success")
    except Exception as e:
        db.session.rollback()
        flash(f"Error generating case skeleton: {str(e)}", "is-danger")
        abort(500)

    return redirect(url_for("casefile.details", tenant_name=tenant_name, casefile_id=casefile_id))



# Generate All First Party LORS
@drive_integration.route('/<tenant_name>/casefile/<int:casefile_id>/copy-all-first-party-lor')
@login_required
def copy_first_party_lor(tenant_name,casefile_id):
    validate_tenant(tenant_name)
    # casefile = db.get_or_404(Casefile, casefile_id)
    casefile = Casefile.query.filter_by(id=casefile_id,  tenant_id=session['tenant_id']).first_or_404()
    first_party_lor = os.environ.get("FIRST_PARTY_LOR_TEMPLATE")
    todays_date = date.today()
    todays_date = todays_date.strftime("%B %d, %Y")
    date_of_loss = casefile.date_of_loss
    date_of_loss = date_of_loss.strftime("%B %d, %Y")

    if check_access_token(current_user.token_expiration):
        # Create Each Claim
        for auto_claim in casefile.first_party_claims:
            # Copy Template
            file_id = copy_template(current_user.access_token, first_party_lor, f"First Party LOR - {auto_claim.auto_insurance.name}", casefile.first_party_folder_id)
            # Build Json Body For Batch Update
            flag_pairs = [
                ("Clients_AutoInsurer::name", auto_claim.auto_insurance.name),
                ("Clients_Adjuster::fullName", auto_claim.auto_adjuster.full_name),
                ("adjuster_street_address", auto_claim.auto_adjuster.street_address),
                ("adjuster_city", auto_claim.auto_adjuster.city),
                ("adjuster_state", auto_claim.auto_adjuster.state),
                ("adjuster_zip_code", auto_claim.auto_adjuster.zip_code),
                ("Clients_Adjuster::fax", auto_claim.auto_adjuster.fax),
                ("Client::fullName", auto_claim.casefile.client_list),
                ("Clients_Claim::claimNumber", auto_claim.claim_number),
                ("Wreck::date", date_of_loss),
                ("Wreck::city", auto_claim.casefile.wreck_city),
                ("Wreck::state", auto_claim.casefile.wreck_state),
                ("$$fullDate", todays_date)
            ]
            json_body = build_json_body(*flag_pairs)
            # Batch Update File
            result = batch_update_file(current_user.access_token, file_id, json_body)
            if result == 200:
                flash("First Party LOR batch update was successful", "is-success")
            else:
                flash(f"First Party LOR batch update returned an error code, {result}", "is-danger")
        flash("Done generating First Party LOR", "is-info")
    return redirect(url_for("casefile.details",tenant_name=tenant_name, casefile_id = casefile_id))

# Generate All Third Party LORS
@drive_integration.route('/<tenant_name>/casefile/<int:casefile_id>/copy-all-third-party-lor')
@login_required
def copy_third_party_lor(tenant_name,casefile_id):
    validate_tenant(tenant_name)
    # casefile = db.get_or_404(Casefile, casefile_id)
    casefile = Casefile.query.filter_by(id=casefile_id,  tenant_id=session['tenant_id']).first_or_404()
    third_party_lor = os.environ.get("THIRD_PARTY_LOR_TEMPLATE")
    todays_date = date.today()
    todays_date = todays_date.strftime("%B %d, %Y")
    date_of_loss = casefile.date_of_loss
    date_of_loss = date_of_loss.strftime("%B %d, %Y")

    if check_access_token(current_user.token_expiration):
        # Create Each Claim
        for defendant in casefile.defendants:
            # Copy Template
            file_id = copy_template(current_user.access_token, third_party_lor, f"Third Party LOR - {defendant.auto_insurance.name}", casefile.third_party_folder_id)
            # Build Json Body for Batch Update
            flag_pairs = [
                ("Defendants_AutoInsurer::name", defendant.auto_insurance.name),
                ("Defendants_Adjuster::fullName", defendant.auto_claim.auto_adjuster.full_name),
                ("adjuster_street_address", defendant.auto_claim.auto_adjuster.street_address),
                ("adjuster_city", defendant.auto_claim.auto_adjuster.city),
                ("adjuster_state", defendant.auto_claim.auto_adjuster.state),
                ("adjuster_zip_code", defendant.auto_claim.auto_adjuster.zip_code),
                ("Defendants_Adjuster::fax", defendant.auto_claim.auto_adjuster.fax),
                ("Client::fullName", casefile.client_list),
                ("Defendant::fullName", defendant.full_name),
                ("Clients_Claim::claimNumber", defendant.auto_claim.claim_number),
                ("Wreck::date", date_of_loss),
                ("Wreck::city", casefile.wreck_city),
                ("Wreck::state", casefile.wreck_state),
                ("$$fullDate", todays_date)
            ]
            json_body = build_json_body(*flag_pairs)
            # Batch Update File
            result = batch_update_file(current_user.access_token, file_id, json_body)
            if result == 200:
                flash("Third Party LOR batch update was successful", "is-success")
            else:
                flash(f"Third Party LOR batch update returned an error code, {result}", "is-danger")
        flash("Done generating Third Party LOR", "is-info")
    return redirect(url_for("casefile.details",tenant_name=tenant_name, casefile_id = casefile_id))

# Generate All Client Engagement Letters
@drive_integration.route('/<tenant_name>/casefile/<int:casefile_id>/copy-client-engagement-letter')
@login_required
def copy_client_engagement_letter(tenant_name,casefile_id):
    # casefile = db.get_or_404(Casefile, casefile_id)
    validate_tenant(tenant_name)
    casefile = Casefile.query.filter_by(id=casefile_id,  tenant_id=session['tenant_id']).first_or_404()
    client_engagement_letter = os.environ.get("CLIENT_ENGAGEMENT_LETTER_TEMPLATE")
    todays_date = date.today()
    todays_date = todays_date.strftime("%B %d, %Y")

    if check_access_token(current_user.token_expiration):
        # Create Each Claim
        for client in casefile.clients:
            # Copy Template
            file_id = copy_template(current_user.access_token, client_engagement_letter, f"Client Engagement Letter - {client.full_name}", casefile.client_documentation_folder_id)
            # Build Json Body for Batch Update
            flag_pairs = [
                ("$$fullDate", todays_date),
                ("Client::fullName", client.full_name),
                ("Client::streetAddress", client.street_address),
                ("Client::city", client.city),
                ("Client::state", client.state),
                ("Client::zip", client.zip_code)
            ]
            json_body = build_json_body(*flag_pairs)
            # Batch Update File
            result = batch_update_file(current_user.access_token, file_id, json_body)
            if result == 200:
                flash("Client engagement letter batch update was successful", "is-success")
            else:
                flash(f"Client engagement letter batch update returned an error code, {result}", "is-danger")
        flash("Done generating Client engagement letter", "is-info")
    return redirect(url_for("casefile.details",tenant_name=tenant_name, casefile_id = casefile_id))

# Generate All Withdrawal Letters
@drive_integration.route('/<tenant_name>/casefile/<int:casefile_id>/copy-withdrawal-letter')
@login_required
def copy_withdrawal_letter(tenant_name,casefile_id):
    validate_tenant(tenant_name)
    # casefile = db.get_or_404(Casefile, casefile_id)
    casefile = Casefile.query.filter_by(id=casefile_id,  tenant_id=session['tenant_id']).first_or_404()
    withdrawal_letter = os.environ.get("WITHDRAWAL_LETTER_TEMPLATE")
    todays_date = date.today()
    todays_date = todays_date.strftime("%B %d, %Y")
    date_of_loss = casefile.date_of_loss
    date_of_loss = date_of_loss.strftime("%B %d, %Y")

    if check_access_token(current_user.token_expiration):
        # Create Each Claim
        for client in casefile.clients:
            # Copy Template
            file_id = copy_template(current_user.access_token, withdrawal_letter, f"Withdrawal Letter - {client.full_name}", casefile.main_folder_id)
            # Build Json Body for Batch Update
            flag_pairs = [
                ("$$fullDate", todays_date),
                ("client.fullName", client.full_name),
                ("client.street_address", client.street_address),
                ("client.city", client.city),
                ("client.state", client.state),
                # ADD STATUTE OF LIMITATIONS FIELD
                ("client.zip_code", client.zip_code)
            ]
            json_body = build_json_body(*flag_pairs)
            # Batch Update File
            result = batch_update_file(current_user.access_token, file_id, json_body)
            if result == 200:
                flash("Withdrawal letter batch update was successful", "is-success")
            else:
                flash(f"Withdrawal letter batch update returned an error code, {result}", "is-danger")
        flash("Done generating Withdrawal letter", "is-info")
    return redirect(url_for("casefile.details",tenant_name=tenant_name, casefile_id = casefile_id))

# Generate All Subrogation LORs
@drive_integration.route('/<tenant_name>/casefile/<int:casefile_id>/copy-subrogation-lor')
@login_required
def copy_subrogation_lor(tenant_name,casefile_id):
    validate_tenant(tenant_name)
    # casefile = db.get_or_404(Casefile, casefile_id)
    casefile = Casefile.query.filter_by(id=casefile_id,  tenant_id=session['tenant_id']).first_or_404()
    subrogation_lor = os.environ.get("HEALTH_CLAIM_LOR_TEMPLATE")
    todays_date = date.today()
    todays_date = todays_date.strftime("%B %d, %Y")
    date_of_loss = casefile.date_of_loss
    date_of_loss = date_of_loss.strftime("%B %d, %Y")

    if check_access_token(current_user.token_expiration):
        # Create Each Claim
        for client in casefile.clients:
            for health_claim in client.health_claims:
                # Copy Template
                file_id = copy_template(current_user.access_token, subrogation_lor, f"Subrogation LOR - {client.full_name} to {health_claim.health_insurance.name}", casefile.subrogation_folder_id)
                # Build Json Body for Batch Update
                flag_pairs = [
                    ("$$fullDate", todays_date),
                    ("health_claim.health_insurance.name", health_claim.health_insurance.name),
                    ("health_claim.health_adjuster.fax", health_claim.health_insurance.fax_1),
                    ("client.fullName", client.full_name),
                    ("health_claim.member_id", health_claim.member_id),
                    ("client.dob", client.dob.strftime('%m/%d/%Y')),
                    ("date_of_loss", date_of_loss),
                    ("wreck_city", casefile.wreck_city),
                    ("wreck_state", casefile.wreck_state),
                    ("medical_provider.name", client.medical_provider_list)
                ]
                json_body = build_json_body(*flag_pairs)
                # Batch Update File
                result = batch_update_file(current_user.access_token, file_id, json_body)
                if result == 200:
                    flash("Subrogation LOR batch update was successful", "is-success")
                else:
                    flash(f"Subrogation LOR batch update returned an error code, {result}", "is-danger")
            flash("Done generating Subrogation LOR", "is-info")
    return redirect(url_for("casefile.details",tenant_name=tenant_name, casefile_id = casefile_id))

# Generate AdHoc Subrogation LOR
@drive_integration.route('/<tenant_name>/generate-adhoc-subrogation-lor/client/<int:client_id>/healthinsurer/<int:health_insurance_id>')
@login_required
def generate_adhoc_subrogation_lor(tenant_name,client_id, health_insurance_id):
    validate_tenant(tenant_name)
    # health_claim = db.get_or_404(HealthClaim, (client_id, health_insurance_id))
    health_claim = HealthClaim.query.filter_by(client_id=client_id,health_insurance_id=health_insurance_id,  tenant_id=session['tenant_id']).first_or_404()
    subrogation_lor = os.environ.get("HEALTH_CLAIM_LOR_TEMPLATE")
    todays_date = date.today()
    todays_date = todays_date.strftime("%B %d, %Y")
    date_of_loss = health_claim.client.casefile.date_of_loss
    date_of_loss = date_of_loss.strftime("%B %d, %Y")

    if check_access_token(current_user.token_expiration):
        # Copy Template
        file_id = copy_template(current_user.access_token, subrogation_lor, f"Subrogation LOR - {health_claim.client.full_name} to {health_claim.health_insurance.name}", health_claim.client.casefile.subrogation_folder_id)
        # Build Json Body for Batch Update
        flag_pairs = [
            ("$$fullDate", todays_date),
            ("health_claim.health_insurance.name", health_claim.health_insurance.name),
            ("health_claim.health_adjuster.fax", health_claim.health_insurance.fax_1),
            ("client.fullName", health_claim.client.full_name),
            ("health_claim.member_id", health_claim.member_id),
            ("client.dob", health_claim.client.dob.strftime('%m/%d/%Y')),
            ("date_of_loss", date_of_loss),
            ("wreck_city", health_claim.client.casefile.wreck_city),
            ("wreck_state", health_claim.client.casefile.wreck_state),
            ("medical_provider.name", health_claim.client.medical_provider_list)
        ]
        json_body = build_json_body(*flag_pairs)
        # Batch Update File
        result = batch_update_file(current_user.access_token, file_id, json_body)
        if result == 200:
            flash("Subrogation LOR batch update was successful", "is-success")
        else:
            flash(f"Subrogation LOR batch update returned an error code, {result}", "is-danger")
    flash("Done generating Subrogation LOR", "is-info")
    return redirect(url_for("casefile.details",tenant_name=tenant_name, casefile_id = health_claim.client.casefile_id))

# Generate All Contracts
@drive_integration.route('/<tenant_name>/casefile/<int:casefile_id>/copy-contract')
@login_required
def copy_contract(tenant_name , casefile_id):
    validate_tenant(tenant_name)
    # casefile = db.get_or_404(Casefile, casefile_id)
    casefile = Casefile.query.filter_by(id=casefile_id,  tenant_id=session['tenant_id']).first_or_404()
    contract = os.environ.get("CONTRACT_TEMPLATE")
    todays_date = date.today()
    todays_date_string = todays_date.strftime("%B %d, %Y")
    todays_day_string = todays_date.strftime("%d")
    todays_month_string = todays_date.strftime("%B")
    todays_year_string = todays_date.strftime("%Y")

    if check_access_token(current_user.token_expiration):
        # Create Each Contract
        for client in casefile.clients:
            # Copy Template
            file_id = copy_template(current_user.access_token, contract, f"Contract - {client.full_name}", casefile.client_documentation_folder_id)
            # Build Json Body for Batch Update
            flag_pairs = [
                ("$$dayDate", todays_day_string),
                ("$$monthDate", todays_month_string),
                ("$$yearDate", todays_year_string),
                ("$$fullDate", todays_date_string),
                ("Wreck::county", casefile.wreck_county),
                ("Wreck::state", casefile.wreck_state),
                ("Client::fullName", client.full_name)
            ]
            json_body = build_json_body(*flag_pairs)
            # Batch Update File
            result = batch_update_file(current_user.access_token, file_id, json_body)
            if result == 200:
                flash("Contract batch update was successful", "is-success")
            else:
                flash(f"Contract batch update returned an error code, {result}", "is-danger")
        flash("Done generating Contract", "is-info")
    return redirect(url_for("casefile.details",tenant_name=tenant_name, casefile_id = casefile_id))

# Generate All Medical Bill HIPAAs
@drive_integration.route('/<tenant_name>/casefile/<int:casefile_id>/generate-all-medical-bill-hipaas')
@login_required
def generate_all_medical_hipaas(tenant_name , casefile_id):
    validate_tenant(tenant_name)
    # casefile = db.get_or_404(Casefile, casefile_id)
    casefile = Casefile.query.filter_by(id=casefile_id,  tenant_id=session['tenant_id']).first_or_404()
    hipaa = os.environ.get("HIPAA_TEMPLATE")
    date_of_loss = casefile.date_of_loss
    date_of_loss = date_of_loss.strftime("%B %d, %Y")

    if check_access_token(current_user.token_expiration):
        # Create Each Claim
        for client in casefile.clients:
            for medical_bill in client.medical_bills:
                # Copy Template
                file_id = copy_template(current_user.access_token, hipaa, f"HIPAA - {medical_bill.medical_provider.name} for {client.full_name}", casefile.client_documentation_folder_id)
                # Build Json Body for Batch Update
                flag_pairs = [
                    ("MedicalProvider::name", medical_bill.medical_provider.name),
                    ("MedicalProvider::streetAddress", medical_bill.medical_provider.street_address),
                    ("MedicalProvider::city", medical_bill.medical_provider.city),
                    ("MedicalProvider::state", medical_bill.medical_provider.state),
                    ("MedicalProvider::zip", medical_bill.medical_provider.zip_code),
                    ("Client::fullName", client.full_name),
                    ("Client::dateOfBirth", client.dob.strftime('%m/%d/%Y')),
                    ("Client::socialSecurityNumber", client.ssn),
                    ("$$fullDate", date_of_loss),
                ]
                json_body = build_json_body(*flag_pairs)
                # Batch Update File
                result = batch_update_file(current_user.access_token, file_id, json_body)
                if result == 200:
                    flash("HIPAA batch update was successful", "is-success")
                else:
                    flash(f"HIPAA batch update returned an error code, {result}", "is-danger")
            flash("Done generating HIPAA", "is-info")
    return redirect(url_for("casefile.details",tenant_name=tenant_name, casefile_id = casefile_id))
# Generate AdHoc Medical Bill HIPAA
# Generate AdHoc Medical Bill HIPAA
@drive_integration.route('/<tenant_name>/generate-adhoc-medical-bill-hipaa/client/<int:client_id>/medprovider/<int:medical_provider_id>')
@login_required
def generate_adhoc_medical_hipaa(tenant_name, client_id, medical_provider_id):
    validate_tenant(tenant_name)
    
    # Get the medical bill or raise a 404 error
    medical_bill = MedicalBill.query.filter_by(
        client_id=client_id,
        medical_provider_id=medical_provider_id,
        tenant_id=session['tenant_id']
    ).first_or_404()
    
    # Fetch the HIPAA template from environment variable
    hipaa = os.environ.get("HIPAA_TEMPLATE")
    
    
    # Format the date of loss
    date_of_loss = medical_bill.client.casefile.date_of_loss
    date_of_loss = date_of_loss.strftime("%B %d, %Y")
    
    # # Check and handle the token expiration
    # if current_user.token_expiration is None:
    #     flash("User token expiration is not set. Please log in again.", "is-danger")
    #     return redirect(url_for("auth.login"))  # Redirect to login if token is invalid or missing
    
    # Validate the token expiration
    if check_access_token(current_user.token_expiration):

        # Ensure access token is available
        # if not current_user.access_token:
        #     raise ValueError("Access token is not available.")
        
        # # Ensure the client documentation folder ID is available
        # if not medical_bill.client.casefile.client_documentation_folder_id:
        #     raise ValueError("Client documentation folder ID is missing.")
        
        # Copy template
        file_id = copy_template(
            current_user.access_token,
            hipaa,
            f"HIPAA - {medical_bill.medical_provider.name} for {medical_bill.client.full_name}",
            medical_bill.client.casefile.client_documentation_folder_id
        )
        

        # Build JSON body for batch update
        flag_pairs = [
            ("MedicalProvider::name", medical_bill.medical_provider.name),
            ("MedicalProvider::streetAddress", medical_bill.medical_provider.street_address),
            ("MedicalProvider::city", medical_bill.medical_provider.city),
            ("MedicalProvider::state", medical_bill.medical_provider.state),
            ("MedicalProvider::zip", medical_bill.medical_provider.zip_code),
            ("Client::fullName", medical_bill.client.full_name),
            ("Client::dateOfBirth", medical_bill.client.dob.strftime('%m/%d/%Y')) ,
            ("Client::socialSecurityNumber", medical_bill.client.ssn),
            ("$$fullDate", date_of_loss),
        ]
        json_body = build_json_body(*flag_pairs)
        
        # Batch update file
        result = batch_update_file(current_user.access_token, file_id, json_body)
        if result == 200:
            flash("HIPAA batch update was successful", "is-success")
        else:
            flash(f"HIPAA batch update returned an error code, {result}", "is-danger")
    else:
        flash("Access token has expired. Please log in again.", "is-danger")
        return redirect(url_for("auth.login"))  # Redirect to login if token is expired
    
    flash("Done generating HIPAA", "is-info")
    return redirect(url_for("casefile.details", tenant_name=tenant_name, casefile_id=medical_bill.client.casefile_id))

# Generate All Health Claim HIPAAs
@drive_integration.route('/<tenant_name>/casefile/<int:casefile_id>/generate-all-health-claim-hipaas')
@login_required
def generate_all_health_hipaas(tenant_name,casefile_id):
    validate_tenant(tenant_name)
    # casefile = db.get_or_404(Casefile, casefile_id)
    casefile = Casefile.query.filter_by(id=casefile_id,  tenant_id=session['tenant_id']).first_or_404()
    hipaa = os.environ.get("HIPAA_TEMPLATE")
    date_of_loss = casefile.date_of_loss
    date_of_loss = date_of_loss.strftime("%B %d, %Y")

    if check_access_token(current_user.token_expiration):
        # Create Each Claim
        for client in casefile.clients:
            for health_claim in client.health_claims:
                # Copy Template
                file_id = copy_template(current_user.access_token, hipaa, f"HIPAA - {health_claim.health_insurance.name} for {client.full_name}", casefile.subrogation_folder_id)
                # Build Json Body for Batch Update
                flag_pairs = [
                    ("MedicalProvider::name", health_claim.health_insurance.name),
                    ("MedicalProvider::streetAddress", health_claim.health_insurance.street_address),
                    ("MedicalProvider::city", health_claim.health_insurance.city),
                    ("MedicalProvider::state", health_claim.health_insurance.state),
                    ("MedicalProvider::zip", health_claim.health_insurance.zip_code),
                    ("Client::fullName", client.full_name),
                    ("Client::dateOfBirth", client.dob.strftime('%m/%d/%Y')),
                    ("Client::socialSecurityNumber", client.ssn),
                    ("$$fullDate", date_of_loss),
                ]
                json_body = build_json_body(*flag_pairs)
                # Batch Update File
                result = batch_update_file(current_user.access_token, file_id, json_body)
                if result == 200:
                    flash("HIPAA batch update was successful", "is-success")
                else:
                    flash(f"HIPAA batch update returned an error code, {result}", "is-danger")
            flash("Done generating HIPAA", "is-info")
    return redirect(url_for("casefile.details",tenant_name=tenant_name, casefile_id = casefile_id))

# Generate AdHoc Health Claim HIPAA
@drive_integration.route('/<tenant_name>/generate-adhoc-health-claim-hipaa/client/<int:client_id>/healthinsurance/<int:health_insurance_id>')
@login_required
def generate_adhoc_health_hipaa(tenant_name,client_id, health_insurance_id):
    validate_tenant(tenant_name)
    # health_claim = db.get_or_404(HealthClaim, (client_id, health_insurance_id))
    health_claim = HealthClaim.query.filter_by(client_id=client_id,health_insurance_id=health_insurance_id,  tenant_id=session['tenant_id']).first_or_404()
    hipaa = os.environ.get("HIPAA_TEMPLATE")
    date_of_loss = health_claim.client.casefile.date_of_loss
    date_of_loss = date_of_loss.strftime("%B %d, %Y")

    if check_access_token(current_user.token_expiration):
        # Copy Template
        file_id = copy_template(current_user.access_token, hipaa, f"HIPAA - {health_claim.health_insurance.name} for {health_claim.client.full_name}", health_claim.client.casefile.subrogation_folder_id)
        # Build Json Body for Batch Update
        flag_pairs = [
            ("MedicalProvider::name", health_claim.health_insurance.name),
            ("MedicalProvider::streetAddress", health_claim.health_insurance.street_address),
            ("MedicalProvider::city", health_claim.health_insurance.city),
            ("MedicalProvider::state", health_claim.health_insurance.state),
            ("MedicalProvider::zip", health_claim.health_insurance.zip_code),
            ("Client::fullName", health_claim.client.full_name),
            ("Client::dateOfBirth", health_claim.client.dob.strftime('%m/%d/%Y')),
            ("Client::socialSecurityNumber", health_claim.client.ssn),
            ("$$fullDate", date_of_loss),
        ]
        json_body = build_json_body(*flag_pairs)
        # Batch Update File
        result = batch_update_file(current_user.access_token, file_id, json_body)
        if result == 200:
            flash("HIPAA batch update was successful", "is-success")
        else:
            flash(f"HIPAA batch update returned an error code, {result}", "is-danger")
    flash("Done generating HIPAA", "is-info")
    return redirect(url_for("casefile.details",tenant_name=tenant_name, casefile_id = health_claim.client.casefile_id))

# Generate Check Payment Log
@drive_integration.route('/<tenant_name>/casefile/<int:casefile_id>/copy-check-payment-log')
@login_required
def copy_check_payment_log(tenant_name,casefile_id):
    validate_tenant(tenant_name)
    # casefile = db.get_or_404(Casefile, casefile_id)
    casefile = Casefile.query.filter_by(id=casefile_id,  tenant_id=session['tenant_id']).first_or_404()
    check_payment_log = os.environ.get("CHECK_PAYMENT_LOG_TEMPLATE")

    if check_access_token(current_user.token_expiration):
        # Copy Template
        try:
            copy_template(current_user.access_token, check_payment_log, "Check Payment Log", casefile.checks_folder_id, mime_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
        except:
            flash(f"Check Payment Log Template returned an error", "is-danger")

    flash("Done generating Check Payment Log", "is-info")
    return redirect(url_for("casefile.details",tenant_name=tenant_name, casefile_id = casefile_id))

# Generate All Demands
@drive_integration.route('/<tenant_name>/casefile/<int:casefile_id>/copy-all-demands')
@login_required
def copy_demand(tenant_name,casefile_id):
    validate_tenant(tenant_name)
    # casefile = db.get_or_404(Casefile, casefile_id)
    casefile = Casefile.query.filter_by(id=casefile_id,  tenant_id=session['tenant_id']).first_or_404()
    if casefile.wreck_type == "REAR END":
        demand = os.environ.get("REAR_END_DEMAND_TEMPLATE")
    elif casefile.wreck_type == "LANE CHANGE":
        demand = os.environ.get("LANE_CHANGE_DEMAND_TEMPLATE")
    elif casefile.wreck_type == "T BONE":
        demand = os.environ.get("T_BONE_DEMAND_TEMPLATE")
    todays_date = date.today()
    todays_date = todays_date.strftime("%B %d, %Y")
    date_of_loss = casefile.date_of_loss
    date_of_loss = date_of_loss.strftime("%B %d, %Y")
    
    if check_access_token(current_user.token_expiration):
        # Create Each Claim
        for defendant in casefile.defendants:
            # Copy Template
            file_id = copy_template(current_user.access_token, demand, f"Demand - {defendant.auto_claim.auto_insurance.name}", casefile.main_folder_id)
            # Build Json Body for Batch Update
            flag_pairs = [
                ("Defendants_AutoInsurer::name", defendant.auto_claim.auto_insurance.name),
                ("Defendants_Adjuster::fullName", defendant.auto_claim.auto_adjuster.full_name),
                ("adjuster_street_address", defendant.auto_claim.auto_adjuster.street_address),
                ("adjuster_city", defendant.auto_claim.auto_adjuster.city),
                ("adjuster_state", defendant.auto_claim.auto_adjuster.state),
                ("adjuster_zip_code", defendant.auto_claim.auto_adjuster.zip_code),
                ("Defendants_Adjuster::fax", defendant.auto_claim.auto_adjuster.fax),
                ("Clients_Claim::claimNumber", defendant.auto_claim.claim_number),
                ("Defendant::fullName", defendant.full_name),
                ("Wreck::date", date_of_loss),
                ("client.list", casefile.client_list),
                ("Wreck::street", casefile.wreck_street),
                ("Wreck::city", casefile.wreck_city),
                ("Wreck::state", casefile.wreck_state),
                ("$$fullDate", todays_date)
            ]
            json_body = build_json_body(*flag_pairs)
            # Batch Update File
            result = batch_update_file(current_user.access_token, file_id, json_body)
            if result == 200:
                flash("Demand batch update was successful", "is-success")
            else:
                flash(f"Demand batch update returned an error code, {result}", "is-danger")
        flash("Done generating Demand", "is-info")
    return redirect(url_for("casefile.details",tenant_name=tenant_name, casefile_id = casefile_id))

# Generate AdHoc Demand
@drive_integration.route('/<tenant_name>/generate-adhoc-demand/defendant/<int:defendant_id>/autoinsurance/<int:auto_insurance_id>')
@login_required
def generate_adhoc_demand(tenant_name,defendant_id, auto_insurance_id):
    validate_tenant(tenant_name)
    # third_party_claim = db.get_or_404(ThirdPartyClaim, (defendant_id, auto_insurance_id))
    third_party_claim = ThirdPartyClaim.query.filter_by(defendant_id=defendant_id,auto_insurance_id=auto_insurance_id,  tenant_id=session['tenant_id']).first_or_404()
    if third_party_claim.defendant.casefile.wreck_type == "REAR END":
        demand = os.environ.get("REAR_END_DEMAND_TEMPLATE")
    elif third_party_claim.defendant.casefile.wreck_type == "LANE CHANGE":
        demand = os.environ.get("LANE_CHANGE_DEMAND_TEMPLATE")
    elif third_party_claim.defendant.casefile.wreck_type == "T BONE":
        demand = os.environ.get("T_BONE_DEMAND_TEMPLATE")
    todays_date = date.today()
    todays_date = todays_date.strftime("%B %d, %Y")
    date_of_loss = third_party_claim.defendant.casefile.date_of_loss
    date_of_loss = date_of_loss.strftime("%B %d, %Y")

    if check_access_token(current_user.token_expiration):
        # Copy Template
        file_id = copy_template(current_user.access_token, demand, f"Demand - {third_party_claim.auto_insurance.name}", third_party_claim.defendant.casefile.main_folder_id)
        # Build Json Body for Batch Update
        flag_pairs = [
            ("Defendants_AutoInsurer::name", third_party_claim.auto_insurance.name),
            ("Defendants_Adjuster::fullName", third_party_claim.auto_adjuster.full_name),
            ("adjuster_street_address", third_party_claim.auto_adjuster.street_address),
            ("adjuster_city", third_party_claim.auto_adjuster.city),
            ("adjuster_state", third_party_claim.auto_adjuster.state),
            ("adjuster_zip_code", third_party_claim.auto_adjuster.zip_code),
            ("Defendants_Adjuster::fax", third_party_claim.auto_adjuster.fax),
            ("Clients_Claim::claimNumber", third_party_claim.claim_number),
            ("Defendant::fullName", third_party_claim.defendant.full_name),
            ("Wreck::date", date_of_loss),
            ("client.list", third_party_claim.defendant.casefile.client_list),
            ("Wreck::street", third_party_claim.defendant.casefile.wreck_street),
            ("Wreck::city", third_party_claim.defendant.casefile.wreck_city),
            ("Wreck::state", third_party_claim.defendant.casefile.wreck_state),
            ("$$fullDate", todays_date)
        ]
        json_body = build_json_body(*flag_pairs)
        # Batch Update File
        result = batch_update_file(current_user.access_token, file_id, json_body)
        if result == 200:
            flash("Demand batch update was successful", "is-success")
        else:
            flash(f"Demand batch update returned an error code, {result}", "is-danger")
    flash("Done generating Demand", "is-info")
    return redirect(url_for("casefile.details",tenant_name=tenant_name, casefile_id = third_party_claim.defendant.casefile_id))

# Generate All MedPay Demands
@drive_integration.route('/<tenant_name>/casefile/<int:casefile_id>/copy-all-medpay-demands')
@login_required
def copy_medpay_demand(tenant_name,casefile_id):
    validate_tenant(tenant_name)
    # casefile = db.get_or_404(Casefile, casefile_id)
    casefile = Casefile.query.filter_by(id=casefile_id,  tenant_id=session['tenant_id']).first_or_404()
    demand = os.environ.get("MEDPAY_DEMAND_TEMPLATE")
    todays_date = date.today()
    todays_date = todays_date.strftime("%B %d, %Y")
    date_of_loss = casefile.date_of_loss
    date_of_loss = date_of_loss.strftime("%B %d, %Y")

    if check_access_token(current_user.token_expiration):
        # Create Each Claim
        for first_party_claim in casefile.first_party_claims:
            if first_party_claim.has_medpay == "True":
                # Copy Template
                file_id = copy_template(current_user.access_token, demand, f"Medpay Demand - {first_party_claim.auto_insurance.name}", casefile.main_folder_id)
                # Build Json Body for Batch Update
                flag_pairs = [
                    ("AutoInsurer::name", first_party_claim.auto_insurance.name),
                    ("Defendants_Adjuster::fullName", first_party_claim.auto_adjuster.full_name),
                    ("adjuster_street_address", first_party_claim.auto_adjuster.street_address),
                    ("adjuster_city", first_party_claim.auto_adjuster.city),
                    ("adjuster_state", first_party_claim.auto_adjuster.state),
                    ("adjuster_zip_code", first_party_claim.auto_adjuster.zip_code),
                    ("Adjuster::fax", first_party_claim.auto_adjuster.fax),
                    ("Client::fullName", first_party_claim.casefile.client_list),
                    ("Clients_Claim::claimNumber", first_party_claim.claim_number),
                    ("$$fullDate", todays_date)
                ]
                json_body = build_json_body(*flag_pairs)
                # Batch Update File
                result = batch_update_file(current_user.access_token, file_id, json_body)
                if result == 200:
                    flash("MP Demand batch update was successful", "is-success")
                else:
                    flash(f"MP Demand batch update returned an error code, {result}", "is-danger")
                flash("Done generating MP Demand", "is-info")
            else:
                flash("One or more policies does not have MedPay recorded on file. Please check your records and update the claim information if necessary.", "is-warning")
    return redirect(url_for("casefile.details",tenant_name=tenant_name, casefile_id = casefile_id))

# Generate Adhoc MedPay Demands
@drive_integration.route('/<tenant_name>/generate-adhoc-medpay-demand/casefile/<int:casefile_id>/autoinsurance/<int:auto_insurance_id>')
@login_required
def generate_adhoc_medpay_demand(tenant_name,casefile_id, auto_insurance_id):
    validate_tenant(tenant_name)
    # first_party_claim = db.get_or_404(FirstPartyClaim, (casefile_id, auto_insurance_id))
    first_party_claim = FirstPartyClaim.query.filter_by(casefile_id=casefile_id,auto_insurance_id=auto_insurance_id,  tenant_id=session['tenant_id']).first_or_404()
    demand = os.environ.get("MEDPAY_DEMAND_TEMPLATE")
    todays_date = date.today()
    todays_date = todays_date.strftime("%B %d, %Y")
    date_of_loss = first_party_claim.casefile.date_of_loss
    date_of_loss = date_of_loss.strftime("%B %d, %Y")

    if check_access_token(current_user.token_expiration):
        # Create Each Claim
        if first_party_claim.has_medpay == "True":
            # Copy Template
            file_id = copy_template(current_user.access_token, demand, f"Medpay Demand - {first_party_claim.auto_insurance.name}", first_party_claim.casefile.main_folder_id)
            # Build Json Body for Batch Update
            flag_pairs = [
                ("AutoInsurer::name", first_party_claim.auto_insurance.name),
                ("Defendants_Adjuster::fullName", first_party_claim.auto_adjuster.full_name),
                ("adjuster_street_address", first_party_claim.auto_adjuster.street_address),
                ("adjuster_city", first_party_claim.auto_adjuster.city),
                ("adjuster_state", first_party_claim.auto_adjuster.state),
                ("adjuster_zip_code", first_party_claim.auto_adjuster.zip_code),
                ("Adjuster::fax", first_party_claim.auto_adjuster.fax),
                ("Client::fullName", first_party_claim.casefile.client_list),
                ("Clients_Claim::claimNumber", first_party_claim.claim_number),
                ("$$fullDate", todays_date)
            ]
            json_body = build_json_body(*flag_pairs)
            # Batch Update File
            result = batch_update_file(current_user.access_token, file_id, json_body)
            if result == 200:
                flash("MP Demand batch update was successful", "is-success")
            else:
                flash(f"MP Demand batch update returned an error code, {result}", "is-danger")
            flash("Done generating MP Demand", "is-info")
        else:
            flash("This policy does not have MedPay recorded on file. Please check your records and update the claim information if necessary.", "is-warning")
    return redirect(url_for("casefile.details",tenant_name=tenant_name, casefile_id = casefile_id))

# Generate Counter Demand
@drive_integration.route('/<tenant_name>/generate-counter-demand/defendant/<int:defendant_id>/autoinsurance/<int:auto_insurance_id>')
@login_required
def generate_counter_demand(tenant_name , defendant_id, auto_insurance_id):
    validate_tenant(tenant_name)
    # third_party_claim = db.get_or_404(ThirdPartyClaim, (defendant_id, auto_insurance_id))
    third_party_claim = ThirdPartyClaim.query.filter_by(defendant_id=defendant_id,auto_insurance_id=auto_insurance_id,  tenant_id=session['tenant_id']).first_or_404()
    demand = os.environ.get("COUNTER_DEMAND_TEMPLATE")
    todays_date = date.today()
    todays_date = todays_date.strftime("%B %d, %Y")
    date_of_loss = third_party_claim.defendant.casefile.date_of_loss
    date_of_loss = date_of_loss.strftime("%B %d, %Y")

    if check_access_token(current_user.token_expiration):
        # Copy Template
        file_id = copy_template(current_user.access_token, demand, f"Counter - {third_party_claim.auto_insurance.name}", third_party_claim.defendant.casefile.main_folder_id)
        # Build Json Body for Batch Update
        flag_pairs = [
            ("third_party_claim.auto_insurance.name", third_party_claim.auto_insurance.name),
            ("auto_adjuster.full_name", third_party_claim.auto_adjuster.full_name),
            ("auto_adjuster_street_address", third_party_claim.auto_adjuster.street_address),
            ("auto_adjuster_city", third_party_claim.auto_adjuster.city),
            ("auto_adjuster_state", third_party_claim.auto_adjuster.state),
            ("auto_adjuster_zip_code", third_party_claim.auto_adjuster.zip_code),
            ("third_party_claim.auto_adjuster.fax", third_party_claim.auto_adjuster.fax),
            ("third_party_claim.claim_number", third_party_claim.claim_number),
            ("defendant.full_name", third_party_claim.defendant.full_name),
            ("date_of_loss", date_of_loss),
            ("client.list", third_party_claim.defendant.casefile.client_list),
            ("$$fullDate", todays_date)
        ]
        json_body = build_json_body(*flag_pairs)
        # Batch Update File
        result = batch_update_file(current_user.access_token, file_id, json_body)
        if result == 200:
            flash("Counter Demand batch update was successful", "is-success")
        else:
            flash(f"Counter Demand batch update returned an error code, {result}", "is-danger")
    flash("Done generating Counter Demand", "is-info")
    return redirect(url_for("casefile.details",tenant_name=tenant_name, casefile_id = third_party_claim.defendant.casefile_id))

# Generate All Proposed Settlement Statements
@drive_integration.route('/<tenant_name>/casefile/<int:casefile_id>/copy-proposed-settlement-statements')
@login_required
def copy_proposed_settlement_statement(tenant_name , casefile_id):
    validate_tenant(tenant_name)
    # casefile = db.get_or_404(Casefile, casefile_id)
    casefile = Casefile.query.filter_by(id=casefile_id,  tenant_id=session['tenant_id']).first_or_404()
    proposed_settlement_statement = os.environ.get("PROPOSED_SETTLEMENT_STATEMENT_TEMPLATE")
    todays_date = date.today()
    todays_date = todays_date.strftime("%B %d, %Y")
    date_of_loss = casefile.date_of_loss
    date_of_loss = date_of_loss.strftime("%B %d, %Y")

    if check_access_token(current_user.token_expiration):
        # Create Each Claim
        for defendant in casefile.defendants:
            for client in casefile.clients:
                # Copy Template
                file_id = copy_template(current_user.access_token, proposed_settlement_statement, f"PSS - {defendant.auto_claim.auto_insurance.name} {client.full_name}", casefile.main_folder_id)
                # Build Json Body for Batch Update
                flag_pairs = [
                    ("$$fullDate", todays_date),
                    ("client.fullName", client.full_name),
                    ("third_party_claim.auto_insurance.name", defendant.auto_claim.auto_insurance.name),
                    ("third_party_claim.claim_number", defendant.auto_claim.claim_number),
                    ("date_of_loss", date_of_loss),
                    ("medical_provider.list", client.medical_provider_list)
                ]
                json_body = build_json_body(*flag_pairs)
                # Batch Update File
                result = batch_update_file(current_user.access_token, file_id, json_body)
                if result == 200:
                    flash("PSS batch update was successful", "is-success")
                else:
                    flash(f"PSS batch update returned an error code, {result}", "is-danger")
        flash("Done generating PSS", "is-info")
    return redirect(url_for("casefile.details",tenant_name=tenant_name, casefile_id = casefile_id))

# Generate Adhoc Proposed Settlement Statements
@drive_integration.route('/<tenant_name>/generate-proposed-settlement-statement/defendant/<int:defendant_id>/autoinsurance/<int:auto_insurance_id>')
@login_required
def generate_adhoc_proposed_settlement_statement(tenant_name , defendant_id, auto_insurance_id):
    validate_tenant(tenant_name)
    # third_party_claim = db.get_or_404(ThirdPartyClaim, (defendant_id, auto_insurance_id))
    third_party_claim = ThirdPartyClaim.query.filter_by(defendant_id=defendant_id,auto_insurance_id=auto_insurance_id,  tenant_id=session['tenant_id']).first_or_404()
    proposed_settlement_statement = os.environ.get("PROPOSED_SETTLEMENT_STATEMENT_TEMPLATE")
    todays_date = date.today()
    todays_date = todays_date.strftime("%B %d, %Y")
    date_of_loss = third_party_claim.defendant.casefile.date_of_loss
    date_of_loss = date_of_loss.strftime("%B %d, %Y")

    if check_access_token(current_user.token_expiration):
        # Create Each Claim
        for client in third_party_claim.defendant.casefile.clients:
            # Copy Template
            file_id = copy_template(current_user.access_token, proposed_settlement_statement, f"PSS - {third_party_claim.auto_insurance.name} {client.full_name}", third_party_claim.defendant.casefile.main_folder_id)
            # Build Json Body for Batch Update
            flag_pairs = [
                ("$$fullDate", todays_date),
                ("client.fullName", client.full_name),
                ("third_party_claim.auto_insurance.name", third_party_claim.defendant.auto_claim.auto_insurance.name),
                ("third_party_claim.claim_number", third_party_claim.defendant.auto_claim.claim_number),
                ("date_of_loss", date_of_loss),
                ("medical_provider.list", client.medical_provider_list)
            ]
            json_body = build_json_body(*flag_pairs)
            # Batch Update File
            result = batch_update_file(current_user.access_token, file_id, json_body)
            if result == 200:
                flash("PSS batch update was successful", "is-success")
            else:
                flash(f"PSS batch update returned an error code, {result}", "is-danger")
        flash("Done generating PSS", "is-info")
    return redirect(url_for("casefile.details",tenant_name=tenant_name, casefile_id = third_party_claim.defendant.casefile_id))

# Generate Acceptance Letter
@drive_integration.route('/<tenant_name>/generate-acceptance-letter/defendant/<int:defendant_id>/autoinsurance/<int:auto_insurance_id>')
@login_required
def generate_acceptance_letter(tenant_name,defendant_id, auto_insurance_id):
    validate_tenant(tenant_name)
    # third_party_claim = db.get_or_404(ThirdPartyClaim, (defendant_id, auto_insurance_id))
    third_party_claim = ThirdPartyClaim.query.filter_by(defendant_id=defendant_id,auto_insurance_id=auto_insurance_id,  tenant_id=session['tenant_id']).first_or_404()
    acceptance_letter = os.environ.get("ACCEPTANCE_LETTER_TEMPLATE")
    todays_date = date.today()
    todays_date = todays_date.strftime("%B %d, %Y")
    date_of_loss = third_party_claim.defendant.casefile.date_of_loss
    date_of_loss = date_of_loss.strftime("%B %d, %Y")

    if check_access_token(current_user.token_expiration):
        # Copy Template
        file_id = copy_template(current_user.access_token, acceptance_letter, f"Offer Acceptance Letter - {third_party_claim.auto_insurance.name}", third_party_claim.defendant.casefile.main_folder_id)
        # Build Json Body for Batch Update
        flag_pairs = [
            ("auto_insurance.name", third_party_claim.auto_insurance.name),
            ("adjuster_full_name", third_party_claim.auto_adjuster.full_name),
            ("adjuster_street_address", third_party_claim.auto_adjuster.street_address),
            ("adjuster_city", third_party_claim.auto_adjuster.city),
            ("adjuster_state", third_party_claim.auto_adjuster.state),
            ("adjuster_zip_code", third_party_claim.auto_adjuster.zip_code),
            ("adjuster_fax", third_party_claim.auto_adjuster.fax),
            ("claim_number", third_party_claim.claim_number),
            ("defendant.full_name", third_party_claim.defendant.full_name),
            ("date_of_loss", date_of_loss),
            ("client.list", third_party_claim.defendant.casefile.client_list),
            ("$$fullDate", todays_date)
        ]
        json_body = build_json_body(*flag_pairs)
        # Batch Update File
        result = batch_update_file(current_user.access_token, file_id, json_body)
        if result == 200:
            flash("Offer Acceptance letter batch update was successful", "is-success")
        else:
            flash(f"Offer Acceptance letter batch update returned an error code, {result}", "is-danger")
    flash("Done generating Offer Acceptance Letter", "is-info")
    return redirect(url_for("casefile.details",tenant_name=tenant_name, casefile_id = third_party_claim.defendant.casefile_id))

# Generate AdHoc Reduction Request
@drive_integration.route('/<tenant_name>/generate-adhoc-reduction-request/client/<int:client_id>/medprovider/<int:medical_provider_id>')
@login_required
def generate_adhoc_reduction_request(tenant_name , client_id, medical_provider_id):
    validate_tenant(tenant_name)
    # medical_bill = db.get_or_404(MedicalBill, (client_id, medical_provider_id))
    medical_bill = MedicalBill.query.filter_by(client_id=client_id,medical_provider_id=medical_provider_id,  tenant_id=session['tenant_id']).first_or_404()
    reduction_request = os.environ.get("REDUCTION_REQUEST_TEMPLATE")
    todays_date = date.today()
    todays_date = todays_date.strftime("%B %d, %Y")
    date_of_loss = medical_bill.client.casefile.date_of_loss
    date_of_loss = date_of_loss.strftime("%B %d, %Y")

    if check_access_token(current_user.token_expiration):
        # Copy Template
        file_id = copy_template(current_user.access_token, reduction_request, f"Reduction Request - {medical_bill.medical_provider.name} for {medical_bill.client.full_name}", medical_bill.client.casefile.client_documentation_folder_id)
        # Build Json Body for Batch Update
        flag_pairs = [
            ("medical_provider.name", medical_bill.medical_provider.name),
            ("medical_provider.street_address", medical_bill.medical_provider.street_address),
            ("medical_provider.city", medical_bill.medical_provider.city),
            ("medical_provider.state", medical_bill.medical_provider.state),
            ("medical_provider.zip_code", medical_bill.medical_provider.zip_code),
            ("client.full_name", medical_bill.client.full_name),
            ("client.dob", medical_bill.client.dob.strftime('%m/%d/%Y')),
            ("date_of_loss", date_of_loss),
            ("$$fullDate", todays_date),
            ("wreck_city", medical_bill.client.casefile.wreck_city),
            ("wreck_state", medical_bill.client.casefile.wreck_state),
            ("total_due", str(medical_bill.total_due))
          ]
        json_body = build_json_body(*flag_pairs)
        # Batch Update File
        result = batch_update_file(current_user.access_token, file_id, json_body)
        if result == 200:
          flash("Reduction request batch update was successful", "is-success")
        else:
            flash(f"Reduction request batch update returned an error code, {result}", "is-danger")
    flash("Done generating Reduction request", "is-info")
    return redirect(url_for("casefile.details",tenant_name=tenant_name, casefile_id = medical_bill.client.casefile_id))

# Generate Payment Instructions
@drive_integration.route('/<tenant_name>/generate-payment-instructions/defendant/<int:defendant_id>/autoinsurance/<int:auto_insurance_id>')
@login_required
def generate_payment_instructions(tenant_name , defendant_id, auto_insurance_id):
    validate_tenant(tenant_name)
    # third_party_claim = db.get_or_404(ThirdPartyClaim, (defendant_id, auto_insurance_id))
    third_party_claim = ThirdPartyClaim.query.filter_by(defendant_id=defendant_id,auto_insurance_id=auto_insurance_id,  tenant_id=session['tenant_id']).first_or_404()
    payment_instructions = os.environ.get("PAYMENT_INSTRUCTIONS_TEMPLATE")
    todays_date = date.today()
    todays_date = todays_date.strftime("%B %d, %Y")
    date_of_loss = third_party_claim.defendant.casefile.date_of_loss
    date_of_loss = date_of_loss.strftime("%B %d, %Y")

    if check_access_token(current_user.token_expiration):
        # Copy Template
        file_id = copy_template(current_user.access_token, payment_instructions, f"Payment Instructions - {third_party_claim.auto_insurance.name}", third_party_claim.defendant.casefile.main_folder_id)
        # Build Json Body for Batch Update
        flag_pairs = [
            ("auto_insurance.name", third_party_claim.auto_insurance.name),
            ("adjuster_full_name", third_party_claim.auto_adjuster.full_name),
            ("adjuster_street_address", third_party_claim.auto_adjuster.street_address),
            ("adjuster_city", third_party_claim.auto_adjuster.city),
            ("adjuster_state", third_party_claim.auto_adjuster.state),
            ("adjuster_zip_code", third_party_claim.auto_adjuster.zip_code),
            ("adjuster_fax", third_party_claim.auto_adjuster.fax),
            ("claim_number", third_party_claim.claim_number),
            ("defendant.full_name", third_party_claim.defendant.full_name),
            ("date_of_loss", date_of_loss),
            ("client.list", third_party_claim.defendant.casefile.client_list),
            ("$$fullDate", todays_date)
        ]
        json_body = build_json_body(*flag_pairs)
        # Batch Update File
        result = batch_update_file(current_user.access_token, file_id, json_body)
        if result == 200:
            flash("Payment Instructions batch update was successful", "is-success")
        else:
            flash(f"Payment Instructions batch update returned an error code, {result}", "is-danger")
    flash("Done generating Payment Instructions", "is-info")
    return redirect(url_for("casefile.details",tenant_name=tenant_name, casefile_id = third_party_claim.defendant.casefile_id))


@drive_integration.route('/<tenant_name>/generate-adhoc-um-demand/casefile/<int:casefile_id>/autoinsurance/<int:auto_insurance_id>')
@login_required
def generate_adhoc_um_demand(tenant_name,casefile_id, auto_insurance_id):
    validate_tenant(tenant_name)
    # first_party_claim = db.get_or_404(FirstPartyClaim, (casefile_id, auto_insurance_id))
    first_party_claim = FirstPartyClaim.query.filter_by(casefile_id=casefile_id,auto_insurance_id=auto_insurance_id,  tenant_id=session['tenant_id']).first_or_404()
    demand = os.environ.get("UM_DEMAND_TEMPLATE")
    todays_date = date.today()
    todays_date = todays_date.strftime("%B %d, %Y")
    date_of_loss = first_party_claim.casefile.date_of_loss
    date_of_loss = date_of_loss.strftime("%B %d, %Y")

    if check_access_token(current_user.token_expiration):
        # Create Each Claim
        #if first_party_claim.has_ == "True":
            # Copy Template
        file_id = copy_template(current_user.access_token, demand, f"UM Demand - {first_party_claim.auto_insurance.name}", first_party_claim.casefile.main_folder_id)
            # Build Json Body for Batch Update
        flag_pairs = [
                ("AutoInsurer::name", first_party_claim.auto_insurance.name),
                ("Defendants_Adjuster::fullName", first_party_claim.auto_adjuster.full_name),
                ("adjuster_street_address", first_party_claim.auto_adjuster.street_address),
                ("adjuster_city", first_party_claim.auto_adjuster.city),
                ("adjuster_state", first_party_claim.auto_adjuster.state),
                ("adjuster_zip_code", first_party_claim.auto_adjuster.zip_code),
                ("Adjuster::fax", first_party_claim.auto_adjuster.fax),
                ("Client::fullName", first_party_claim.casefile.client_list),
                ("Clients_Claim::claimNumber", first_party_claim.claim_number),
                ("$$fullDate", todays_date)
            ]
        json_body = build_json_body(*flag_pairs)
            # Batch Update File
        result = batch_update_file(current_user.access_token, file_id, json_body)
        if result == 200:
                flash("UM Demand batch update was successful", "is-success")
        else:
                flash(f"UM Demand batch update returned an error code, {result}", "is-danger")
        flash("Done generating UM Demand", "is-info")
    else:
            flash("This policy does not have UM recorded on file. Please check your records and update the claim information if necessary.", "is-warning")
    return redirect(url_for("casefile.details",tenant_name=tenant_name, casefile_id = casefile_id))