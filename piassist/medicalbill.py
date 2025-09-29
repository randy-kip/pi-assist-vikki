from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify,session,abort
from flask_login import login_required
from datetime import datetime
from sqlalchemy import cast, Numeric
from sqlalchemy import func
from piassist.models import MedicalBill, MedicalProvider, Client,Tenant
from . import db

medicalbill = Blueprint('medicalbill', __name__)

def validate_tenant(tenant_name):
    tenant = Tenant.query.filter_by(name=tenant_name).first()
    if tenant:
        session['tenant_id'] = tenant.id
        session['tenant_name'] = tenant.name
    else:
        flash("Invalid tenant specified in URL.", "is-warning")
        abort(404, description=f"Invalid tenant: '{tenant_name}'")
# def calculate_totals(client_id, medical_provider_id):
#     # Initialize total values
#     totals = {
#         'insurance_paid': 0,
#         'mp_paid': 0,
#         'patient_paid': 0,
#         'reduction_amount': 0,
#         'total_billed': 0,
#         'insurance_adjusted': 0,
#         'expense': 0,
#         'total_due': 0

#     }

#     # Fetch all bills for the provider
#     medical_bills = MedicalBill.query.filter_by(client_id=client_id, medical_provider_id=medical_provider_id).all()

#     for bill in medical_bills:
#     #     totals['insurance_paid'] += bill.insurance_paid or 0
#     #     totals['mp_paid'] += bill.mp_paid or 0
#     #     totals['patient_paid'] += bill.patient_paid or 0
#     #     totals['reduction_amount'] += bill.reduction_amount or 0
#     #     totals['total_billed'] += bill.total_billed or 0
#     #     totals['insurance_adjusted'] += bill.insurance_adjusted or 0
#     #     totals['expense'] += bill.expense or 0
#     #     # total_due = bill.total_billed - (bill.insurance_paid + bill.insurance_adjusted + bill.patient_paid)
#     #     totals['total_due'] += bill.total_due or 0
#      totals['insurance_paid'] += float(bill.insurance_paid() or 0) if callable(bill.insurance_paid) else float(bill.insurance_paid or 0)
#     totals['mp_paid'] += float(bill.mp_paid() or 0) if callable(bill.mp_paid) else float(bill.mp_paid or 0)
#     totals['patient_paid'] += float(bill.patient_paid() or 0) if callable(bill.patient_paid) else float(bill.patient_paid or 0)
#     totals['reduction_amount'] += float(bill.reduction_amount() or 0) if callable(bill.reduction_amount) else float(bill.reduction_amount or 0)
#     totals['total_billed'] += float(bill.total_billed() or 0) if callable(bill.total_billed) else float(bill.total_billed or 0)
#     totals['insurance_adjusted'] += float(bill.insurance_adjusted() or 0) if callable(bill.insurance_adjusted) else float(bill.insurance_adjusted or 0)
#     totals['expense'] += float(bill.expense() or 0) if callable(bill.expense) else float(bill.expense or 0)
#     # Safely handle both callable and non-callable `total_due`, ensuring it's not `None`
#     totals['total_due'] += bill.total_due or 0








#     return totals



@medicalbill.route('/<tenant_name>/medicalbills')
def index(tenant_name):
    medicalbills = MedicalBill.query.join(MedicalProvider).filter_by(tenant_id=session['tenant_id']).order_by(MedicalProvider.name).all()

    return render_template('medicalbill/medicalbill-index.html', medicalbills=medicalbills, tenant_name=tenant_name)

