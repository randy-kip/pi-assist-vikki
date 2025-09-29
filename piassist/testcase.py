import os
import base64
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from .models import *
import click

# Create 2 Client, 2 Defendant Case
@click.command('create-multi')
def create_multi():
    ssn = "111-22-3333"
    my_salt = os.urandom(16)
    crystal_key = os.environ.get("CRYSTAL_KEY").encode()
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=my_salt,
        iterations=480000
    )
    f_key = base64.urlsafe_b64encode(kdf.derive(crystal_key))
    f = Fernet(f_key)
    f_token = f.encrypt(ssn.encode())
    new_casefile = Casefile(
        status = "Intake",
        stage = "Incomplete",
        client_count = 2,
        defendant_count = 2,
        date_of_loss = "2023-04-01",
        time_of_wreck = "12:00:00",
        wreck_type = "REAREND",
        wreck_street = "Street & Avenue",
        wreck_city = "Town City",
        wreck_state = "OK",
        wreck_county = "Here County",
        wreck_description = "Chain reaction rear end",
        is_police_involved = "True",
        police_force = "PolicePD",
        is_police_report = "True",
        police_report_number = "2023-111",
        vehicle_description = "Year Make Model",
        damage_level = 5,
        wreck_notes = "This one is a doozy"
    )
    new_client_1 = Client(
        client_number = 1,
        first_name = "Rachel",
        middle_name = "Karen",
        last_name = "Green",
        dob = "1980-01-01",
        # Have Kendal Help Me With These Two
        physical_identifier = f_token,
        nacl = my_salt,
        marital_status = "Single",
        street_address = "111 Street St",
        city = "Town City",
        state = "NY",
        zip_code = "10000",
        primary_phone = "555-555-5555",
        secondary_phone = "999-999-9999",
        email = "rachel@gmail.com",
        referrer = "Crane",
        referrer_relationship = "DC",
        notes = "Important client",
        injuries = "Whiplash, broken wrist, seat belt burn",
        rode_ambulance = "True",
        visited_hospital = "True",
        has_hi = "True",
        had_prior_injury = "False",
        prior_injury_notes = "None",
        had_prior_accident = "False",
        prior_accident_notes = "None",
        was_work_impacted = "True",
        work_impacted_notes = "Log will be sent",
        is_driver = "True"
    )
    new_client_2 = Client(
        client_number = 2,
        first_name = "Monica",
        middle_name = "E",
        last_name = "Gellar-Bing",
        dob = "1980-12-01",
        # Have Kendal Help Me With These Two
        physical_identifier = f_token,
        nacl = my_salt,
        marital_status = "Married",
        street_address = "999 Street St",
        city = "Town City",
        state = "NY",
        zip_code = "10000",
        primary_phone = "333-333-3333",
        secondary_phone = "222-222-2222",
        email = "monica@gmail.com",
        referrer = "Crane",
        referrer_relationship = "DC",
        notes = "Important client",
        injuries = "Whiplash, headaches, seat belt burn",
        rode_ambulance = "False",
        visited_hospital = "False",
        has_hi = "True",
        had_prior_injury = "False",
        prior_injury_notes = "None",
        had_prior_accident = "False",
        prior_accident_notes = "None",
        was_work_impacted = "True",
        work_impacted_notes = "See log",
        is_driver = "False"
    )
    new_defendant_1 = Defendant(
        defendant_number = 1,
        liability = "70%",
        first_name = "Phoebe",
        last_name = "Buffay",
        is_policyholder = "True",
        policyholder_first_name = "Phoebe",
        policyholder_last_name = "Buffay",
        rode_ambulance = "True",
        auto_insurance_id = 1052,
        policy_number = "G-000-1111",
        notes = "Was cited for texting at time of accident"
    )
    new_defendant_2 = Defendant(
        defendant_number = 2,
        liability = "30%",
        first_name = "Joey",
        last_name = "Tribiani",
        is_policyholder = "True",
        policyholder_first_name = "Joey",
        policyholder_last_name = "Tribiani",
        rode_ambulance = "True",
        auto_insurance_id = 1050,
        policy_number = "ZZZ-555-0000",
        notes = "Was middle vehicle"
    )
    new_first_party_claim = FirstPartyClaim(
        auto_insurance_id = 1067,
        claim_number = "ONO-666-111",
        is_started = "True",
        is_statement = "False",
        policy_number = "LLL-33333",
        has_medpay = "True",
        medpay_amount = 5000,
        has_um_coverage = "True",
        um_amount = "100/300",
        is_lor_sent = "False",
        is_loa_received = "False",
        is_dec_sheets_received = "False",
        notes = "None"
    )
    new_third_party_claim_1 = ThirdPartyClaim(
        auto_insurance_id = new_defendant_1.auto_insurance_id,
        claim_number = "XX-00000",
        is_started = "True",
        is_statement = "False",
        is_lor_sent = "False",
        is_loa_received = "False",
        notes = "None"
    )
    new_third_party_claim_2 = ThirdPartyClaim(
        auto_insurance_id = new_defendant_2.auto_insurance_id,
        claim_number = "QQ-00000",
        is_started = "True",
        is_statement = "False",
        is_lor_sent = "False",
        is_loa_received = "False",
        notes = "None"
    )
    new_health_claim_1 = HealthClaim(
        health_insurance_id = 15,
        member_id = "QQQ000999",
        event_number = "B56789",
        is_hipaa_sent = "False",
        is_lor_sent = "False",
        is_log_received = "False",
        notes = ""
    )
    new_health_claim_2 = HealthClaim(
        health_insurance_id = 15,
        member_id = "QQQ444666",
        event_number = "B12345",
        is_hipaa_sent = "False",
        is_lor_sent = "False",
        is_log_received = "False",
        notes = ""
    )
    new_medical_bill_1 = MedicalBill(
        medical_provider_id = 62,
        is_hipaa_sent = "False",
        is_bill_received = "False",
        is_record_received = "False",
        total_billed = 0,
        insurance_paid = 0,
        insurance_adjusted = 0,
        is_lien_filed = "False",
        is_in_collections = "False"
    )
    new_medical_bill_2 = MedicalBill(
        medical_provider_id = 143,
        is_hipaa_sent = "False",
        is_bill_received = "False",
        is_record_received = "False",
        total_billed = 0,
        insurance_paid = 0,
        insurance_adjusted = 0,
        is_lien_filed = "False",
        is_in_collections = "False"
    )
    new_medical_bill_3 = MedicalBill(
        medical_provider_id = 126,
        is_hipaa_sent = "False",
        is_bill_received = "False",
        is_record_received = "False",
        total_billed = 0,
        insurance_paid = 0,
        insurance_adjusted = 0,
        is_lien_filed = "False",
        is_in_collections = "False"
    )
    new_medical_bill_4 = MedicalBill(
        medical_provider_id = 126,
        is_hipaa_sent = "False",
        is_bill_received = "False",
        is_record_received = "False",
        total_billed = 0,
        insurance_paid = 0,
        insurance_adjusted = 0,
        is_lien_filed = "False",
        is_in_collections = "False"
    )

    # Start making connections
    new_defendant_1.auto_claim = new_third_party_claim_1
    new_defendant_2.auto_claim = new_third_party_claim_2
    new_client_1.health_claims.append(new_health_claim_1)
    new_client_2.health_claims.append(new_health_claim_2)
    new_client_1.medical_bills.append(new_medical_bill_1)
    new_client_1.medical_bills.append(new_medical_bill_2)
    new_client_1.medical_bills.append(new_medical_bill_3)
    new_client_2.medical_bills.append(new_medical_bill_4)
    new_casefile.clients.append(new_client_1)
    new_casefile.clients.append(new_client_2)
    new_casefile.defendants.append(new_defendant_1)
    new_casefile.defendants.append(new_defendant_2)
    new_casefile.first_party_claims.append(new_first_party_claim)
    # Commit the data
    db.session.add(new_casefile)
    db.session.commit()
