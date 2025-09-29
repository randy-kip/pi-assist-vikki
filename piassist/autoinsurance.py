# from flask import Blueprint, render_template, request, redirect, url_for, flash , session, abort
# from flask_login import login_required
# from piassist.models import AutoInsurance,Tenant
# from . import db

# autoinsurance = Blueprint('autoinsurance', __name__)

# def validate_tenant(tenant_name):
#     tenant = Tenant.query.filter_by(name=tenant_name).first()
#     if tenant:
#         session['tenant_id'] = tenant.id
#         session['tenant_name'] = tenant.name
#     else:
#         flash("Invalid tenant specified in URL.", "is-warning")
#         abort(404, description=f"Invalid tenant: '{tenant_name}'")
# # Auto Insurance Index Route
# @autoinsurance.route('/autoinsurance')
# @login_required
# def index():
#     auto_insurances = AutoInsurance.query.order_by(AutoInsurance.name).all()
#     return render_template("autoinsurance/autoinsurance-index.html", auto_insurances=auto_insurances)

# # Auto Insurance View Only Route
# @autoinsurance.route('/autoinsurance/view/<int:auto_insurance_id>')
# @login_required
# def view_details(auto_insurance_id):
#     auto_insurance = db.get_or_404(AutoInsurance, auto_insurance_id)
#     return render_template('autoinsurance/autoinsurance-detail-viewonly.html', auto_insurance=auto_insurance)

# # Auto Insurance Detail Route
# @autoinsurance.route('/autoinsurance/<int:auto_insurance_id>', methods=['GET', 'POST'])
# @login_required
# def details(auto_insurance_id):
#     auto_insurance = db.get_or_404(AutoInsurance, auto_insurance_id)
#     if request.method == 'POST':
#         auto_insurance.name = request.form.get("name")
#         auto_insurance.street_address = request.form.get("street_address")
#         auto_insurance.street_address_2 = request.form.get("street_address_2")
#         auto_insurance.city = request.form.get("city")
#         auto_insurance.state = request.form.get("state")
#         auto_insurance.zip_code = request.form.get("zip_code")
#         auto_insurance.phone_1_type = request.form.get("phone_1_type")
#         auto_insurance.phone_1 = request.form.get("phone_1")
#         auto_insurance.phone_2_type = request.form.get("phone_2_type")
#         auto_insurance.phone_2 = request.form.get("phone_2")
#         auto_insurance.phone_3_type = request.form.get("phone_3_type")
#         auto_insurance.phone_3 = request.form.get("phone_3")
#         auto_insurance.fax_1_type = request.form.get("fax_1_type")
#         auto_insurance.fax_1 = request.form.get("fax_1")
#         auto_insurance.fax_2_type = request.form.get("fax_2_type")
#         auto_insurance.fax_2 = request.form.get("fax_2")
#         auto_insurance.fax_3_type = request.form.get("fax_3_type")
#         auto_insurance.fax_3 = request.form.get("fax_3")
#         auto_insurance.email_1_type = request.form.get("email_1_type")
#         auto_insurance.email_1 = request.form.get("email_1")
#         auto_insurance.email_2_type = request.form.get("email_2_type")
#         auto_insurance.email_2 = request.form.get("email_2")
#         auto_insurance.notes = request.form.get("notes")

#         db.session.commit()
#         flash(f"The Auto Insurance Provider, {auto_insurance.name}, has been updated successfully", "is-success")
#         return redirect(url_for('autoinsurance.index'))
#     return render_template('autoinsurance/autoinsurance-detail.html', auto_insurance=auto_insurance)

# # Auto Insurance Input Route
# @autoinsurance.route('/new/autoinsurance', methods=['GET', 'POST'])
# @login_required
# def input():
#     if request.method == 'POST':
#         name = request.form.get("name")
#         street_address = request.form.get("street_address")
#         street_address_2 = request.form.get("street_address_2")
#         city = request.form.get("city")
#         state = request.form.get("state")
#         zip_code = request.form.get("zip_code")
#         phone_1_type = request.form.get("phone_1_type")
#         phone_1 = request.form.get("phone_1")
#         phone_2_type = request.form.get("phone_2_type")
#         phone_2 = request.form.get("phone_2")
#         phone_3_type = request.form.get("phone_3_type")
#         phone_3 = request.form.get("phone_3")
#         fax_1_type = request.form.get("fax_1_type")
#         fax_1 = request.form.get("fax_1")
#         fax_2_type = request.form.get("fax_2_type")
#         fax_2 = request.form.get("fax_2")
#         fax_3_type = request.form.get("fax_3_type")
#         fax_3 = request.form.get("fax_3")
#         email_1_type = request.form.get("email_1_type")
#         email_1 = request.form.get("email_1")
#         email_2_type = request.form.get("email_2_type")
#         email_2 = request.form.get("email_2")
#         notes = request.form.get("notes")