# Medical Bill Detail Route
@medicalbill.route('/<tenant_name>/medicalbill/client/<int:client_id>/medicalprovider/<int:medical_provider_id>', methods=['GET', 'POST'])
@login_required
def details(tenant_name, client_id, medical_provider_id):
    validate_tenant(tenant_name)
    # medical_bill = db.get_or_404(MedicalBill, (client_id, medical_provider_id))
    medical_bill = MedicalBill.query.filter_by(client_id=client_id,medical_provider_id=medical_provider_id, tenant_id=session['tenant_id']).first_or_404()
    # Fetch all bills for the client and provider
    # medical_bills = MedicalBill.query.filter_by(client_id=client_id, medical_provider_id=medical_provider_id).all()
    medical_bills = MedicalBill.query.filter_by(client_id=client_id,medical_provider_id=medical_provider_id, tenant_id=session['tenant_id']).all()
    

    # Calculate totals for each category
    total_insurance_paid = db.session.query(func.sum(MedicalBill.insurance_paid)).filter_by(client_id=client_id, medical_provider_id=medical_provider_id).scalar() or 0
    total_mp_paid = db.session.query(func.sum(MedicalBill.mp_paid)).filter_by(client_id=client_id, medical_provider_id=medical_provider_id).scalar() or 0
    total_patient_paid = db.session.query(func.sum(MedicalBill.patient_paid)).filter_by(client_id=client_id, medical_provider_id=medical_provider_id).scalar() or 0
    total_reduction = db.session.query(func.sum(MedicalBill.reduction_amount)).filter_by(client_id=client_id, medical_provider_id=medical_provider_id).scalar() or 0

    if request.method == 'POST':
        medical_bill.is_hipaa_sent = request.form.get("is_hipaa_sent")
        medical_bill.is_bill_received = request.form.get("is_bill_received")
        medical_bill.is_record_received = request.form.get("is_record_received")

        # Process float fields with error handling
        float_fields = [
            'total_billed', 'insurance_paid', 'insurance_adjusted',
            'mp_paid', 'patient_paid', 'reduction_amount', 'expense'
        ]
        
        for field in float_fields:
            try:
                setattr(medical_bill, field, float(request.form.get(field, 0)))
            except ValueError:
                print(f"Couldn't convert {field}")

        # Process last request date
        try:
            medical_bill.last_request_date = datetime.strptime(request.form.get("last_request_date"), '%Y-%m-%d').date()
        except ValueError:
            print("Last request date couldn't be saved for updated casefile.")
        
        # Additional fields
        medical_bill.is_lien_filed = request.form.get("is_lien_filed")
        medical_bill.is_in_collections = request.form.get("is_in_collections")

        db.session.commit()
        flash("Successfully Updated Medical Bill", "is-success")
        return redirect(url_for('casefile.details',casefile_id=medical_bill.client.casefile_id, tenant_name=tenant_name))

    return render_template('medicalbill/medical-bill-detail.html', 
                           medical_bill=medical_bill,  # This is a single instance
                           medical_bills=medical_bills,
                           client_id=client_id,
                           medical_provider_id=medical_provider_id,
                           tenant_name=tenant_name,
                           total_insurance_paid=total_insurance_paid,
                           total_mp_paid=total_mp_paid,
                           total_patient_paid=total_patient_paid,
                           total_reduction=total_reduction)

# Send Fax Route
@medicalbill.route('/sendfax/<int:medical_bill_id>', methods=['POST'])
def send_fax(medical_bill_id):
    medical_bill = MedicalBill.query.get_or_404(medical_bill_id)
    fax_number = medical_bill.provider.fax_number
    file_path = 'path/to/bill/document.pdf'  # Generate or locate the PDF file

    # Assuming a send_fax function exists
    response = send_fax(file_path, fax_number)

    if response.successful:
        flash('Fax sent successfully!', 'is-success')
    else:
        flash('Failed to send fax.', 'is-danger')

    return redirect(url_for('medicalbill.details', client_id=medical_bill.client_id, medical_provider_id=medical_bill.medical_provider_id))

# Calendar Events Route
@medicalbill.route('/calendar/events')
@login_required
def get_events():
    events = []
    medical_bills = MedicalBill.query.all()
    for bill in medical_bills:
        events.append({
            'title': f'Medical Bill for {bill.provider.name}',
            'start': bill.last_request_date.isoformat()  # Event date
        })
    return jsonify(events)

