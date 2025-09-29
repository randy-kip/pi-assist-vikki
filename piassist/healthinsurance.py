from flask import Blueprint, render_template, request, redirect, url_for, flash,session,abort
from flask_login import login_required
from piassist.models import HealthInsurance,Tenant
from . import db

healthinsurance = Blueprint('healthinsurance', __name__)
def validate_tenant(tenant_name):
    tenant = Tenant.query.filter_by(name=tenant_name).first()
    if tenant:
        session['tenant_id'] = tenant.id
        session['tenant_name'] = tenant.name
    else:
        flash("Invalid tenant specified in URL.", "is-warning")
        abort(404, description=f"Invalid tenant: '{tenant_name}'")

# Health Insurance Index Route
@healthinsurance.route('/<tenant_name>/healthinsurance')
@login_required
def index(tenant_name):
    validate_tenant(tenant_name)
    # health_insurances = HealthInsurance.query.order_by(HealthInsurance.name).all()
    health_insurances = HealthInsurance.query.filter_by( tenant_id=session['tenant_id']).order_by(HealthInsurance.name).all()
    return render_template('healthinsurance/healthinsurance-index.html', tenant_name=tenant_name, health_insurances=health_insurances)

# Health Insurance View Only Route
@healthinsurance.route('/<tenant_name>/healthinsurance/view/<int:health_insurance_id>')
@login_required
def view_details(tenant_name , health_insurance_id):
    validate_tenant(tenant_name)
    health_insurance = HealthInsurance.query.filter_by(id=health_insurance_id, tenant_id=session['tenant_id']).first_or_404()
    # health_insurance = db.get_or_404(HealthInsurance, health_insurance_id)
    return render_template('healthinsurance/healthinsurance-detail-viewonly.html', tenant_name=tenant_name, health_insurance=health_insurance)

# Health Insurance Detail Route
@healthinsurance.route('/<tenant_name>/healthinsurance/<int:health_insurance_id>', methods=['GET', 'POST'])
@login_required
def details(tenant_name , health_insurance_id):
    validate_tenant(tenant_name)
    health_insurance = HealthInsurance.query.filter_by(id=health_insurance_id, tenant_id=session['tenant_id']).first_or_404()
    #health_insurance = db.get_or_404(HealthInsurance, health_insurance_id)
    if request.method == 'POST':
        health_insurance.name = request.form.get("name")
        health_insurance.street_address = request.form.get("street_address")
        health_insurance.street_address_2 = request.form.get("street_address_2")
        health_insurance.city = request.form.get("city")
        health_insurance.state = request.form.get("state")
        health_insurance.zip_code = request.form.get("zip_code")
        health_insurance.phone_1_type = request.form.get("phone_1_type")
        health_insurance.phone_1 = request.form.get("phone_1")
        health_insurance.phone_2_type = request.form.get("phone_2_type")
        health_insurance.phone_2 = request.form.get("phone_2")
        health_insurance.phone_3_type = request.form.get("phone_3_type")
        health_insurance.phone_3 = request.form.get("phone_3")
        health_insurance.fax_1_type = request.form.get("fax_1_type")
        health_insurance.fax_1 = request.form.get("fax_1")
        health_insurance.fax_2_type = request.form.get("fax_2_type")
        health_insurance.fax_2 = request.form.get("fax_2")
        health_insurance.fax_3_type = request.form.get("fax_3_type")
        health_insurance.fax_3 = request.form.get("fax_3")
        health_insurance.email_1_type = request.form.get("email_1_type")
        health_insurance.email_1 = request.form.get("email_1")
        health_insurance.email_2_type = request.form.get("email_2_type")
        health_insurance.email_2 = request.form.get("email_2")
        health_insurance.notes = request.form.get("notes")

        db.session.commit()
        flash(f"The Health Insurance Provider, {health_insurance.name}, has been updated successfully", "is-success")
        return redirect(url_for('healthinsurance.index', tenant_name=tenant_name))
    return render_template('healthinsurance/healthinsurance-detail.html',tenant_name=tenant_name,health_insurance_id=health_insurance_id, health_insurance=health_insurance)

# Health Insurance Input Route
@healthinsurance.route('/<tenant_name>/new/healthinsurance', methods=['GET', 'POST'])
@login_required
def input(tenant_name):
    validate_tenant(tenant_name)
    if request.method == 'POST':
        name = request.form.get("name")
        street_address = request.form.get("street_address")
        street_address_2 = request.form.get("street_address_2")
        city = request.form.get("city")
        state = request.form.get("state")
        zip_code = request.form.get("zip_code")
        phone_1_type = request.form.get("phone_1_type")
        phone_1 = request.form.get("phone_1")
        phone_2_type = request.form.get("phone_2_type")
        phone_2 = request.form.get("phone_2")
        phone_3_type = request.form.get("phone_3_type")
        phone_3 = request.form.get("phone_3")
        fax_1_type = request.form.get("fax_1_type")
        fax_1 = request.form.get("fax_1")
        fax_2_type = request.form.get("fax_2_type")
        fax_2 = request.form.get("fax_2")
        fax_3_type = request.form.get("fax_3_type")
        fax_3 = request.form.get("fax_3")
        email_1_type = request.form.get("email_1_type")
        email_1 = request.form.get("email_1")
        email_2_type = request.form.get("email_2_type")
        email_2 = request.form.get("email_2")
        notes = request.form.get("notes")

        new_health_insurance = HealthInsurance(
            name=name,
            street_address=street_address,
            street_address_2=street_address_2,
            city=city,
            state=state,
            zip_code=zip_code,
            phone_1=phone_1,
            phone_1_type=phone_1_type,
            phone_2=phone_2,
            phone_2_type=phone_2_type,
            phone_3=phone_3,
            phone_3_type=phone_3_type,
            fax_1=fax_1,
            fax_1_type=fax_1_type,
            fax_2=fax_2,
            fax_2_type=fax_2_type,
            fax_3=fax_3,
            fax_3_type=fax_3_type,
            email_1=email_1,
            email_1_type=email_1_type,
            email_2=email_2,
            email_2_type=email_2_type,
            notes=notes,
            tenant_id=session['tenant_id']
        )
        db.session.add(new_health_insurance)
        db.session.commit()
        flash(f"Created New Health Insurance Provider, {new_health_insurance.name}, successfully!", "is-success")
        return redirect(url_for('healthinsurance.index' , tenant_name=tenant_name))
    return render_template('healthinsurance/healthinsurance-input.html' , tenant_name=tenant_name)