#         new_auto_insurance = AutoInsurance(
#             name=name,
#             street_address=street_address,
#             street_address_2=street_address_2,
#             city=city,
#             state=state,
#             zip_code=zip_code,
#             phone_1=phone_1,
#             phone_1_type=phone_1_type,
#             phone_2=phone_2,
#             phone_2_type=phone_2_type,
#             phone_3=phone_3,
#             phone_3_type=phone_3_type,
#             fax_1=fax_1,
#             fax_1_type=fax_1_type,
#             fax_2=fax_2,
#             fax_2_type=fax_2_type,
#             fax_3=fax_3,
#             fax_3_type=fax_3_type,
#             email_1=email_1,
#             email_1_type=email_1_type,
#             email_2=email_2,
#             email_2_type=email_2_type,
#             notes=notes
#         )
#         db.session.add(new_auto_insurance)
#         db.session.commit()
#         flash(f"Created Auto Insurance Provider, {new_auto_insurance.name}, successfully!", "is-success")
#         return redirect(url_for('autoinsurance.index'))
#     return render_template('autoinsurance/autoinsurance-input.html')

from flask import Blueprint, render_template, request, redirect, url_for, flash, session, abort
from flask_login import login_required
from piassist.models import AutoInsurance, Tenant
from . import db

autoinsurance = Blueprint('autoinsurance', __name__)

def validate_tenant(tenant_name):
    tenant = Tenant.query.filter_by(name=tenant_name).first()
    if tenant:
        session['tenant_id'] = tenant.id
        session['tenant_name'] = tenant.name
    else:
        flash("Invalid tenant specified in URL.", "is-warning")
        abort(404, description=f"Invalid tenant: '{tenant_name}'")

# Auto Insurance Index Route
@autoinsurance.route('/<tenant_name>/autoinsurance')
@login_required
def index(tenant_name):
    auto_insurances = AutoInsurance.query.filter_by(tenant_id=session['tenant_id']).order_by(AutoInsurance.name).all()
    return render_template("autoinsurance/autoinsurance-index.html", auto_insurances=auto_insurances, tenant_name=tenant_name)

# # Auto Insurance View Only Route
@autoinsurance.route('/<tenant_name>/auto_insurance/view/<int:auto_insurance_id>')
@login_required
def view_details(tenant_name , auto_insurance_id):
    validate_tenant(tenant_name)
    auto_insurance = AutoInsurance.query.filter_by(id=auto_insurance_id, tenant_id=session['tenant_id']).first_or_404()
    return render_template('autoinsurance/autoinsurance-detail-viewonly.html',auto_insurance_id=auto_insurance_id, auto_insurance=auto_insurance , tenant_name=tenant_name)

# Auto Insurance Detail Route
@autoinsurance.route('/<tenant_name>/autoinsurance/<int:auto_insurance_id>', methods=['GET', 'POST'])
@login_required
def details(tenant_name , auto_insurance_id):
    # auto_insurance = db.get_or_404(AutoInsurance.query.filter_by(tenant_id=session['tenant_id']), auto_insurance_id)
    auto_insurance = AutoInsurance.query.filter_by(id=auto_insurance_id, tenant_id=session['tenant_id']).first_or_404()
    if request.method == 'POST':
        auto_insurance.name = request.form.get("name")
        auto_insurance.street_address = request.form.get("street_address")
        auto_insurance.street_address_2 = request.form.get("street_address_2")
        auto_insurance.city = request.form.get("city")
        auto_insurance.state = request.form.get("state")
        auto_insurance.zip_code = request.form.get("zip_code")
        auto_insurance.phone_1_type = request.form.get("phone_1_type")
        auto_insurance.phone_1 = request.form.get("phone_1")
        auto_insurance.phone_2_type = request.form.get("phone_2_type")
        auto_insurance.phone_2 = request.form.get("phone_2")
        auto_insurance.phone_3_type = request.form.get("phone_3_type")
        auto_insurance.phone_3 = request.form.get("phone_3")
        auto_insurance.fax_1_type = request.form.get("fax_1_type")
        auto_insurance.fax_1 = request.form.get("fax_1")
        auto_insurance.fax_2_type = request.form.get("fax_2_type")
        auto_insurance.fax_2 = request.form.get("fax_2")
        auto_insurance.fax_3_type = request.form.get("fax_3_type")
        auto_insurance.fax_3 = request.form.get("fax_3")
        auto_insurance.email_1_type = request.form.get("email_1_type")
        auto_insurance.email_1 = request.form.get("email_1")
        auto_insurance.email_2_type = request.form.get("email_2_type")
        auto_insurance.email_2 = request.form.get("email_2")
        auto_insurance.notes = request.form.get("notes")

        db.session.commit()
        flash(f"The Auto Insurance Provider, {auto_insurance.name}, has been updated successfully", "is-success")
        return redirect(url_for('autoinsurance.index',  tenant_name=tenant_name))
    return render_template('autoinsurance/autoinsurance-detail.html',auto_insurance=auto_insurance, tenant_name=tenant_name)

# Auto Insurance Input Route
@autoinsurance.route('/<tenant_name>/new/autoinsurance', methods=['GET', 'POST'])
@login_required
def input(tenant_name):
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

        new_auto_insurance = AutoInsurance(
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
            tenant_id=session['tenant_id']  # Add tenant_id
        )
        db.session.add(new_auto_insurance)
        db.session.commit()
        flash(f"Created Auto Insurance Provider, {new_auto_insurance.name}, successfully!", "is-success")
        return redirect(url_for('autoinsurance.index' , tenant_name=tenant_name))
    return render_template('autoinsurance/autoinsurance-input.html' , tenant_name=tenant_name)