# Medical Bill Input Route
@medicalbill.route('/<tenant_name>/new/medicalbill/casefile/<int:casefile_id>', methods=['GET', 'POST'])
@login_required
def input(tenant_name,casefile_id):
    validate_tenant(tenant_name)
    # medical_providers = MedicalProvider.query.order_by(MedicalProvider.name).all()
    medical_providers = MedicalProvider.query.filter_by(tenant_id=session['tenant_id']).order_by(MedicalProvider.name).all()
    # clients = Client.query.filter(Client.casefile_id == casefile_id).all()
    clients = Client.query.filter_by(casefile_id=casefile_id, tenant_id=session['tenant_id']).all()
    
    if request.method == 'POST':
        client_id = request.form.get("client_id")
        medical_provider_id = request.form.get("medical_provider_id")
        is_bill_received = request.form.get("is_bill_received")
        is_record_received = request.form.get("is_record_received")
        is_lien_filed = request.form.get("is_lien_filed")
        is_in_collections = request.form.get("is_in_collections")
        
        # Process float fields
        float_fields = [
            'total_billed', 'insurance_paid', 'insurance_adjusted',
            'mp_paid', 'patient_paid', 'reduction_amount', 'expense'
        ]
        values = {}
        
        for field in float_fields:
            try:
                values[field] = float(request.form.get(field, 0))
            except ValueError:
                print(f"Couldn't Convert {field}")
                values[field] = None

        # Process last request date
        try:
            last_request_date = datetime.strptime(request.form.get("last_request_date"), '%Y-%m-%d').date()
        except ValueError:
            print("Last request date couldn't be saved for updated casefile.")
            last_request_date = None
        
        # Create new MedicalBill instance
        try:
            new_medical_bill = MedicalBill(
                client_id=int(client_id),
                medical_provider_id=int(medical_provider_id),
                is_bill_received=is_bill_received,
                is_record_received=is_record_received,
                is_lien_filed=is_lien_filed,
                is_in_collections=is_in_collections,
                total_billed=values['total_billed'],
                insurance_paid=values['insurance_paid'],
                insurance_adjusted=values['insurance_adjusted'],
                mp_paid=values['mp_paid'],
                patient_paid=values['patient_paid'],
                reduction_amount=values['reduction_amount'],
                last_request_date=last_request_date,
                expense=values['expense'],
                tenant_id=session['tenant_id']
            )
            db.session.add(new_medical_bill)
            db.session.commit()
            flash("Created New Medical Bill successfully!", "is-success")
        except Exception as e:
            db.session.rollback()
            print(f"Error creating new medical bill: {e}")
            flash("Error creating new medical bill, make sure you're associating the bill with both a client and medical provider.", "is-danger")
        
        return redirect(url_for('casefile.details',casefile_id=casefile_id,tenant_name=tenant_name,))

    return render_template('medicalbill/medical-bill-input.html',tenant_name=tenant_name, medical_providers=medical_providers, clients=clients)

# DELETE MEDICAL BILL ROUTE
@medicalbill.route('/<tenant_name>/delete/medicalbill/client/<int:client_id>/medicalprovider/<int:medical_provider_id>')
@login_required
def delete(tenant_name,client_id, medical_provider_id):
    validate_tenant(tenant_name)
    # medicalbill = db.get_or_404(MedicalBill, (client_id, medical_provider_id))
    medicalbill = MedicalBill.query.filter_by(client_id=client_id,medical_provider_id=medical_provider_id, tenant_id=session['tenant_id']).first_or_404()
    casefile_id = medicalbill.client.casefile_id
    try:
        db.session.delete(medicalbill)
        db.session.commit()
        flash("Medical Bill Deleted Successfully", "is-success")
    except Exception as e:
        db.session.rollback()
        print(f"Error deleting medical bill: {e}")
        flash('Something went wrong', 'is-danger')
    return redirect(url_for('casefile.details',tenant_name=tenant_name, casefile_id=casefile_id))


# Route to calculate and display totals for each provider by category
# Route to calculate and display totals for each provider by category (without client-level details)
@medicalbill.route('/<tenant_name>/medicalbill/totals', methods=['GET'])
@login_required
def medical_totals(tenant_name):
    validate_tenant(tenant_name)
    
    # Aggregate totals for each provider without client-level details
    provider_totals = db.session.query(
        MedicalProvider.name.label('provider_name'),
        func.sum(MedicalBill.insurance_paid).label('total_insurance_paid'),
        func.sum(MedicalBill.mp_paid).label('total_mp_paid'),
        func.sum(MedicalBill.patient_paid).label('total_patient_paid'),
        func.sum(MedicalBill.reduction_amount).label('total_reduction_amount'),
        func.sum(MedicalBill.total_billed).label('total_billed'),
        func.sum(MedicalBill.insurance_adjusted).label('insurance_adjusted'),
        func.sum(MedicalBill.expense).label('total_expense'),
        # func.sum(MedicalBill.total_due).label('total_due')
        (db.func.sum(MedicalBill.total_billed) - db.func.sum(MedicalBill.insurance_paid) -
     db.func.sum(MedicalBill.insurance_adjusted) - db.func.sum(MedicalBill.mp_paid) -
     db.func.sum(MedicalBill.patient_paid) - db.func.sum(MedicalBill.reduction_amount)).label('total_due')
    ).join(MedicalProvider).filter(MedicalProvider.tenant_id == session['tenant_id']).group_by(MedicalProvider.name).all()
    grand_totals = {
    'total_insurance_paid': sum(total.total_insurance_paid or 0 for total in provider_totals),
    'total_mp_paid': sum(total.total_mp_paid or 0 for total in provider_totals),
    'total_patient_paid': sum(total.total_patient_paid or 0 for total in provider_totals),
    'total_reduction_amount': sum(total.total_reduction_amount or 0 for total in provider_totals),
    'total_billed': sum(total.total_billed or 0 for total in provider_totals),
    'insurance_adjusted': sum(total.insurance_adjusted or 0 for total in provider_totals),
    'total_due': sum(total.total_due or 0 for total in provider_totals),
    'total_expense': sum(total.total_expense or 0 for total in provider_totals),
}

    return render_template(
        'medicalbill/medical-bill-totals.html',
         provider_totals=provider_totals,
         grand_totals=grand_totals,
        tenant_name=tenant_name
    )




