import os
import base64
from datetime import datetime
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from flask import Blueprint, render_template, request, redirect, url_for,session,flash,abort
from flask_login import login_required
from . import db
from piassist.models import Casefile, Client, MedicalBill, MedicalProvider, HealthInsurance, AutoInsurance, Defendant, HealthClaim, FirstPartyClaim, ThirdPartyClaim,Tenant

import os

crystal_key = os.environ.get("CRYSTAL_KEY")


intake = Blueprint('intake', __name__)
def validate_tenant(tenant_name):
    tenant = Tenant.query.filter_by(name=tenant_name).first()
    if tenant:
        session['tenant_id'] = tenant.id
        session['tenant_name'] = tenant.name
    else:
        flash("Invalid tenant specified in URL.", "is-warning")
        abort(404, description=f"Invalid tenant: '{tenant_name}'")

@intake.route('/<tenant_name>/intake', methods=['POST', 'GET'])
@login_required
def primary(tenant_name):
    validate_tenant(tenant_name)
    medical_providers = MedicalProvider.query.filter_by(tenant_id=session['tenant_id']).order_by(MedicalProvider.name).all()
    health_insurance_providers = HealthInsurance.query.filter_by(tenant_id=session['tenant_id']).order_by(HealthInsurance.name).all()
    auto_insurance_providers = AutoInsurance.query.filter_by(tenant_id=session['tenant_id']).order_by(AutoInsurance.name).all()
    # medical_providers = MedicalProvider.query.order_by(MedicalProvider.name).all()
    # health_insurance_providers = HealthInsurance.query.order_by(HealthInsurance.name).all()
    # auto_insurance_providers = AutoInsurance.query.order_by(AutoInsurance.name).all()
    if request.method == 'POST':
        # Get User Inputs
        # Casefile
        client_count = int(request.form.get('client_count'))
        defendant_count = int(request.form.get('defendant_count'))
        date_of_loss = request.form.get('date_of_loss')
        time_of_wreck = request.form.get('time_of_wreck')
        wreck_type = request.form.get('wreck_type')
        wreck_street = request.form.get('wreck_street')
        wreck_city = request.form.get('wreck_city')
        wreck_state = request.form.get('wreck_state')
        wreck_county = request.form.get('wreck_county')
        wreck_description = request.form.get('wreck_description')
        is_police_involved = request.form.get('is_police_involved')
        police_force = request.form.get('police_force')
        is_police_report = request.form.get('is_police_report')
        police_report_number = request.form.get('police_report_number')
        vehicle_description = request.form.get('vehicle_description')
        damage_level = request.form.get('damage_level')
        wreck_notes = request.form.get('wreck_notes')
        # Client 1
        client_number = 1
        is_driver = request.form.get('is_driver')
        first_name = request.form.get('first_name')
        middle_name = request.form.get('middle_name')
        last_name = request.form.get('last_name')
        marital_status = request.form.get('marital_status')
        dob = request.form.get('dob')
        ssn = request.form.get('ssn') # Hash this
        if ssn:
            crystal_key = os.environ.get("CRYSTAL_KEY").encode()

            if crystal_key is None:
               raise ValueError("CRYSTAL_KEY environment variable is not set.")
    
    # Now, you can safely encode it
            # crystal_key = crystal_key.encode()
            nacl = os.urandom(16)
            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=32,
                salt=nacl,
                iterations=480000
            )
            f_key = base64.urlsafe_b64encode(kdf.derive(crystal_key))
            f = Fernet(f_key)
            f_token = f.encrypt(ssn.encode())
        else:
            f_token = None
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
        # medical provider
        med_providers = request.form.getlist('med_provider')
        has_hi = request.form.get('has_hi')
        # health insurance
        health_insurance_id = request.form.get('health_insurance_id')
        member_id = request.form.get('member_id')
        had_prior_injury = request.form.get('had_prior_injury')
        prior_injury_notes = request.form.get('prior_injury_notes')
        had_prior_accident = request.form.get('had_prior_accident')
        prior_accident_notes = request.form.get('prior_accident_notes')
        was_work_impacted = request.form.get('was_work_impacted')
        work_impacted_notes = request.form.get('work_impacted_notes')
        # first party auto claim
        auto_insurance_id = request.form.get('auto_insurance_id')
        policy_number = request.form.get('policy_number')
        has_medpay = request.form.get('has_medpay')
        medpay_amount = request.form.get('medpay_amount')
        has_um_coverage = request.form.get('has_um_coverage')
        um_amount = request.form.get('um_amount')
        is_started = request.form.get('is_started')
        is_statement = request.form.get('is_statement')
        claim_number = request.form.get('claim_number')

        # Create Casefile
        # Try to Convert Casefile DateTimes
        try:
            date_of_loss=datetime.strptime(date_of_loss, '%Y-%m-%d').date()
        except:
            print("Couldn't Convert Date of Loss")
            date_of_loss=None

        try:
            time_of_wreck = datetime.strptime(time_of_wreck, '%H:%M').time()
        except:
            print("Couldn't Convert Time of Wreck")
            time_of_wreck=None

        try:
            medpay_amount = int(medpay_amount)
        except:
            print("Couldn't convert medpay amount")
            medpay_amount=None

        new_case = Casefile(
            client_count=client_count,
            defendant_count=defendant_count,
            date_of_loss=date_of_loss,
            time_of_wreck=time_of_wreck,
            wreck_type=wreck_type,
            wreck_street=wreck_street,
            wreck_city=wreck_city,
            wreck_state=wreck_state,
            wreck_county=wreck_county,
            wreck_description=wreck_description,
            is_police_involved=is_police_involved,
            police_force=police_force,
            is_police_report=is_police_report,
            police_report_number=police_report_number,
            vehicle_description=vehicle_description,
            damage_level=damage_level,
            wreck_notes=wreck_notes,
            tenant_id = session['tenant_id']
        )

        # Create Primary Client and Append to Casefile
        # Try DateTime Conversions
        try:
            dob = datetime.strptime(dob, '%Y-%m-%d').date()
        except:
            print("Couldn't Convert Date of Birth")
            dob = None

        new_primary_client = Client(
            client_number=client_number,
            is_driver=is_driver,
            first_name=first_name,
            middle_name=middle_name,
            last_name=last_name,
            marital_status=marital_status,
            dob=dob,
            physical_identifier=f_token,
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
            has_hi=has_hi,
            had_prior_injury=had_prior_injury,
            prior_injury_notes=prior_injury_notes,
            had_prior_accident=had_prior_accident,
            prior_accident_notes=prior_accident_notes,
            was_work_impacted=was_work_impacted,
            work_impacted_notes=work_impacted_notes,
            tenant_id = session['tenant_id']
        )
        new_case.clients.append(new_primary_client)

        # Create Medical Providers and Append to Medical Bills
        for med_provider in med_providers:
            try:
                medical_provider_id = int(med_provider)
                new_medical_bill = MedicalBill(medical_provider_id=medical_provider_id,tenant_id=session['tenant_id'])
                new_primary_client.medical_bills.append(new_medical_bill)
            except:
                print("Medical Provider Blank")

        # Create Health Claim and Append to Client
        try:
            health_insurance_id = int(health_insurance_id)
            new_health_claim = HealthClaim(
                health_insurance_id = health_insurance_id,
                member_id = member_id,
                tenant_id = session['tenant_id']
                
            )
            new_primary_client.health_claims.append(new_health_claim)
            
        except:
            print("Health Insurance Id Empty")

        # Create First Party Auto Claim and Append to Client
        try:
            auto_insurance_id = int(auto_insurance_id)
            new_first_party_claim = FirstPartyClaim(
                auto_insurance_id = auto_insurance_id,
                claim_number = claim_number,
                is_started = is_started,
                is_statement = is_statement,
                policy_number = policy_number,
                has_medpay = has_medpay,
                medpay_amount = medpay_amount,
                has_um_coverage = has_um_coverage,
                um_amount = um_amount,
                tenant_id = session['tenant_id']
            )
            new_case.first_party_claims.append(new_first_party_claim)
        except:
            print("Auto Insurance Id Empty")

        # Commit To Database
        db.session.add(new_case)
        db.session.commit()

        # Return generated casefile_id so we can pass it forwards
        new_case_id = new_case.id

        # Go To Next View
        if client_count > 1:
            return render_template('intake/client-intake.html', case_id=new_case_id, client_number=2, client_count=client_count, defendant_count=defendant_count, medical_providers=medical_providers, tenant_name=tenant_name, auto_insurance_providers=auto_insurance_providers, health_insurance_providers=health_insurance_providers)
        else:
            return render_template('intake/defendant-intake.html', case_id=new_case_id, defendant_count=defendant_count, defendant_number=1, tenant_name=tenant_name, auto_insurance_providers=auto_insurance_providers)

    return render_template('intake/case-intake.html', medical_providers=medical_providers, tenant_name=tenant_name, health_insurance_providers=health_insurance_providers, auto_insurance_providers=auto_insurance_providers)

