import re
import os
import base64
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from datetime import datetime
from dateutil import tz
from flask_login import UserMixin
from . import db

class Tenant(db.Model):
    """
    Model to represent each tenant (client or company) in the multi-tenant system.
    Each tenant can have multiple admins and access their own data exclusively.
    """
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    google_drive_folder_id=db.Column(db.String(255), nullable=True)

    folder_id = db.Column(db.String(255), nullable=True)
    admin_users = db.relationship("User", back_populates="tenant", cascade="all, delete-orphan")
    auto_adjusters = db.relationship("AutoAdjuster", back_populates="tenant", cascade="all, delete-orphan")
    auto_insurances = db.relationship("AutoInsurance", back_populates="tenant", cascade="all, delete-orphan")
    casefiles = db.relationship("Casefile", back_populates="tenant", cascade="all, delete-orphan")
    clients = db.relationship("Client", back_populates="tenant", cascade="all, delete-orphan")
    defendants = db.relationship("Defendant", back_populates="tenant", cascade="all, delete-orphan")
    entries = db.relationship("Entry", back_populates="tenant", cascade="all, delete-orphan")
    firstpartyclaims = db.relationship("FirstPartyClaim", back_populates="tenant", cascade="all, delete-orphan")
    healthadjusters = db.relationship("HealthAdjuster", back_populates="tenant", cascade="all, delete-orphan")
    healthclaims = db.relationship("HealthClaim", back_populates="tenant", cascade="all, delete-orphan")
    healthinsurances = db.relationship("HealthInsurance", back_populates="tenant", cascade="all, delete-orphan")
    medicalbills = db.relationship("MedicalBill", back_populates="tenant", cascade="all, delete-orphan")
    medicalproviders = db.relationship("MedicalProvider", back_populates="tenant", cascade="all, delete-orphan")
    members = db.relationship("Member", back_populates="tenant", cascade="all, delete-orphan")
    thirdpartyclaims = db.relationship("ThirdPartyClaim", back_populates="tenant", cascade="all, delete-orphan")
    reminders = db.relationship("Reminder", back_populates="tenant", cascade="all, delete-orphan")
    admins = db.relationship("Admin", back_populates="tenant", cascade="all, delete-orphan")


    def __repr__(self):
        return f"<Tenant {self.name}>"
    