# from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
# from flask_login import login_required
# from datetime import datetime
# from sqlalchemy import func
# from piassist.models import MedicalBill, MedicalProvider, Client
# from . import db

# medicalbill = Blueprint('medicalbill', __name__)

# # Function to calculate totals for each provider
# def calculate_totals(client_id, medical_provider_id):
#     # Initialize total values
#     totals = {
#         'insurance_paid': 0,
#         'mp_paid': 0,
#         'patient_paid': 0,
#         'reduction_amount': 0,
#     }

#     # Fetch all bills for the provider
#     medical_bills = MedicalBill.query.filter_by(client_id=client_id, medical_provider_id=medical_provider_id).all()

#     for bill in medical_bills:
#         totals['insurance_paid'] += bill.insurance_paid or 0
#         totals['mp_paid'] += bill.mp_paid or 0
#         totals['patient_paid'] += bill.patient_paid or 0
#         totals['reduction_amount'] += bill.reduction_amount or 0

#     return totals

# # Medical Bill Detail Route
# @medicalbill.route('/medicalbill/client/<int:client_id>/medicalprovider/<int:medical_provider_id>', methods=['GET', 'POST'])
# @login_required
# def details(client_id, medical_provider_id):
#     medical_bill = db.get_or_404(MedicalBill, (client_id, medical_provider_id))

#     # Fetch all bills for the client and provider
#     medical_bill = MedicalBill.query.filter_by(client_id=client_id, medical_provider_id=medical_provider_id).all()

#     # Calculate totals for each category
#     totals = calculate_totals(client_id, medical_provider_id)

#     if request.method == 'POST':
#         medical_bill.is_hipaa_sent = request.form.get("is_hipaa_sent")
#         medical_bill.is_bill_received = request.form.get("is_bill_received")
#         medical_bill.is_record_received = request.form.get("is_record_received")

#         # Process float fields with error handling
#         float_fields = [
#             'total_billed', 'insurance_paid', 'insurance_adjusted',
#             'mp_paid', 'patient_paid', 'reduction_amount', 'expense'
#         ]
        
#         for field in float_fields:
#             try:
#                 setattr(medical_bill, field, float(request.form.get(field, 0)))
#             except ValueError:
#                 print(f"Couldn't convert {field}")

#         # Process last request date
#         try:
#             medical_bill.last_request_date = datetime.strptime(request.form.get("last_request_date"), '%Y-%m-%d').date()
#         except ValueError:
#             print("Last request date couldn't be saved for updated casefile.")
        
#         # Additional fields
#         medical_bill.is_lien_filed = request.form.get("is_lien_filed")
#         medical_bill.is_in_collections = request.form.get("is_in_collections")

#         db.session.commit()
#         flash("Successfully Updated Medical Bill", "is-success")
#         return redirect(url_for('casefile.details', casefile_id=medical_bill.client.casefile_id))

#     return render_template('medicalbill/medical-bill-detail.html', 
#                            medical_bill=medical_bill,
#                            totals=totals)  # Pass totals to the template

# # Send Fax Route
# @medicalbill.route('/sendfax/<int:medical_bill_id>', methods=['POST'])
# def send_fax(medical_bill_id):
#     medical_bill = MedicalBill.query.get_or_404(medical_bill_id)
#     fax_number = medical_bill.provider.fax_number
#     file_path = 'path/to/bill/document.pdf'  # Generate or locate the PDF file

