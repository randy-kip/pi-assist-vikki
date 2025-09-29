from datetime import datetime
from flask import Blueprint, render_template, request, redirect, url_for, flash , session,abort
from flask_login import login_required
from piassist.models import HealthClaim, HealthInsurance, Client, HealthAdjuster,Tenant
from . import db

healthclaim = Blueprint('healthclaim', __name__)
def validate_tenant(tenant_name):
    tenant = Tenant.query.filter_by(name=tenant_name).first()
    if tenant:
        session['tenant_id'] = tenant.id
        session['tenant_name'] = tenant.name
    else:
        flash("Invalid tenant specified in URL.", "is-warning")
        abort(404, description=f"Invalid tenant: '{tenant_name}'")
# Health Claim Detail Route
@healthclaim.route('/<tenant_name>/healthclaim/client/<int:client_id>/healthinsurance/<int:health_insurance_id>', methods=['GET', 'POST'])
@login_required
def details(tenant_name , client_id, health_insurance_id):
    validate_tenant(tenant_name)
    # health_claim = db.get_or_404(HealthClaim, (client_id, health_insurance_id))
    # health_adjusters = HealthAdjuster.query.filter(HealthAdjuster.health_insurance_id == health_insurance_id).all()
    health_claim = HealthClaim.query.filter_by(health_insurance_id=health_insurance_id,client_id=client_id, tenant_id=session['tenant_id']).first_or_404()
    health_adjusters = HealthAdjuster.query.filter_by(health_insurance_id=health_insurance_id, tenant_id=session['tenant_id']).all()
    if request.method == 'POST':
        health_claim.member_id = request.form.get("member_id")
        health_claim.event_number = request.form.get("event_number")
        health_claim.is_hipaa_sent = request.form.get("is_hipaa_sent")
        health_claim.is_lor_sent = request.form.get("is_lor_sent")
        health_claim.is_log_received = request.form.get("is_log_received")

        try:
            health_claim.total_due = float(request.form.get("total_due"))
        except:
            flash("Didn't save a total for Health Claim, make sure you enter a whole number.", "is-warning")
        
        try:
            health_claim.health_adjuster_id = int(request.form.get("health_adjuster_id"))
        except:
            flash("Didn't update the Health Insurance Adjuster related to the updated Health Claim", "is-warning")
        
        try:
            health_claim.last_request_date = datetime.strptime(request.form.get("last_request_date"), '%Y-%m-%d').date()
        except:
            flash("Last request date couldn't be saved.", "is-warning")

        db.session.commit()
        flash("Update Health Claim Successfully", "is-success")
        return redirect(url_for('casefile.details', casefile_id = health_claim.client.casefile_id , tenant_name=tenant_name))

    return render_template('healthclaim/health-claim-detail.html',health_insurance_id=health_insurance_id,   client_id=client_id, health_claim=health_claim,tenant_name=tenant_name, health_adjusters=health_adjusters)

# Health Claim Input Route
@healthclaim.route('/<tenant_name>/new/healthclaim/casefile/<int:casefile_id>', methods=['GET', 'POST'])
@login_required
def input(tenant_name , casefile_id):
    validate_tenant(tenant_name)
    # health_insurance_providers = HealthInsurance.query.order_by(HealthInsurance.name).all()
    # clients = Client.query.filter(Client.casefile_id == casefile_id).all()
    clients = Client.query.filter_by(casefile_id=casefile_id, tenant_id=session['tenant_id']).all()
    health_insurance_providers = HealthInsurance.query.filter_by(tenant_id=session['tenant_id']).order_by(HealthInsurance.name).all()
    if request.method == 'POST':
        # ADD HEALTH ADJUSTER ID
        client_id = request.form.get("client_id")
        health_insurance_id = request.form.get("health_insurance_id")
        member_id = request.form.get("member_id")
        event_number = request.form.get("event_number")
        is_hipaa_sent = request.form.get("is_hipaa_sent")
        is_lor_sent = request.form.get("is_lor_sent")
        is_log_received = request.form.get("is_log_received")
        total_due = request.form.get("total_due")
        last_request_date = request.form.get("last_request_date")
        
        try:
            client_id = int(client_id)
            health_insurance_id = int(health_insurance_id)
        except:
            # NEED TO ADD AN ABORT HERE
            flash("Error: New Health Claims must be associated with a client and health insurance provider.", "is-danger")
            return redirect(url_for('casefile.details', casefile_id=casefile_id))

        try:
            total_due = float(total_due)
        except:
            flash("Total due not saved because value provided wasn't an integer", "is-warning")
            total_due = None
        
        try:
            last_request_date = datetime.strptime(request.form.get("last_request_date"), '%Y-%m-%d').date()
        except:
            flash("Last request date couldn't be saved.", "is-warning")
            last_request_date = None

        new_health_claim = HealthClaim(
            client_id = client_id,
            health_insurance_id = health_insurance_id,
            member_id = member_id,
            event_number = event_number,
            is_hipaa_sent = is_hipaa_sent,
            is_lor_sent = is_lor_sent, 
            is_log_received = is_log_received,
            total_due = total_due,
            last_request_date = last_request_date,
            tenant_id = session['tenant_id']
        )

        try:
            db.session.add(new_health_claim)
            db.session.commit()
        except:
            flash("Didn't create new health claim. Claim already exists for that client and medical provider.", "is-danger")

        return redirect(url_for('casefile.details',tenant_name=tenant_name, casefile_id=casefile_id))
    return render_template('healthclaim/health-claim-input.html', health_insurance_providers=health_insurance_providers,tenant_name=tenant_name,casefile_id=casefile_id, clients=clients)

# DELETE HEALTH CLAIM ROUTE
@healthclaim.route('/<tenant_name>/delete/healthclaim/client/<int:client_id>/healthinsurance/<int:health_insurance_id>')
@login_required
def delete(tenant_name,client_id, health_insurance_id):
    validate_tenant(tenant_name)
    # healthclaim = db.get_or_404(HealthClaim, (client_id, health_insurance_id))
    healthclaim = HealthClaim.query.filter_by(client_id=client_id, health_insurance_id=health_insurance_id, tenant_id=session['tenant_id']).first_or_404()
    casefile_id = healthclaim.client.casefile_id
    try:
        db.session.delete(healthclaim)
        db.session.commit()
        flash(f"Health Claim deleted successfuly", "is-success")
    except:
        flash('Something went wrong', 'is-danger')
    return redirect(url_for('casefile.details', tenant_name=tenant_name, casefile_id = casefile_id))