@intake.route('/<tenant_name>/intake/client', methods=['POST', 'GET'])
@login_required
def client(tenant_name):
    validate_tenant(tenant_name)
    # medical_providers = MedicalProvider.query.order_by(MedicalProvider.name).all()
    # health_insurance_providers = HealthInsurance.query.order_by(HealthInsurance.name).all()
    # auto_insurance_providers = AutoInsurance.query.order_by(AutoInsurance.name).all()
    medical_providers = MedicalProvider.query.filter_by(tenant_id=session['tenant_id']).order_by(MedicalProvider.name).all()
    health_insurance_providers = HealthInsurance.query.filter_by(tenant_id=session['tenant_id']).order_by(HealthInsurance.name).all()
    auto_insurance_providers = AutoInsurance.query.filter_by(tenant_id=session['tenant_id']).order_by(AutoInsurance.name).all()
    if request.method == 'POST':
        # Get User Inputs
        case_id = request.form.get("case_id")
        client_number = request.form.get("client_number")
        client_count = request.form.get("client_count")
        defendant_count = request.form.get("defendant_count")
        is_driver = request.form.get("is_driver")
        first_name = request.form.get("first_name")
        middle_name = request.form.get("middle_name")
        last_name = request.form.get("last_name")
        marital_status = request.form.get("marital_status")
        dob = request.form.get("dob")
        ssn = request.form.get("ssn") #HASH THIS
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
            f_token = f.encrypt(ssn.encode())
        else:
            f_token = None
            nacl = None
        street_address = request.form.get("street_address")
        city = request.form.get("city")
        state = request.form.get("state")
        zip_code = request.form.get("zip_code")
        primary_phone = request.form.get("primary_phone")
        secondary_phone = request.form.get("secondary_phone")
        email = request.form.get("email")
        referrer = request.form.get("referrer")
        referrer_relationship = request.form.get("referrer_relationship")
        injuries = request.form.get("injuries")
        rode_ambulance = request.form.get("rode_ambulance")
        visited_hospital = request.form.get("visited_hospital")
        # medical providers
        med_providers = request.form.getlist("med_provider")
        has_hi = request.form.get("has_hi")
        # health insurance
        member_id = request.form.get("hi_member_id")
        had_prior_injury = request.form.get("had_prior_injury")
        prior_injury_notes = request.form.get("prior_injury_notes")
        had_prior_accident = request.form.get("had_prior_accident")
        prior_accident_notes = request.form.get("prior_accident_notes")
        was_work_impacted = request.form.get("was_work_impacted")
        work_impacted_notes = request.form.get("work_impacted_notes")
        # auto insurance

        # Try Datatype conversions
        try:
            dob = datetime.strptime(dob, '%Y-%m-%d').date()
        except:
            print("Couldn't convert date of birth")
            dob = None

        try:
            client_number = int(client_number)
        except:
            print("Couldn't convert client number")
            client_number = None

        try:
            client_count = int(client_count)
        except:
            print("Couldn't convert client count")
            client_count = None

        try:
            defendant_count = int(defendant_count)
        except:
            print("Couldn't Convert defendant count")
            defendant_count = None


        # Commit To Database
        new_client = Client(
            casefile_id=case_id,
            client_number=client_number,
            is_driver=is_driver,
            first_name=first_name,
            middle_name=middle_name,
            last_name=last_name,
            marital_status=marital_status,
            dob=dob,
            physical_identifier=f_token,
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
            injuries=injuries,
            rode_ambulance=rode_ambulance,
            visited_hospital=visited_hospital,
            has_hi=has_hi,
            had_prior_injury=had_prior_injury,
            prior_injury_notes=prior_injury_notes,
            had_prior_accident=had_prior_accident,
            prior_accident_notes=prior_accident_notes,
            was_work_impacted=was_work_impacted,
            work_impacted_notes=work_impacted_notes,
            tenant_id = session['tenant_id']
        )

        # Create Medical Providers and Append to Client
        for med_provider in med_providers:
            try:
                medical_provider_id = int(med_provider)
                new_medical_bill = MedicalBill(medical_provider_id=medical_provider_id)
                new_client.medical_bills.append(new_medical_bill)
            except:
                print("Medical Provider Blank")

        # Create Health Claim and Append to Client
        try:
            health_insurance_id = int(health_insurance_id)
            new_health_claim = HealthClaim(
                health_insurance_id=health_insurance_id,
                member_id=member_id
            )
            new_client.health_claims.append(new_health_claim)
        except:
            print("No Health Claim Added")

        db.session.add(new_client)
        db.session.commit()

        # Go To Next View
        # MOVE TO NEXT FORM
        if client_number < client_count:
            # Next Client
            client_number += 1
            return render_template('intake/client-intake.html', case_id=case_id,tenant_name=tenant_name, client_number=client_number, client_count=client_count, defendant_count=defendant_count, medical_providers=medical_providers, health_insurance_providers=health_insurance_providers, auto_insurance_providers=auto_insurance_providers)
        else:
            # Defendant
            return render_template('intake/defendant-intake.html', case_id=case_id,tenant_name=tenant_name, defendant_number=1, defendant_count=defendant_count, auto_insurance_providers=auto_insurance_providers)

    return render_template('intake/client-intake.html', medical_providers=medical_providers,tenant_name=tenant_name, health_insurance_providers=health_insurance_providers, auto_insurance_providers=auto_insurance_providers)