class Admin(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    tenant_id = db.Column(db.Integer, db.ForeignKey('tenant.id'), nullable=True)
    is_superadmin = db.Column(db.Boolean, default=False)  
    role = db.Column(db.String(50), default='user')

    members = db.relationship("Member", back_populates="admin", cascade="all, delete-orphan")
    tenant = db.relationship("Tenant", back_populates="admins")

    def __init__(self, email, password, role='user'):  # Ensure the role is defaulted to 'user'
        self.email = email
        self.password = password
        self.role = role

class User(db.Model, UserMixin):
    """
    Admin users who manage the data for a specific tenant.
    Each admin belongs to one tenant and has access to that tenant's data.
    """
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    tenant_id = db.Column(db.Integer, db.ForeignKey("tenant.id"), nullable=False)

    tenant = db.relationship("Tenant", back_populates="admin_users")

    def __repr__(self):
        return f"<User {self.username}>"

class AutoAdjuster(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(100))
    middle_name = db.Column(db.String(100))
    last_name = db.Column(db.String(100))
    phone = db.Column(db.Text)
    fax = db.Column(db.Text)
    email = db.Column(db.Text)
    street_address = db.Column(db.Text)
    city = db.Column(db.Text)
    state = db.Column(db.Text)
    zip_code = db.Column(db.Text)
    tenant_id = db.Column(db.Integer, db.ForeignKey("tenant.id"), nullable=False)
    auto_insurance_id = db.Column(db.ForeignKey("auto_insurance.id"), nullable=False)
    
    tenant = db.relationship("Tenant", back_populates="auto_adjusters")
    employer = db.relationship("AutoInsurance", back_populates="adjusters")
    first_party_claims = db.relationship("FirstPartyClaim", back_populates="auto_adjuster")
    third_party_claims = db.relationship("ThirdPartyClaim", back_populates="auto_adjuster")

     # PYTHON CLASS PROPERTIES
    @property
    def full_name(self):
        concat = self.first_name + " " + self.middle_name + " " + self.last_name
        trimmed = concat.strip()
        return re.sub(r"\s\s+", " ", trimmed)  # Use a raw string


class AutoInsurance(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text)
    street_address = db.Column(db.Text)
    street_address_2 = db.Column(db.Text)
    city = db.Column(db.Text)
    state = db.Column(db.Text)
    zip_code = db.Column(db.Text)
    phone_1_type = db.Column(db.Text)
    phone_1 = db.Column(db.Text)
    phone_2_type = db.Column(db.Text)
    phone_2 = db.Column(db.Text)
    phone_3_type = db.Column(db.Text)
    phone_3 = db.Column(db.Text)
    fax_1_type = db.Column(db.Text)
    fax_1 = db.Column(db.Text)
    fax_2_type = db.Column(db.Text)
    fax_2 = db.Column(db.Text)
    fax_3_type = db.Column(db.Text)
    fax_3 = db.Column(db.Text)
    email_1_type = db.Column(db.Text)
    email_1 = db.Column(db.Text)
    email_2_type = db.Column(db.Text)
    email_2 = db.Column(db.Text)
    notes = db.Column(db.Text)
    tenant_id = db.Column(db.Integer, db.ForeignKey("tenant.id"), nullable=False)

    tenant = db.relationship("Tenant", back_populates="auto_insurances")
    adjusters = db.relationship("AutoAdjuster", back_populates="employer", cascade="all, delete-orphan")
    defendants = db.relationship("Defendant", back_populates="auto_insurance")
    first_party_claims = db.relationship("FirstPartyClaim", back_populates="auto_insurance", cascade="all, delete-orphan")
    third_party_claims = db.relationship("ThirdPartyClaim", back_populates="auto_insurance", cascade="all, delete-orphan")

class Casefile(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    status = db.Column(db.String(100), server_default="New")
    stage = db.Column(db.String(100), server_default="Intake")
    client_count = db.Column(db.Integer)
    defendant_count = db.Column(db.Integer)
    date_of_loss = db.Column(db.Date)
    time_of_wreck = db.Column(db.Time)
    wreck_type = db.Column(db.String(100))
    wreck_street = db.Column(db.Text)
    wreck_city = db.Column(db.Text) # Potential Enumeration
    wreck_state = db.Column(db.Text) # Potential Enumeration
    wreck_county = db.Column(db.Text) # Potential Enumeration
    wreck_description = db.Column(db.Text)
    is_police_involved = db.Column(db.String(5))
    police_force = db.Column(db.Text) # Potential Enumeration
    is_police_report = db.Column(db.String(5))
    police_report_number = db.Column(db.Text)
    vehicle_description = db.Column(db.Text)
    damage_level = db.Column(db.Text) # ENUMERATION
    wreck_notes = db.Column(db.Text)
    # GOOGLE INTEGRATION FIELDS
    main_folder_id = db.Column(db.Text)
    client_documentation_folder_id = db.Column(db.Text)
    subrogation_folder_id = db.Column(db.Text)
    medical_records_folder_id = db.Column(db.Text)
    first_party_folder_id = db.Column(db.Text)
    third_party_folder_id = db.Column(db.Text)
    checks_folder_id = db.Column(db.Text)
    litigation_folder_id = db.Column(db.Text)
    lost_wages_folder_id = db.Column(db.Text)
    pics_and_video_folder_id = db.Column(db.Text)
    property_damage_folder_id = db.Column(db.Text)
    tenant_id = db.Column(db.Integer, db.ForeignKey("tenant.id"), nullable=False)
    closed = db.Column(db.Boolean, default=False)
    tenant = db.relationship("Tenant", back_populates="casefiles")
    clients = db.relationship("Client", back_populates="casefile", cascade="all, delete-orphan")
    defendants = db.relationship("Defendant", back_populates="casefile", cascade="all, delete-orphan")
    entries = db.relationship("Entry", back_populates="casefile", cascade="all, delete-orphan")
    first_party_claims = db.relationship("FirstPartyClaim", back_populates="casefile", cascade="all, delete-orphan")

    # PYTHON CLASS PROPERTIES
    @property
    def client_list(self):
        lst = []
        for client in self.clients:
            lst.append(client.full_name)
        return ", ".join(lst)
    
    @property
    def case_label(self):
        # Get List of Last Names
        lst = []
        dol = datetime.strftime(self.date_of_loss, "%m/%d/%y") 
        clients = Client.query.filter(Client.casefile_id == self.id).order_by(Client.last_name).distinct(Client.last_name).all()
        for client in clients:
            lst.append(client.last_name)
        # Join Last Names Into String
        return "-".join(lst) + f" {dol}"
    
    @property
    def new_case_label(self):
        lst = []
        outside_last_names = []
        unique_clients = Client.query.filter(Client.casefile_id ==self.id).distinct(Client.last_name).all()
        non_clients = Client.query.filter(Client.casefile_id != self.id).distinct(Client.last_name).all()
        # Get Driver Last Name
        for client in self.clients:
            if client.is_driver == "True":
                driver = client
        # Are there more clients?
        # No, just one
        if len(self.clients) == 1:
            return driver.last_name + ", " + driver.first_name
        # Yes many clients
        else:
            # Get all unique client last names that aren't the driver
            for unique_client in unique_clients:
                if unique_client.last_name != driver.last_name:
                    lst.append(unique_client.last_name)
            # Are There any?
            if len(lst) == 0:
            # no
            # is driver last name included in any other cases?
                for non_client in non_clients:
                    outside_last_names.append(non_client.last_name)
                if driver.last_name in outside_last_names:
                    # yes
                    # add last_name, first_name
                    return driver.last_name + ", " + driver.first_name
                else:
                    # no, add driver last name
                    return driver.last_name
            else:
            # yes
            # is driver last name included in any other cases?
                for non_client in non_clients:
                    outside_last_names.append(non_client.last_name)
                if driver.last_name in outside_last_names:
                    # add driver first and last name to new list 
                    new_lst=[f"{driver.last_name}, {driver.first_name}"]
                    print (new_lst)
                    # yes
                    # are other names in outside last names?
                    for item in lst:
                        if item in outside_last_names:
                        # NEED TO ADD FIRST NAME HERE
                           new_lst.append(f"{item}, {unique_clients[lst.index(item)].first_name}")
                           continue
                        else:
                            new_lst.append(item)
                    return " / ".join(new_lst)
                else:
                    # no, add driver last name and other last names
                    for item in lst:
                        return driver.last_name + " / " + item

class Client(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    casefile_id = db.Column(db.Integer, db.ForeignKey("casefile.id"), nullable=True)
    tenant_id = db.Column(db.Integer, db.ForeignKey("tenant.id"), nullable=False)
    client_number = db.Column(db.Integer)
    first_name = db.Column(db.String(100))
    middle_name = db.Column(db.String(100))
    last_name = db.Column(db.String(100))
    dob = db.Column(db.Date)
    physical_identifier = db.Column(db.LargeBinary)
    nacl = db.Column(db.LargeBinary)
    marital_status = db.Column(db.String(50))
    street_address = db.Column(db.Text)
    city = db.Column(db.Text)
    state = db.Column(db.Text)
    zip_code = db.Column(db.Text)
    primary_phone = db.Column(db.String(13)) # Potential TABLE
    secondary_phone = db.Column(db.String(13)) # Potential TABLE
    email = db.Column(db.String(100)) # Potential TABLE
    referrer = db.Column(db.Text)
    referrer_relationship = db.Column(db.Text)
    notes = db.Column(db.Text)
    injuries = db.Column(db.Text)
    rode_ambulance = db.Column(db.String(5))
    visited_hospital = db.Column(db.String(5))
    has_hi = db.Column(db.String(5))
    had_prior_injury = db.Column(db.String(5))
    prior_injury_notes = db.Column(db.Text)
    had_prior_accident = db.Column(db.String(5))
    prior_accident_notes = db.Column(db.Text)
    was_work_impacted = db.Column(db.String(5))
    work_impacted_notes = db.Column(db.Text)
    is_driver = db.Column(db.String(5))

    tenant = db.relationship("Tenant", back_populates="clients")
    casefile = db.relationship("Casefile", back_populates="clients")
    medical_bills = db.relationship("MedicalBill", back_populates="client", cascade="all, delete-orphan")
    health_claims = db.relationship("HealthClaim", back_populates="client", cascade="all, delete-orphan")

    # PYTHON CLASS PROPERTIES
    @property
    def full_name(self):
        concat = self.first_name + " " + self.middle_name + " " + self.last_name
        trimmed = concat.strip()
        return re.sub(r"\s\s+", " ", trimmed)  # Use a raw string


    @property
    def medical_provider_list(self):
        lst = []
        for bill in self.medical_bills:
            lst.append(bill.medical_provider.name)
        return ', '.join(lst)
    
    # @property
    # def ssn(self):
    #     if self.physical_identifier:
    #         crystal_key = os.environ.get("CRYSTAL_KEY").encode()
    #         nacl = self.nacl
    #         kdf = PBKDF2HMAC(
    #             algorithm=hashes.SHA256(),
    #             length=32,
    #             salt=nacl,
    #             iterations=480000
    #         )
    #         f_key = base64.urlsafe_b64encode(kdf.derive(crystal_key))
    #         f = Fernet(f_key)
    #         f_token = f.decrypt(self.physical_identifier)
    #         return f_token.decode()
    #     else:
    #         return None
    @property
    def ssn(self):
      if self.physical_identifier:
        crystal_key = os.environ.get("CRYSTAL_KEY").encode()  # Ensure CRYSTAL_KEY is bytes
        nacl = self.nacl

        # **Improved type handling for nacl**
        if nacl is None:
            # raise ValueError("nacl is None. Please ensure it is set correctly.")
            return None
        elif isinstance(nacl, str):
            nacl = nacl.encode("utf-8")  # Convert string to bytes
        elif not isinstance(nacl, bytes):
            raise TypeError("nacl must be a string or bytes")  # Error for invalid type

        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=nacl,  # nacl is guaranteed to be bytes
            iterations=480000
        )

        f_key = base64.urlsafe_b64encode(kdf.derive(crystal_key))
        f = Fernet(f_key)
        f_token = f.decrypt(self.physical_identifier)
        return f_token.decode()
      else:
        return None




class Defendant(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    casefile_id = db.Column(db.Integer, db.ForeignKey("casefile.id"), nullable=False)
    tenant_id = db.Column(db.Integer, db.ForeignKey("tenant.id"), nullable=False)
    defendant_number = db.Column(db.Integer)
    liability = db.Column(db.Text)
    first_name = db.Column(db.String(100))
    last_name = db.Column(db.String(100))
    is_policyholder = db.Column(db.String(5))
    policyholder_first_name = db.Column(db.String(100))
    policyholder_last_name = db.Column(db.String(100))
    rode_ambulance = db.Column(db.String(5))
    auto_insurance_id = db.Column(db.ForeignKey("auto_insurance.id"))
    policy_number = db.Column(db.Text)
    notes = db.Column(db.Text)

    tenant = db.relationship("Tenant", back_populates="defendants")
    auto_insurance = db.relationship("AutoInsurance", back_populates="defendants")
    casefile = db.relationship("Casefile", back_populates="defendants")
    auto_claim = db.relationship("ThirdPartyClaim", back_populates="defendant", cascade="all, delete-orphan", uselist=False)

    # PYTHON CLASS PROPERTIES
    @property
    def full_name(self):
        concat = self.first_name + " " + self.last_name
        trimmed = concat.strip()
        return re.sub(r"\s\s+", " ", trimmed)  # Use a raw string


class Entry(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    casefile_id = db.Column(db.Integer, db.ForeignKey("casefile.id"), nullable=False)
    tenant_id = db.Column(db.Integer, db.ForeignKey("tenant.id"), nullable=False)
    member_id = db.Column(db.Text, db.ForeignKey("member.id"))
    description = db.Column(db.Text)
    utc_timestamp = db.Column(db.DateTime)

    tenant = db.relationship("Tenant", back_populates="entries")
    casefile = db.relationship("Casefile", back_populates="entries")
    member = db.relationship("Member", back_populates="entries")

    def local_datetime(self):
        to_zone = tz.tzlocal()
        return self.utc_timestamp.astimezone(to_zone)
    
    def central_datetime(self):
        to_zone = tz.gettz('America/Chicago')
        return self.utc_timestamp.astimezone(to_zone)

class FirstPartyClaim(db.Model):
    casefile_id = db.Column(db.ForeignKey("casefile.id"), primary_key=True)
    tenant_id = db.Column(db.Integer, db.ForeignKey("tenant.id"), nullable=False)
    auto_insurance_id = db.Column(db.ForeignKey("auto_insurance.id"), primary_key=True)
    auto_adjuster_id = db.Column(db.ForeignKey("auto_adjuster.id"))
    claim_number = db.Column(db.Text)
    is_started = db.Column(db.String(5))
    is_statement = db.Column(db.String(5))
    policy_number = db.Column(db.Text)
    has_medpay = db.Column(db.String(5))
    medpay_amount = db.Column(db.Integer)
    has_um_coverage = db.Column(db.String(5))
    um_amount = db.Column(db.Text) # GIVEN AS A RATIO NOT INTEGER
    is_lor_sent = db.Column(db.String(5))
    is_loa_received = db.Column(db.String(5))
    is_dec_sheets_received = db.Column(db.String(5))
    last_request_date = db.Column(db.Date)
    notes = db.Column(db.Text)
    
    tenant = db.relationship("Tenant", back_populates="firstpartyclaims")
    auto_insurance = db.relationship("AutoInsurance", back_populates="first_party_claims")
    auto_adjuster = db.relationship("AutoAdjuster", back_populates="first_party_claims")
    casefile = db.relationship("Casefile", back_populates="first_party_claims")

class HealthAdjuster(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    tenant_id = db.Column(db.Integer, db.ForeignKey("tenant.id"), nullable=False)
    first_name = db.Column(db.String(100))
    middle_name = db.Column(db.String(100))
    last_name = db.Column(db.String(100))
    phone = db.Column(db.Text)
    fax = db.Column(db.Text)
    email = db.Column(db.Text)
    health_insurance_id = db.Column(db.ForeignKey("health_insurance.id"))
    
    tenant = db.relationship("Tenant", back_populates="healthadjusters")
    health_insurance = db.relationship("HealthInsurance", back_populates="adjusters")
    claims = db.relationship("HealthClaim", back_populates="adjuster")

     # PYTHON CLASS PROPERTIES
    @property
    def full_name(self):
        concat = self.first_name + " " + self.middle_name + " " + self.last_name
        trimmed = concat.strip()
        return re.sub(r"\s\s+", " ", trimmed)  # Use a raw string


class HealthClaim(db.Model):
    client_id = db.Column(db.ForeignKey("client.id"), primary_key=True)
    health_insurance_id = db.Column(db.ForeignKey("health_insurance.id"), primary_key=True)
    tenant_id = db.Column(db.Integer, db.ForeignKey("tenant.id"), nullable=False)
    member_id = db.Column(db.Text)
    health_adjuster_id = db.Column(db.ForeignKey("health_adjuster.id"))
    event_number = db.Column(db.Text)
    is_hipaa_sent = db.Column(db.String(5), server_default="False")
    is_lor_sent = db.Column(db.String(5), server_default="False")
    is_log_received = db.Column(db.String(5), server_default="False")
    total_due = db.Column(db.Float)
    last_request_date = db.Column(db.Date)
    notes = db.Column(db.Text)

    tenant = db.relationship("Tenant", back_populates="healthclaims")
    client = db.relationship("Client", back_populates="health_claims")
    adjuster = db.relationship("HealthAdjuster", back_populates="claims")
    health_insurance = db.relationship("HealthInsurance", back_populates="claims")

class HealthInsurance(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    tenant_id = db.Column(db.Integer, db.ForeignKey("tenant.id"), nullable=False)
    name = db.Column(db.Text)
    street_address = db.Column(db.Text)
    street_address_2 = db.Column(db.Text)
    city = db.Column(db.Text)
    state = db.Column(db.Text)
    zip_code = db.Column(db.Text)
    phone_1_type = db.Column(db.Text)
    phone_1 = db.Column(db.Text)
    phone_2_type = db.Column(db.Text)
    phone_2 = db.Column(db.Text)
    phone_3_type = db.Column(db.Text)
    phone_3 = db.Column(db.Text)
    fax_1_type = db.Column(db.Text)
    fax_1 = db.Column(db.Text)
    fax_2_type = db.Column(db.Text)
    fax_2 = db.Column(db.Text)
    fax_3_type = db.Column(db.Text)
    fax_3 = db.Column(db.Text)
    email_1_type = db.Column(db.Text)
    email_1 = db.Column(db.Text)
    email_2_type = db.Column(db.Text)
    email_2 = db.Column(db.Text)
    notes = db.Column(db.Text)
    
    tenant = db.relationship("Tenant", back_populates="healthinsurances")
    adjusters = db.relationship("HealthAdjuster", back_populates="health_insurance")
    claims = db.relationship("HealthClaim", back_populates="health_insurance")

class MedicalBill(UserMixin, db.Model):
    client_id = db.Column(db.ForeignKey("client.id"), primary_key=True)
    medical_provider_id = db.Column(db.ForeignKey("medical_provider.id"), primary_key=True)
    tenant_id = db.Column(db.Integer, db.ForeignKey("tenant.id"), nullable=False)
    is_hipaa_sent = db.Column(db.String(5), server_default="False")
    is_bill_received = db.Column(db.String(5), server_default="False")
    is_record_received = db.Column(db.String(5), server_default="False")
    total_billed = db.Column(db.Float)
    insurance_paid = db.Column(db.Float)
    insurance_adjusted = db.Column(db.Float)
    mp_paid = db.Column(db.Float)
    patient_paid = db.Column(db.Float)
    reduction_amount = db.Column(db.Float)
    is_lien_filed = db.Column(db.String(5))
    is_in_collections = db.Column(db.String(5))
    last_request_date = db.Column(db.Date)
    expense = db.Column(db.Float)
    total_due = db.Column(db.Float)
    
    tenant = db.relationship("Tenant", back_populates="medicalbills")
    client = db.relationship("Client", back_populates="medical_bills")
    medical_provider = db.relationship("MedicalProvider", back_populates="medical_bills")

    # Python Properties
    @property
    def total_due(self):
        try:
            x = self.total_billed
            try:
                x = x - self.insurance_paid
            except:
                print("Couldn't subtract insurance paid")

            try:
                x = x - self.insurance_adjusted
            except:
                print("Couldn't subtract insurace adjusted")
            
            try:
                x = x - self.mp_paid
            except:
                print("Couldn't subtract MP paid")
            
            try:
                x = x - self.patient_paid
            except:
                print("Couldn't subtract patient paid")

            try:
                x = x - self.reduction_amount
            except:
                print("Couldn't subtract reduction amount")
                
        except:
            x = None
        if x:
            return round(x,2)
    # def calculate_total_due(self):
    #     try:
    #         x = self.total_billed
    #         try:
    #             x = x - self.insurance_paid
    #         except:
    #             print("Couldn't subtract insurance paid")

    #         try:
    #             x = x - self.insurance_adjusted
    #         except:
    #             print("Couldn't subtract insurance adjusted")
            
    #         try:
    #             x = x - self.mp_paid
    #         except:
    #             print("Couldn't subtract MP paid")
            
    #         try:
    #             x = x - self.patient_paid
    #         except:
    #             print("Couldn't subtract patient paid")

    #         try:
    #             x = x - self.reduction_amount
    #         except:
    #             print("Couldn't subtract reduction amount")
                
    #     except:
    #         x = None
    #     if x:
    #         return round(x, 2)

class MedicalProvider(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    tenant_id = db.Column(db.Integer, db.ForeignKey("tenant.id"), nullable=False)
    name = db.Column(db.Text)
    street_address = db.Column(db.Text)
    street_address_2 = db.Column(db.Text)
    city = db.Column(db.Text)
    state = db.Column(db.Text)
    zip_code = db.Column(db.Text)
    phone_1_type = db.Column(db.Text)
    phone_1 = db.Column(db.Text)
    phone_2_type = db.Column(db.Text)
    phone_2 = db.Column(db.Text)
    phone_3_type = db.Column(db.Text)
    phone_3 = db.Column(db.Text)
    fax_1_type = db.Column(db.Text)
    fax_1 = db.Column(db.Text)
    fax_2_type = db.Column(db.Text)
    fax_2 = db.Column(db.Text)
    fax_3_type = db.Column(db.Text)
    fax_3 = db.Column(db.Text)
    email_1_type = db.Column(db.Text)
    email_1 = db.Column(db.Text)
    email_2_type = db.Column(db.Text)
    email_2 = db.Column(db.Text)
    hipaa_method = db.Column(db.Text)
    notes = db.Column(db.Text)
    
    tenant = db.relationship("Tenant", back_populates="medicalproviders")
    medical_bills = db.relationship("MedicalBill", back_populates="medical_provider", cascade="all, delete-orphan")

class Member(UserMixin, db.Model):
    id = db.Column(db.Text, primary_key=True )
    # secret = db.Column(db.String(255), unique=True, nullable=False)
    tenant_id = db.Column(db.Integer, db.ForeignKey("tenant.id"), nullable=False)
    # tenant_name = db.Column(db.String, nullable=False)
    admin_id = db.Column(db.Integer, db.ForeignKey("admin.id"), nullable=True)
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))
    is_admin = db.Column(db.Boolean)
    name = db.Column(db.String(1000))
    access_token = db.Column(db.Text)
    refresh_token = db.Column(db.Text)
    token_expiration = db.Column(db.DateTime)
    role = db.Column(db.String(50), default='user')
    
    admin = db.relationship("Admin", back_populates="members")
    tenant = db.relationship("Tenant", back_populates="members")
    entries = db.relationship("Entry", back_populates="member")

class ThirdPartyClaim(db.Model):
    defendant_id = db.Column(db.ForeignKey("defendant.id"), primary_key=True)
    tenant_id = db.Column(db.Integer, db.ForeignKey("tenant.id"), nullable=False)
    auto_insurance_id = db.Column(db.ForeignKey("auto_insurance.id"), primary_key=True)
    auto_adjuster_id = db.Column(db.ForeignKey("auto_adjuster.id"))
    claim_number = db.Column(db.Text)
    is_started = db.Column(db.String(5))
    is_statement = db.Column(db.String(5))
    is_lor_sent = db.Column(db.String(5))
    is_loa_received = db.Column(db.String(5))
    last_request_date = db.Column(db.Date)
    notes = db.Column(db.Text)

    tenant = db.relationship("Tenant", back_populates="thirdpartyclaims")
    auto_insurance = db.relationship("AutoInsurance", back_populates="third_party_claims")
    auto_adjuster = db.relationship("AutoAdjuster", back_populates="third_party_claims")
    defendant = db.relationship("Defendant", back_populates="auto_claim")

class Reminder(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    tenant_id = db.Column(db.Integer, db.ForeignKey('tenant.id'), nullable=False)  # Foreign key to Tenant table
    casefile_id = db.Column(db.Integer, db.ForeignKey('casefile.id'), nullable=True)
    reminder_type = db.Column(db.String(50), nullable=False)
    client_id = db.Column(db.Integer, db.ForeignKey('client.id'), nullable=True)
    method = db.Column(db.String(10), nullable=False)  # "email" or "notification"
    message = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    tenant = db.relationship("Tenant", back_populates="reminders")


class CalendarEvent(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    tenant_id = db.Column(db.Integer, nullable=False)
    casefile_id = db.Column(db.Integer, db.ForeignKey('casefile.id'), nullable=False)
    client_id = db.Column(db.Integer, db.ForeignKey('client.id'), nullable=False)
    event_name = db.Column(db.String(200), nullable=False)
    start_datetime = db.Column(db.DateTime, nullable=False)
    end_datetime = db.Column(db.DateTime, nullable=False)
    description = db.Column(db.String(500))
    event_type = db.Column(db.String(50))  # e.g., 'appointment', 'deadline', etc.
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    casefile = db.relationship('Casefile', backref='events')
    client = db.relationship('Client', backref='events')

    def __repr__(self):
        return f'<CalendarEvent {self.event_name} for {self.client.full_name}>'
