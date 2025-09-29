from flask import Blueprint, request, render_template, redirect, url_for, flash , session, abort
from flask_login import login_required
from datetime import datetime 
from piassist.models import FirstPartyClaim, AutoAdjuster, AutoInsurance , Tenant
from . import db

firstpartyclaim = Blueprint('firstpartyclaim', __name__)

def validate_tenant(tenant_name):
    tenant = Tenant.query.filter_by(name=tenant_name).first()
    if tenant:
        session['tenant_id'] = tenant.id
        session['tenant_name'] = tenant.name
    else:
        flash("Invalid tenant specified in URL.", "is-warning")
        abort(404, description=f"Invalid tenant: '{tenant_name}'")

# Auto Claim Detail Route
@firstpartyclaim.route('/<tenant_name>/casefile/<int:casefile_id>/firstpartyclaim/<int:auto_insurance_id>', methods=['GET', 'POST'])
@login_required
def details(tenant_name , casefile_id, auto_insurance_id):
    validate_tenant(tenant_name)
    first_party_claim = FirstPartyClaim.query.filter_by(casefile_id=casefile_id, auto_insurance_id=auto_insurance_id, tenant_id=session['tenant_id']).first_or_404()
    auto_adjusters = AutoAdjuster.query.filter_by(auto_insurance_id=auto_insurance_id, tenant_id=session['tenant_id']).all()
    # first_party_claim = db.get_or_404(FirstPartyClaim, (casefile_id, auto_insurance_id))
    # auto_adjusters = AutoAdjuster.query.filter(AutoAdjuster.auto_insurance_id == auto_insurance_id).all()
    if request.method == 'POST':
        first_party_claim.policy_number = request.form.get("policy_number")
        first_party_claim.is_started = request.form.get("is_started")
        first_party_claim.claim_number = request.form.get("claim_number")
        first_party_claim.is_statement = request.form.get("is_statement")
        first_party_claim.has_medpay = request.form.get("has_medpay")
        first_party_claim.has_um_coverage = request.form.get("has_um_coverage")
        first_party_claim.um_amount = request.form.get("um_amount")
        first_party_claim.notes = request.form.get("notes")
        first_party_claim.is_lor_sent = request.form.get("is_lor_sent")
        first_party_claim.is_loa_received = request.form.get("is_loa_received")
        first_party_claim.is_dec_sheets_received = request.form.get("is_dec_sheets_received")


        try:
            first_party_claim.medpay_amount = int(request.form.get("medpay_amount"))
        except:
            flash("Couldn't save medpay amount on first party claim because it's not an integer.", "is-warning")

        try:
            first_party_claim.auto_adjuster_id = int(request.form.get("auto_adjuster_id"))
        except:
            flash("The first party claim isn't associated with an Auto Insurance Adjuster", "is-warning")

        try:
            first_party_claim.last_request_date = datetime.strptime(request.form.get("last_request_date"), '%Y-%m-%d').date()
        except:
            flash("Last request date couldn't be saved.", "is-warning")
            
        db.session.commit()
        flash(f"The First Party Auto Claim has been updated successfully", "is-success")
        return redirect(url_for('casefile.details',tenant_name=tenant_name,  casefile_id=casefile_id))
    
    return render_template('firstpartyclaim/first-party-claim-detail.html',tenant_name=tenant_name,casefile_id=casefile_id,auto_insurance_id=auto_insurance_id, first_party_claim=first_party_claim, auto_adjusters=auto_adjusters)

# Auto Claim Input Route
@firstpartyclaim.route('/<tenant_name>/new/firstpartyclaim/casefile/<int:casefile_id>', methods=['GET', 'POST'])
@login_required
def input(tenant_name , casefile_id):
    validate_tenant(tenant_name)
    auto_insurance_providers = AutoInsurance.query.filter_by(tenant_id=session['tenant_id']).order_by(AutoInsurance.name).all()
    # auto_insurance_providers = AutoInsurance.query.order_by(AutoInsurance.name).all()
    if request.method == 'POST':
        auto_insurance_id = request.form.get("auto_insurance_id")
        policy_number = request.form.get("policy_number")
        is_started = request.form.get("is_started")
        claim_number = request.form.get("claim_number")
        is_statement = request.form.get("is_statement")
        has_medpay = request.form.get("has_medpay")
        medpay_amount = request.form.get("medpay_amount")
        has_um_coverage = request.form.get("has_um_coverage")
        um_amount = request.form.get("um_amount")
        notes = request.form.get("notes")
        is_lor_sent = request.form.get("is_lor_sent")
        is_loa_received = request.form.get("is_loa_received")
        is_dec_sheets_received = request.form.get("is_dec_sheets_received")
        last_request_date = request.form.get("last_request_date")


        try:
            medpay_amount = int(medpay_amount)
        except:
            flash("Couldn't save medpay amount on first party claim because it's not an integer.", "is-warning")
            medpay_amount = None

        try:
            um_amount = int(um_amount)
        except:
            flash("Couldn't save UM amount on first party claim because it's not an integer.", "is-warning")
            um_amount = None

        try:
            last_request_date = datetime.strptime(request.form.get("last_request_date"), '%Y-%m-%d').date()
        except:
            flash("Last request date couldn't be saved.", "is-warning")
            last_request_date = None
        
        try:
            auto_insurance_id = int(auto_insurance_id)
            new_first_party_claim = FirstPartyClaim(
                casefile_id = casefile_id,
                auto_insurance_id = auto_insurance_id,
                policy_number = policy_number,
                is_started = is_started,
                claim_number = claim_number,
                is_statement = is_statement,
                has_medpay = has_medpay,
                medpay_amount = medpay_amount,
                has_um_coverage = has_um_coverage,
                um_amount = um_amount,
                notes = notes,
                is_lor_sent = is_lor_sent,
                is_loa_received = is_loa_received,
                is_dec_sheets_received = is_dec_sheets_received,
                last_request_date = last_request_date,
                tenant_id=session['tenant_id'],
            )
            db.session.add(new_first_party_claim)
            db.session.commit()
            flash(f"The New First Party Auto Claim has been created successfully", "is-success")
        except:
            # NEED TO ADD AN ABORT HERE
            flash("Error failed to create first party auto claim. Make sure you associate the claim with an Auto Insurance Provider", "is-danger")

        return redirect(url_for('casefile.details', tenant_name=tenant_name, casefile_id = casefile_id))
    return render_template('firstpartyclaim/first-party-claim-input.html', auto_insurance_providers=auto_insurance_providers,tenant_name=tenant_name, casefile_id=casefile_id)

# DELETE FIRST PARTY CLAIM ROUTE
@firstpartyclaim.route('/<tenant_name>/delete/casefile/<int:casefile_id>/firstpartyclaim/<int:auto_insurance_id>')
@login_required
def delete(tenant_name , casefile_id, auto_insurance_id):
    validate_tenant(tenant_name)
    firstpartyclaim = FirstPartyClaim.query.filter_by(id=casefile_id, auto_insurance_id=auto_insurance_id, tenant_id=session['tenant_id']).first_or_404()
    # firstpartyclaim = db.get_or_404(FirstPartyClaim, (casefile_id, auto_insurance_id))
    db.session.delete(firstpartyclaim)
    db.session.commit()
    flash(f"First Party Claim for Auto Provider {auto_insurance_id} Deleted Successfully", "is-success")
    return redirect(url_for('casefile.details', tenant_name=tenant_name, casefile_id=casefile_id))