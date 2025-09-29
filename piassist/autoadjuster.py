# from flask import Blueprint, render_template, request, redirect, url_for, flash
# from flask_login import login_required
# from piassist.models import AutoAdjuster, AutoInsurance, FirstPartyClaim, ThirdPartyClaim
# from . import db

# autoadjuster = Blueprint('autoadjuster', __name__)

# # Auto Adjuster Index Route
# @autoadjuster.route('/autoadjuster')
# @login_required
# def index():
#     auto_adjusters = AutoAdjuster.query.order_by(AutoAdjuster.last_name).all()
#     return render_template('autoadjuster/autoadjuster-index.html', auto_adjusters=auto_adjusters)

# # Auto Adjuster Detail Route
# @autoadjuster.route('/autoadjuster/<int:auto_adjuster_id>', methods=['GET', 'POST'])
# @login_required
# def details(auto_adjuster_id):
#     auto_adjuster = db.get_or_404(AutoAdjuster, auto_adjuster_id)
#     auto_insurance_providers = AutoInsurance.query.order_by(AutoInsurance.name).all()
#     first_party_claims = FirstPartyClaim.query.filter(FirstPartyClaim.auto_adjuster_id == auto_adjuster_id).all()
#     third_party_claims = ThirdPartyClaim.query.filter(ThirdPartyClaim.auto_adjuster_id == auto_adjuster_id).all()
#     if request.method == 'POST':
#         auto_adjuster.first_name = request.form.get("first_name")
#         auto_adjuster.middle_name = request.form.get("middle_name")
#         auto_adjuster.last_name = request.form.get("last_name")
#         auto_adjuster.phone = request.form.get("phone")
#         auto_adjuster.fax = request.form.get("fax")
#         auto_adjuster.email = request.form.get("email")
#         auto_adjuster.street_address = request.form.get("street_address")
#         auto_adjuster.city = request.form.get("city")
#         auto_adjuster.state = request.form.get("state")
#         auto_adjuster.zip_code = request.form.get("zip_code")

#         try:
#             auto_adjuster.auto_insurance_id = int(request.form.get("auto_insurance_id"))
#         except:
#             flash(f"The Auto Insurance Adjuster, {auto_adjuster.full_name}, isn't associated with an Auto Insurance Provider", "is-warning")

#         db.session.commit()
#         flash(f"The auto adjuster, {auto_adjuster.full_name}, has been updated successfully", "is-success")
#         return redirect(url_for('autoadjuster.index'))
#     return render_template('autoadjuster/autoadjuster-detail.html', auto_adjuster=auto_adjuster, auto_insurance_providers=auto_insurance_providers, first_party_claims=first_party_claims, third_party_claims=third_party_claims)

# # Auto Adjuster Input Route
# @autoadjuster.route('/new/autoadjuster', methods=['GET', 'POST'])
# @login_required
# def input():
#     auto_insurance_providers = AutoInsurance.query.order_by(AutoInsurance.name).all()
#     if request.method == 'POST':
#         first_name = request.form.get("first_name")
#         middle_name = request.form.get("middle_name")
#         last_name = request.form.get("last_name")
#         phone = request.form.get("phone")
#         fax = request.form.get("fax")
#         email = request.form.get("email")
#         auto_insurance_id = request.form.get("auto_insurance_id")
#         street_address = request.form.get("street_address")
#         city = request.form.get("city")
#         state = request.form.get("state")
#         zip_code = request.form.get("zip_code")

#         try:
#             auto_insurance_id = int(auto_insurance_id)
#         except:
#             flash("The new auto adjuster isn't associated with an Auto Insurance Provide", "is-warning")
#             auto_insurance_id = None

#         new_auto_adjuster = AutoAdjuster(
#             first_name=first_name,
#             middle_name=middle_name,
#             last_name=last_name,
#             phone=phone,
#             fax=fax,
#             email=email,
#             auto_insurance_id=auto_insurance_id,
#             street_address=street_address,
#             city=city,
#             state=state,
#             zip_code=zip_code
#         )
#         db.session.add(new_auto_adjuster)
#         db.session.commit()
#         flash(f"Created Auto Adjuster, {new_auto_adjuster.full_name}, successfully!", "is-success")
#         return redirect(url_for('autoadjuster.index'))
#     return render_template('autoadjuster/autoadjuster-input.html', auto_insurance_providers=auto_insurance_providers)

from flask import Blueprint, render_template, request, redirect, url_for, flash, session, abort
from flask_login import login_required
from piassist.models import AutoAdjuster, AutoInsurance, FirstPartyClaim, ThirdPartyClaim, Tenant  # Assuming a Tenant model
from . import db

autoadjuster = Blueprint('autoadjuster', __name__)

