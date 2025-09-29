from datetime import datetime
from flask import Blueprint, request, render_template, redirect, url_for, flash,session,abort
from flask_login import login_required
from piassist.models import ThirdPartyClaim, AutoAdjuster, AutoInsurance, Defendant,Tenant
from . import db

thirdpartyclaim = Blueprint('thirdpartyclaim', __name__)
def validate_tenant(tenant_name):
    tenant = Tenant.query.filter_by(name=tenant_name).first()
    if tenant:
        session['tenant_id'] = tenant.id
        session['tenant_name'] = tenant.name
    else:
        flash("Invalid tenant specified in URL.", "is-warning")
        abort(404, description=f"Invalid tenant: '{tenant_name}'")

# Auto Claim Detail Route
@thirdpartyclaim.route('/<tenant_name>/defendant/<int:defendant_id>/thirdpartyclaim/<int:auto_insurance_id>', methods=['GET', 'POST'])
@login_required
def details(tenant_name, defendant_id, auto_insurance_id):
    validate_tenant(tenant_name)
    # third_party_claim = db.get_or_404(ThirdPartyClaim, (defendant_id, auto_insurance_id))
    third_party_claim = ThirdPartyClaim.query.filter_by(auto_insurance_id=auto_insurance_id, defendant_id=defendant_id, tenant_id=session['tenant_id']).first_or_404()
    # auto_adjusters = AutoAdjuster.query.filter(AutoAdjuster.auto_insurance_id == auto_insurance_id).all()
    auto_adjusters = AutoAdjuster.query.filter_by(auto_insurance_id=auto_insurance_id, tenant_id=session['tenant_id']).all()
    
    if request.method == 'POST':
        third_party_claim.is_started = request.form.get("is_started")
        third_party_claim.claim_number = request.form.get("claim_number")
        third_party_claim.is_statement = request.form.get("is_statement")
        third_party_claim.is_lor_sent = request.form.get("is_lor_sent")
        third_party_claim.is_loa_received = request.form.get("is_loa_received")
        third_party_claim.notes = request.form.get("notes")

        try:
            third_party_claim.auto_adjuster_id = int(request.form.get("auto_adjuster_id"))
        except:
            flash("Auto Insurace Adjuster not updated for Third Party Claim", "is-warning")
        
        try:
            third_party_claim.last_request_date = datetime.strptime(request.form.get("last_request_date"), '%Y-%m-%d').date()
        except:
            flash("Last request date couldn't be saved.", "is-warning")
        
        db.session.commit()
        flash("Third Party Claim Updated Successfully", "is-success")
        return redirect(url_for('casefile.details',tenant_name=tenant_name, casefile_id = third_party_claim.defendant.casefile_id))
    
    return render_template('thirdpartyclaim/third-party-claim-detail.html',defendant_id=defendant_id,tenant_name=tenant_name,auto_insurance_id=auto_insurance_id, third_party_claim=third_party_claim, auto_adjusters=auto_adjusters)

# Defendant Input Route
@thirdpartyclaim.route('/<tenant_name>/new/thirdpartyclaim/defendant/casefile/<int:casefile_id>', methods=['GET', 'POST'])
@login_required
def input(tenant_name , casefile_id):
    validate_tenant(tenant_name)
    # auto_insurance_providers = AutoInsurance.query.order_by(AutoInsurance.name).all()
    auto_insurance_providers = AutoInsurance.query.filter_by(tenant_id=session['tenant_id']).order_by(AutoInsurance.name).all()
    if request.method == 'POST':
        first_name = request.form.get("first_name")
        last_name = request.form.get("last_name")
        is_policyholder = request.form.get("is_policyholder")
        policyholder_first_name = request.form.get("policyholder_first_name")
        policyholder_last_name = request.form.get("policyholder_last_name")
        rode_ambulance = request.form.get("rode_ambulance")
        auto_insurance_id = request.form.get("auto_insurance_id")
        policy_number = request.form.get("policy_number")
        is_started = request.form.get("is_started")
        claim_number = request.form.get("claim_number")
        is_statement = request.form.get("is_statement")
        last_request_date = request.form.get("last_request_date")
        notes = request.form.get("notes")

        try:
            last_request_date = datetime.strptime(request.form.get("last_request_date"), '%Y-%m-%d').date()
        except:
            flash("Last request date couldn't be saved.", "is-warning")
            last_request_date = None

        try:
            auto_insurance_id = int(auto_insurance_id)
            new_defendant = Defendant(
                casefile_id=casefile_id,
                first_name = first_name,
                last_name = last_name,
                is_policyholder = is_policyholder,
                policyholder_first_name = policyholder_first_name,
                policyholder_last_name = policyholder_last_name,
                rode_ambulance = rode_ambulance,
                policy_number = policy_number,
                auto_insurance_id = auto_insurance_id,
                notes = notes,
                tenant_id=session['tenant_id']
            )
            new_claim = ThirdPartyClaim(
                auto_insurance_id=auto_insurance_id,
                is_started = is_started,
                claim_number = claim_number,
                is_statement = is_statement,
                last_request_date = last_request_date,
                tenant_id=session['tenant_id']
            )
            new_defendant.auto_claim = new_claim

            db.session.add(new_defendant)
            db.session.commit()
            flash("New Defendant and Third Party Claim Created Successfully", "is-success")
        except:
            flash("Couldn't Create New Defendant and Third Party Claim.", "is-danger")

        return redirect(url_for('casefile.details',tenant_name=tenant_name, casefile_id = casefile_id))
    return render_template('thirdpartyclaim/third-party-claim-input.html',tenant_name=tenant_name, auto_insurance_providers=auto_insurance_providers, casefile_id=casefile_id)


# DELETE THIRD PARTY CLAIM ROUTE
@thirdpartyclaim.route('/<tenant_name>/delete/defendant/<int:defendant_id>')
@login_required
def delete(tenant_name , defendant_id):
    validate_tenant(tenant_name)
    defendant = Defendant.query.filter_by( id=defendant_id, tenant_id=session['tenant_id']).first_or_404()
    try:
        db.session.delete(defendant)
        db.session.commit()
        flash(f"Defendant deleted successfuly", "is-success")
    except:
        flash('Something went wrong', 'is-danger')
    return redirect(url_for('casefile.details',tenant_name=tenant_name, casefile_id = defendant.casefile_id))