#     # Assuming a send_fax function exists
#     response = send_fax(file_path, fax_number)

#     if response.successful:
#         flash('Fax sent successfully!', 'is-success')
#     else:
#         flash('Failed to send fax.', 'is-danger')

#     return redirect(url_for('medicalbill.details', client_id=medical_bill.client_id, medical_provider_id=medical_bill.medical_provider_id))

# # Calendar Events Route
# @medicalbill.route('/calendar/events')
# @login_required
# def get_events():
#     events = []
#     medical_bills = MedicalBill.query.all()
#     for bill in medical_bills:
#         events.append({
#             'title': f'Medical Bill for {bill.provider.name}',
#             'start': bill.last_request_date.isoformat()  # Event date
#         })
#     return jsonify(events)

# # Medical Bill Input Route
# @medicalbill.route('/new/medicalbill/casefile/<int:casefile_id>', methods=['GET', 'POST'])
# @login_required
# def input(casefile_id):
#     medical_providers = MedicalProvider.query.order_by(MedicalProvider.name).all()
#     clients = Client.query.filter(Client.casefile_id == casefile_id).all()
    
#     if request.method == 'POST':
#         client_id = request.form.get("client_id")
#         medical_provider_id = request.form.get("medical_provider_id")
#         is_bill_received = request.form.get("is_bill_received")
#         is_record_received = request.form.get("is_record_received")
#         is_lien_filed = request.form.get("is_lien_filed")
#         is_in_collections = request.form.get("is_in_collections")
        
#         # Process float fields
#         float_fields = [
#             'total_billed', 'insurance_paid', 'insurance_adjusted',
#             'mp_paid', 'patient_paid', 'reduction_amount', 'expense'
#         ]
#         values = {}
        
#         for field in float_fields:
#             try:
#                 values[field] = float(request.form.get(field, 0))
#             except ValueError:
#                 print(f"Couldn't Convert {field}")
#                 values[field] = None

#         # Process last request date
#         try:
#             last_request_date = datetime.strptime(request.form.get("last_request_date"), '%Y-%m-%d').date()
#         except ValueError:
#             print("Last request date couldn't be saved for updated casefile.")
#             last_request_date = None
        
#         # Create new MedicalBill instance
#         try:
#             new_medical_bill = MedicalBill(
#                 client_id=int(client_id),
#                 medical_provider_id=int(medical_provider_id),
#                 is_bill_received=is_bill_received,
#                 is_record_received=is_record_received,
#                 is_lien_filed=is_lien_filed,
#                 is_in_collections=is_in_collections,
#                 total_billed=values['total_billed'],
#                 insurance_paid=values['insurance_paid'],
#                 insurance_adjusted=values['insurance_adjusted'],
#                 mp_paid=values['mp_paid'],
#                 patient_paid=values['patient_paid'],
#                 reduction_amount=values['reduction_amount'],
#                 last_request_date=last_request_date,
#                 expense=values['expense']
#             )
#             db.session.add(new_medical_bill)
#             db.session.commit()
#             flash("Created New Medical Bill successfully!", "is-success")
#         except Exception as e:
#             db.session.rollback()
#             print(f"Error creating new medical bill: {e}")
#             flash("Error creating new medical bill, make sure you're associating the bill with both a client and medical provider.", "is-danger")
        
#         return redirect(url_for('casefile.details', casefile_id=casefile_id))

#     return render_template('medicalbill/medical-bill-input.html', medical_providers=medical_providers, clients=clients)

# # DELETE MEDICAL BILL ROUTE
@medicalbill.route('/<tenant_name>/delete/medicalbill/client/<int:client_id>/medicalprovider/<int:medical_provider_id>')
@login_required
def delete_bill(tenant_name , client_id, medical_provider_id):
    # medicalbill = db.get_or_404(MedicalBill, (client_id, medical_provider_id))
    medicalbill = MedicalBill.query.filter_by(client_id=client_id,medical_provider_id=medical_provider_id, tenant_id=session['tenant_id']).first_or_404()
    casefile_id = medicalbill.client.casefile_id
    try:
        db.session.delete(medicalbill)
        db.session.commit()
        flash("Medical Bill Deleted Successfully", "is-success")
    except Exception as e:
        db.session.rollback()
        print(f"Error deleting medical bill: {e}")
        flash('Something went wrong', 'is-danger')
    return redirect(url_for('casefile.details',tenant_name=tenant_name, casefile_id=casefile_id))