# Helper function to validate tenant
def validate_tenant(tenant_name):
    tenant = Tenant.query.filter_by(name=tenant_name).first()
    if tenant:
        session['tenant_id'] = tenant.id
        session['tenant_name'] = tenant.name
    else:
        flash("Invalid tenant specified in URL.", "is-warning")
        abort(404, description=f"Invalid tenant: '{tenant_name}'")

# Auto Adjuster Index Route
@autoadjuster.route('/<tenant_name>/autoadjuster')
@login_required
def index(tenant_name):
    validate_tenant(tenant_name)
    auto_adjusters = AutoAdjuster.query.filter_by(tenant_id=session['tenant_id']).order_by(AutoAdjuster.last_name).all()
    return render_template('autoadjuster/autoadjuster-index.html', auto_adjusters=auto_adjusters, tenant_name=tenant_name)

# Auto Adjuster Detail Route
@autoadjuster.route('/<tenant_name>/autoadjuster/<int:auto_adjuster_id>', methods=['GET', 'POST'])
@login_required
def details(tenant_name, auto_adjuster_id):
    validate_tenant(tenant_name)
    auto_adjuster = AutoAdjuster.query.filter_by(id=auto_adjuster_id, tenant_id=session['tenant_id']).first_or_404()
    auto_insurance_providers = AutoInsurance.query.order_by(AutoInsurance.name).all()
    first_party_claims = FirstPartyClaim.query.filter(FirstPartyClaim.auto_adjuster_id == auto_adjuster_id).all()
    third_party_claims = ThirdPartyClaim.query.filter(ThirdPartyClaim.auto_adjuster_id == auto_adjuster_id).all()
    
    if request.method == 'POST':
        auto_adjuster.first_name = request.form.get("first_name")
        auto_adjuster.middle_name = request.form.get("middle_name")
        auto_adjuster.last_name = request.form.get("last_name")
        auto_adjuster.phone = request.form.get("phone")
        auto_adjuster.fax = request.form.get("fax")
        auto_adjuster.email = request.form.get("email")
        auto_adjuster.street_address = request.form.get("street_address")
        auto_adjuster.city = request.form.get("city")
        auto_adjuster.state = request.form.get("state")
        auto_adjuster.zip_code = request.form.get("zip_code")

        try:
            auto_adjuster.auto_insurance_id = int(request.form.get("auto_insurance_id"))
        except ValueError:
            flash(f"The Auto Insurance Adjuster, {auto_adjuster.full_name}, isn't associated with an Auto Insurance Provider", "is-warning")

        db.session.commit()
        flash(f"The auto adjuster, {auto_adjuster.full_name}, has been updated successfully", "is-success")
        return redirect(url_for('autoadjuster.index', tenant_name=tenant_name))

    return render_template('autoadjuster/autoadjuster-detail.html', auto_adjuster=auto_adjuster, auto_insurance_providers=auto_insurance_providers, first_party_claims=first_party_claims, third_party_claims=third_party_claims, tenant_name=tenant_name)

# Auto Adjuster Input Route
@autoadjuster.route('/<tenant_name>/new/autoadjuster', methods=['GET', 'POST'])
@login_required
def input(tenant_name):
    validate_tenant(tenant_name)
    auto_insurance_providers = AutoInsurance.query.filter_by(tenant_id=session['tenant_id']).order_by(AutoInsurance.name).all()
    
    if request.method == 'POST':
        first_name = request.form.get("first_name")
        middle_name = request.form.get("middle_name")
        last_name = request.form.get("last_name")
        phone = request.form.get("phone")
        fax = request.form.get("fax")
        email = request.form.get("email")
        auto_insurance_id = request.form.get("auto_insurance_id")
        street_address = request.form.get("street_address")
        city = request.form.get("city")
        state = request.form.get("state")
        zip_code = request.form.get("zip_code")

        try:
            auto_insurance_id = int(auto_insurance_id)
        except ValueError:
            flash("The new auto adjuster isn't associated with an Auto Insurance Provider", "is-warning")
            auto_insurance_id = None

        new_auto_adjuster = AutoAdjuster(
            first_name=first_name,
            middle_name=middle_name,
            last_name=last_name,
            phone=phone,
            fax=fax,
            email=email,
            auto_insurance_id=auto_insurance_id,
            street_address=street_address,
            city=city,
            state=state,
            zip_code=zip_code,
            tenant_id=session['tenant_id']
        )
        db.session.add(new_auto_adjuster)
        db.session.commit()
        flash(f"Created Auto Adjuster, {new_auto_adjuster.full_name}, successfully!", "is-success")
        return redirect(url_for('autoadjuster.index', tenant_name=tenant_name))

    return render_template('autoadjuster/autoadjuster-input.html', auto_insurance_providers=auto_insurance_providers, tenant_name=tenant_name)
