from flask import Blueprint, render_template, request, redirect, url_for, flash,session,abort
from flask_login import login_required
from piassist.models import HealthAdjuster, HealthClaim, HealthInsurance,Tenant
from . import db

healthadjuster = Blueprint('healthadjuster', __name__)
def validate_tenant(tenant_name):
    tenant = Tenant.query.filter_by(name=tenant_name).first()
    if tenant:
        session['tenant_id'] = tenant.id
        session['tenant_name'] = tenant.name
    else:
        flash("Invalid tenant specified in URL.", "is-warning")
        abort(404, description=f"Invalid tenant: '{tenant_name}'")

# Health Adjuster Index Route
@healthadjuster.route('/<tenant_name>/healthadjuster')
@login_required
def index(tenant_name):
    validate_tenant(tenant_name)
    # health_adjusters = HealthAdjuster.query.order_by(HealthAdjuster.last_name).all()
    health_adjusters = HealthAdjuster.query.filter_by(tenant_id=session['tenant_id']).order_by(HealthAdjuster.last_name).all()
    return render_template('healthadjuster/healthadjuster-index.html',tenant_name=tenant_name, health_adjusters=health_adjusters)

# Health Adjuster Detail Route
@healthadjuster.route('/<tenant_name>/healthadjuster/<int:health_adjuster_id>', methods=['GET', 'POST'])
@login_required
def details(tenant_name , health_adjuster_id):
    validate_tenant(tenant_name)
    # health_adjuster = db.get_or_404(HealthAdjuster, health_adjuster_id)
    # health_insurance_providers = HealthInsurance.query.order_by(HealthInsurance.name).all()
    # claims = HealthClaim.query.filter(HealthClaim.health_adjuster_id == health_adjuster_id).all()
    health_adjuster = HealthAdjuster.query.filter_by(id=health_adjuster_id, tenant_id=session['tenant_id']).first_or_404()
    claims = HealthClaim.query.filter_by(health_adjuster_id=health_adjuster_id, tenant_id=session['tenant_id']).all()
    health_insurance_providers = HealthInsurance.query.filter_by(tenant_id=session['tenant_id']).order_by(HealthInsurance.name).all()
    if request.method == 'POST':
        health_adjuster.first_name = request.form.get("first_name")
        health_adjuster.middle_name = request.form.get("middle_name")
        health_adjuster.last_name = request.form.get("last_name")
        health_adjuster.phone = request.form.get("phone")
        health_adjuster.fax = request.form.get("fax")
        health_adjuster.email = request.form.get("email")
        health_adjuster.notes = request.form.get("notes")
        try:
            health_adjuster.health_insurance_id = int(request.form.get("health_insurance_id"))
        except:
            flash(f"Couldn't update the Health Insurance Provider associated with the Health Insurance Adjuster, {health_adjuster.full_name}.", "is-warning")

        db.session.commit()
        flash(f"The Health Adjuster, {health_adjuster.full_name}, has been updated successfully", "is-success")
        return redirect(url_for('healthadjuster.index' , tenant_name=tenant_name))
    return render_template('healthadjuster/healthadjuster-detail.html', health_adjuster=health_adjuster, health_insurance_providers=health_insurance_providers,tenant_name=tenant_name, claims=claims)

# Health Adjuster Input Route
@healthadjuster.route('/<tenant_name>/new/healthadjuster', methods=['GET', 'POST'])
@login_required
def input(tenant_name):
    # health_insurance_providers = HealthInsurance.query.order_by(HealthInsurance.name).all()
    health_insurance_providers = HealthInsurance.query.filter_by(tenant_id=session['tenant_id']).order_by(HealthInsurance.name).all()
    if request.method == 'POST':
        first_name = request.form.get("first_name")
        middle_name = request.form.get("middle_name")
        last_name = request.form.get("last_name")
        phone = request.form.get("phone")
        fax = request.form.get("fax")
        email = request.form.get("email")
        health_insurance_id = request.form.get("health_insurance_id")

        try:
            health_insurance_id = int(health_insurance_id)
        except:
            flash("The New Health Insurance Adjuster isn't associated with a Health Insurance Provider", "is-warning")
            health_insurance_id = None

        new_health_adjuster = HealthAdjuster(
            first_name=first_name,
            middle_name=middle_name,
            last_name=last_name,
            phone=phone,
            fax=fax,
            email=email,
            health_insurance_id=health_insurance_id,
            tenant_id=session['tenant_id'],

        )
        db.session.add(new_health_adjuster)
        db.session.commit()
        flash(f"The Health Adjuster, {new_health_adjuster.full_name}, has been created successfully", "is-success")
        return redirect(url_for('healthadjuster.index' , tenant_name=tenant_name))
    return render_template('healthadjuster/healthadjuster-input.html',tenant_name=tenant_name,  health_insurance_providers=health_insurance_providers)