@intake.route('/<tenant_name>/intake/defendant', methods=['POST', 'GET'])
@login_required
def defendant(tenant_name):
    validate_tenant(tenant_name)
    # auto_insurance_providers = AutoInsurance.query.order_by(AutoInsurance.name).all()
    auto_insurance_providers = AutoInsurance.query.filter_by(tenant_id=session['tenant_id']).order_by(AutoInsurance.name).all()
    if request.method == 'POST':
        pass
        # Get User Inputs
        case_id = request.form.get("case_id")
        defendant_number = int(request.form.get("defendant_number"))
        defendant_count = request.form.get("defendant_count")
        first_name = request.form.get("first_name")
        last_name = request.form.get("last_name")
        is_policyholder = request.form.get("is_policyholder")
        policyholder_first_name = request.form.get("policy_holder_first_name")
        policyholder_last_name = request.form.get("policyholder_last_name")
        rode_ambulance = request.form.get("rode_ambulance")
        auto_insurance_id = request.form.get("auto_insurance_id")
        policy_number = request.form.get("policy_number")
        is_started = request.form.get("is_started")
        is_statement = request.form.get("is_statement")
        claim_number = request.form.get("claim_number")
        notes = request.form.get("notes")

        try:
            defendant_number = int(defendant_number)
        except:
            print("Couldn't convert client number")
            defendant_number = None

        try:
            defendant_count = int(defendant_count)
        except:
            print("Couldn't convert client count")
            defendant_count = None

        try:
            auto_insurance_id = int(auto_insurance_id)
            # Commit To Database
            new_defendant = Defendant(
                casefile_id=case_id,
                defendant_number=defendant_number,
                first_name=first_name,
                last_name=last_name,
                is_policyholder=is_policyholder,
                policyholder_first_name=policyholder_first_name,
                policyholder_last_name=policyholder_last_name,
                rode_ambulance=rode_ambulance,
                auto_insurance_id=auto_insurance_id,
                policy_number=policy_number,
                notes=notes,
                tenant_id = session['tenant_id']
            )
            new_claim = ThirdPartyClaim(
                auto_insurance_id = auto_insurance_id,
                claim_number = claim_number,
                is_started = is_started,
                is_statement = is_statement,
                tenant_id = session['tenant_id']
            )
            new_defendant.auto_claim = new_claim

            db.session.add(new_defendant)
            db.session.commit()
        except:
             print("Couldn't make either :()")

        # Go To Next View
        if defendant_number < defendant_count:
            # NEXT DEFENDANT
            defendant_number += 1
            return render_template('intake/defendant-intake.html', case_id=case_id,tenant_name= tenant_name, defendant_number=defendant_number, defendant_count=defendant_count, auto_insurance_providers=auto_insurance_providers)
        else:
            # FINISH INTAKE & GO TO CASELOG
            return redirect(url_for('casefile.index',tenant_name=tenant_name))
    return render_template('intake/defendant-intake.html',tenant_name=tenant_name)