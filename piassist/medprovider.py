from flask import Blueprint, render_template, request, redirect, url_for, flash,session,abort
from flask_login import login_required
from piassist.models import MedicalProvider,Tenant
from . import db

medprovider = Blueprint('medprovider', __name__)

def validate_tenant(tenant_name):
    tenant = Tenant.query.filter_by(name=tenant_name).first()
    if tenant:
        session['tenant_id'] = tenant.id
        session['tenant_name'] = tenant.name
    else:
        flash("Invalid tenant specified in URL.", "is-warning")
        abort(404, description=f"Invalid tenant: '{tenant_name}'")
# Medical Provider Index Route
@medprovider.route('/<tenant_name>/medprovider')
@login_required
def index(tenant_name):
    validate_tenant(tenant_name)
    # medical_providers = MedicalProvider.query.order_by(MedicalProvider.name).all()
    medical_providers = MedicalProvider.query.filter_by(tenant_id=session['tenant_id']).order_by(MedicalProvider.name).all()
    return render_template('medicalprovider/medical-provider-index.html',tenant_name=tenant_name, medical_providers=medical_providers)

# Medical Provider View Only Route
@medprovider.route('/<tenant_name>/medprovider/view/<int:medical_provider_id>')
@login_required
def view_details(tenant_name , medical_provider_id):
    validate_tenant(tenant_name)
    # medical_provider = db.get_or_404(MedicalProvider, medical_provider_id)
    medical_provider = MedicalProvider.query.filter_by(id=medical_provider_id, tenant_id=session['tenant_id']).first_or_404()
    return render_template('medicalprovider/medical-provider-detail-viewonly.html',tenant_name=tenant_name,medical_provider_id=medical_provider_id, medical_provider=medical_provider)

# Medical Provider Detail Route
@medprovider.route('/<tenant_name>/medprovider/<int:medical_provider_id>', methods=['GET', 'POST'])
@login_required
def details(tenant_name , medical_provider_id):
    validate_tenant(tenant_name)
    # medical_provider = db.get_or_404(MedicalProvider, medical_provider_id)
    medical_provider = MedicalProvider.query.filter_by(id=medical_provider_id, tenant_id=session['tenant_id']).first_or_404()
    if request.method == 'POST':
        medical_provider.name = request.form.get("name")
        medical_provider.street_address = request.form.get("street_address")
        medical_provider.street_address_2 = request.form.get("street_address_2")
        medical_provider.city = request.form.get("city")
        medical_provider.state = request.form.get("state")
        medical_provider.zip_code = request.form.get("zip_code")
        medical_provider.hipaa_method = request.form.get("hipaa_method")
        medical_provider.phone_1_type = request.form.get("phone_1_type")
        medical_provider.phone_1 = request.form.get("phone_1")
        medical_provider.phone_2_type = request.form.get("phone_2_type")
        medical_provider.phone_2 = request.form.get("phone_2")
        medical_provider.phone_3_type = request.form.get("phone_3_type")
        medical_provider.phone_3 = request.form.get("phone_3")
        medical_provider.fax_1_type = request.form.get("fax_1_type")
        medical_provider.fax_1 = request.form.get("fax_1")
        medical_provider.fax_2_type = request.form.get("fax_2_type")
        medical_provider.fax_2 = request.form.get("fax_2")
        medical_provider.fax_3_type = request.form.get("fax_3_type")
        medical_provider.fax_3 = request.form.get("fax_3")
        medical_provider.email_1_type = request.form.get("email_1_type")
        medical_provider.email_1 = request.form.get("email_1")
        medical_provider.email_2_type = request.form.get("email_2_type")
        medical_provider.email_2 = request.form.get("email_2")
        medical_provider.notes = request.form.get("notes")

        db.session.commit()
        flash(f"Medical Provider, {medical_provider.name}, Updated Successfully.", "is-success")
        return redirect(url_for('medprovider.index',  tenant_name=tenant_name))
    return render_template('medicalprovider/medical-provider-detail.html',tenant_name=tenant_name, medical_provider=medical_provider , medical_provider_id=medical_provider_id)

# Medical Provider Input Route
@medprovider.route('/<tenant_name>/new/medprovider', methods=['GET', 'POST'])
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
        hipaa_method = request.form.get("hipaa_method")
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

        new_medical_provider = MedicalProvider(
            name=name,
            street_address=street_address,
            street_address_2=street_address_2,
            city=city,
            state=state,
            zip_code=zip_code,
            hipaa_method=hipaa_method,
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
        db.session.add(new_medical_provider)
        db.session.commit()
        flash(f"Created New Medical Provider, {new_medical_provider.name}, Successfully", "is-success")
        return redirect(url_for('medprovider.index' , tenant_name=tenant_name))
    return render_template('medicalprovider/medical-provider-input.html',tenant_name=tenant_name)