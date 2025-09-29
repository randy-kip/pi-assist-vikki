import requests, os
from datetime import datetime, timezone
from flask import Blueprint,Flask, render_template, request, redirect, url_for, flash, session, abort
from flask_login import current_user, login_required
from flask_mail import Mail, Message
from piassist.models import Casefile,ThirdPartyClaim,FirstPartyClaim, MedicalBill, HealthClaim, Entry,AutoInsurance, Tenant , Reminder,Casefile,Client,CalendarEvent # Assuming a Tenant model
from extension import mail
from . import db

app = Flask(__name__)

casefile = Blueprint('casefile', __name__)

def validate_tenant(tenant_name):
    tenant = Tenant.query.filter_by(name=tenant_name).first()
    if tenant:
        session['tenant_id'] = tenant.id
        session['tenant_name'] = tenant.name
    else:
        flash("Invalid tenant specified in URL.", "is-warning")
        abort(404, description=f"Invalid tenant: '{tenant_name}'")

# Casefile Index Route
@casefile.route('/<tenant_name>/')
def index( tenant_name):
    validate_tenant(tenant_name)
    casefiles = Casefile.query.filter_by(tenant_id=session['tenant_id'], closed=False).order_by(Casefile.date_of_loss).all()
    # Use a shared 'index.html' template
    return render_template('index.html', casefiles=casefiles, tenant_name=tenant_name)

# Case Detail Route
@casefile.route('/<tenant_name>/casefile/<int:casefile_id>/')
def details(tenant_name, casefile_id):
    validate_tenant(tenant_name)
    casefile = Casefile.query.filter_by(id=casefile_id, tenant_id=session['tenant_id']).first_or_404()
    first_party_claim = FirstPartyClaim.query.filter_by(casefile_id=casefile_id).first()
    third_party_claim = ThirdPartyClaim.query.filter_by(tenant_id=session['tenant_id']).first()
    if not first_party_claim:
        # Handle missing first-party claim scenario
        auto_insurance_id = None
    else:
        auto_insurance_id = first_party_claim.auto_insurance_id
    medicalbill = MedicalBill.query.filter_by(tenant_id=session['tenant_id']).first()
    if not medicalbill:
        # Handle missing first-party claim scenario
        medical_provider_id= None
        client_id = None
    else:
        client_id = medicalbill.client_id
        medical_provider_id=medicalbill.medical_provider_id
    health_claim = HealthClaim.query.filter_by(tenant_id=session['tenant_id']).first()
    if not health_claim:

        health_insurance_id=None
        client_id=None
    else:
        health_insurance_id = health_claim.health_insurance_id
        client_id = health_claim.client_id
    if not third_party_claim:
        auto_insurance_id=None
    else:
        auto_insurance_id=third_party_claim.auto_insurance_id
    return render_template('caselog.html',auto_insurance_id=auto_insurance_id,health_insurance_id=health_insurance_id,  medical_provider_id=medical_provider_id, casefile=casefile,client_id=client_id, current_user=current_user, tenant_name=tenant_name)

# Case Worklog Route
@casefile.route('/<tenant_name>/new-entry/<int:casefile_id>', methods=["POST"])
def add_entry(tenant_name, casefile_id):
    validate_tenant(tenant_name)
    casefile = Casefile.query.filter_by(id=casefile_id, tenant_id=session['tenant_id']).first_or_404()
    description = request.form.get("log_entry")
    utc_timestamp = datetime.now(timezone.utc)
    new_entry = Entry(
        casefile_id=casefile_id,
        member_id=current_user.id,
        description=description,
        utc_timestamp=utc_timestamp,
        tenant_id = session['tenant_id']

    )
    db.session.add(new_entry)
    db.session.commit()
    flash(f"New manual caselog entry created by {current_user.name}.", "is-success")
    return redirect(url_for('casefile.details', tenant_name=tenant_name, casefile=casefile, casefile_id=casefile_id))

# Work Log Index Route
@casefile.route('/<tenant_name>/worklog-index/<int:casefile_id>')

def worklog_index(tenant_name, casefile_id):
    validate_tenant(tenant_name)
    casefile = Casefile.query.filter_by(id=casefile_id, tenant_id=session['tenant_id']).first_or_404()
    # Use a shared 'worklog-index.html' template
    return render_template('worklog-index.html', casefile=casefile, tenant_name=tenant_name)

# Delete Work Log Route
@casefile.route('/<tenant_name>/delete/<int:entry_id>')
def delete_entry(tenant_name, entry_id):
    validate_tenant(tenant_name)
    entry = Entry.query.filter_by(id=entry_id, tenant_id=session['tenant_id']).first_or_404()
    db.session.delete(entry)
    db.session.commit()
    flash("Entry deleted successfully", "is-success")
    return redirect(url_for('casefile.worklog_index', tenant_name=tenant_name, casefile_id=entry.casefile_id))

# Delete Casefile Route
@casefile.route('/<tenant_name>/delete/casefile/<int:casefile_id>')
def delete(tenant_name, casefile_id):
    validate_tenant(tenant_name)
    casefile = Casefile.query.filter_by(id=casefile_id, tenant_id=session['tenant_id']).first_or_404()
    db.session.delete(casefile)
    db.session.commit()
    flash("Casefile Deleted Successfully", "is-success")
    return redirect(url_for('casefile.index', tenant_name=tenant_name))

# Accident Detail Route
@casefile.route('/<tenant_name>/casefile/<int:casefile_id>/accident', methods=['GET', 'POST'])
def accident_details(tenant_name, casefile_id):
    validate_tenant(tenant_name)
    casefile = Casefile.query.filter_by(id=casefile_id, tenant_id=session['tenant_id']).first_or_404()

    if request.method == 'POST':
        # Update casefile details from form input
        casefile.wreck_type = request.form.get("wreck_type")
        casefile.wreck_street = request.form.get("wreck_street")
        casefile.wreck_city = request.form.get("wreck_city")
        casefile.wreck_state = request.form.get("wreck_state")
        casefile.wreck_county = request.form.get("wreck_county")
        casefile.wreck_description = request.form.get("wreck_description")
        casefile.is_police_involved = request.form.get("is_police_involved")
        casefile.police_force = request.form.get("police_force")
        casefile.is_police_report = request.form.get("is_police_report")
        casefile.police_report_number = request.form.get("police_report_number")
        casefile.vehicle_description = request.form.get("vehicle_description")
        casefile.damage_level = request.form.get("damage_level")
        casefile.wreck_notes = request.form.get("wreck_notes")
        casefile.stage = request.form.get("stage")
        casefile.status = request.form.get("status")

        # Date and time parsing with validation
        try:
            casefile.date_of_loss = datetime.strptime(request.form.get("date_of_loss"), '%Y-%m-%d').date()
        except ValueError:
            flash("Date of loss couldn't be saved for updated casefile.", "is-warning")

        try:
            casefile.time_of_wreck = datetime.strptime(request.form.get("time_of_wreck"), '%H:%M:%S').time()
        except ValueError:
            try:
                casefile.time_of_wreck = datetime.strptime(request.form.get("time_of_wreck"), '%H:%M').time()
            except ValueError:
                flash("Time of loss couldn't be saved for updated casefile", "is-warning")

        db.session.commit()
        flash("Casefile details updated successfully", "is-success")
        return redirect(url_for('casefile.details', tenant_name=tenant_name, casefile_id=casefile.id))

    # Use a shared 'accident.html' template for all tenants
    return render_template('details/accident.html', casefile=casefile, tenant_name=tenant_name)

# @casefile.route('/<tenant_name>/casefile/<int:casefile_id>/add-reminder', methods=['GET', 'POST'])
# @login_required
# def add_reminder(tenant_name,casefile_id):
#     validate_tenant(tenant_name)
#     casefile = Casefile.query.filter_by(id=casefile_id, tenant_id=session['tenant_id']).all()
    
#     if request.method == 'POST':
#         reminder_type = request.form.get("reminder_type")
#         reminder_date = datetime.strptime(request.form.get("reminder_date"), '%Y-%m-%d').date()
#         reminder_time = request.form.get("reminder_time")
#         reminder_time = datetime.strptime(reminder_time, '%H:%M').time() if reminder_time else None
#         notes = request.form.get("notes")

#         new_reminder = Reminder(
#             casefile_id=casefile_id,
#             reminder_type=reminder_type,
#             reminder_date=reminder_date,
#             reminder_time=reminder_time,
#             notes=notes,
#             tenant_id = session['tenant_id']
#         )
#         db.session.add(new_reminder)
#         db.session.commit()
#         flash("Reminder added successfully", "is-success")
#         return redirect(url_for('casefile.details', tenant_name=tenant_name, casefile_id=casefile_id))

#     return render_template('calenders/add_reminder.html', tenant_name=tenant_name)

# # Calendar Route
# @casefile.route('/<tenant_name>/calendar')
# @login_required
# def calendar(tenant_name):
#     validate_tenant(tenant_name)
    
#     # Query reminders associated with the tenant or all casefiles for this tenant
#     reminders = Reminder.query.filter_by(tenant_id=session['tenant_id']).all()
    
#     # Pass the reminders to the template for displaying in the calendar
#     return render_template('calenders/calendar.html', reminders=reminders, tenant_name=tenant_name)



@casefile.route('/<tenant_name>/casefile/<int:casefile_id>/send_reminder', methods=['GET', 'POST'])
def send_reminder(tenant_name, casefile_id):
    # Fetch the casefile based on the casefile_id and tenant_id from the session
    casefile = Casefile.query.filter_by(id=casefile_id, tenant_id=session['tenant_id']).first()
    
    # If the casefile does not exist, redirect or handle error
    if not casefile:
        flash("Casefile not found.", "danger")
        return redirect(url_for('casefile.details', tenant_name=tenant_name, casefile_id=casefile_id))

    client = Client.query.filter_by(casefile_id=casefile.id, tenant_id=session['tenant_id']).first()

    if request.method == 'POST':
        client_id = request.form['client_id']  # Get client_id from form data
        # Correctly filter the client based on casefile_id and client_id
        client = Client.query.filter_by(id=client_id, casefile_id=casefile.id, tenant_id=session['tenant_id']).first()
        
        if not client:
            flash("Client not found for the given casefile.", "danger")
            return redirect(url_for('casefile.details', tenant_name=tenant_name, casefile_id=casefile_id))
        reminder_type=request.form['reminder_type']
        method = request.form['method']
        message = request.form['message']

        # Create the reminder
        reminder = Reminder(casefile_id=casefile_id, tenant_id=session['tenant_id'],reminder_type=reminder_type, method=method, message=message)
        db.session.add(reminder)
        db.session.commit()

        # Send email or notification based on the method selected
        if method == 'email':
            msg = Message(
                subject=f"{reminder_type} Reminder for Case: {casefile.case_label}",
                recipients=[client.email],
                body=f"Dear {client.full_name},\n\n{message}\n\nBest Regards,\n{tenant_name}"
            )
            try:
                mail.send(msg)
                flash("Email reminder sent successfully!", "success")
            except Exception as e:
                flash(f"Error sending email: {str(e)}", "danger")

        elif method == 'notification':
            flash(f"Reminder sent as notification: {message}", "danger")

        return redirect(url_for('casefile.details', tenant_name=tenant_name, casefile_id=casefile_id))

    return render_template('add_reminder.html', tenant_name=tenant_name, casefile_id=casefile_id, client=client)


@casefile.route('/<tenant_name>/calendar')
def view_calendar(tenant_name):
    # Get events for the current tenant
    events = CalendarEvent.query.filter_by(tenant_id=session['tenant_id']).all()
    
    # Format events for FullCalendar (JSON format)
    calendar_events = []
    for event in events:
        calendar_events.append({
            'title': event.event_name,
            'start': event.start_datetime.isoformat(),
            'end': event.end_datetime.isoformat(),
            'description': event.description,
            'event_type': event.event_type,
            'id': event.id
        })
    
    return render_template('calendar.html', tenant_name=tenant_name, events=calendar_events)
@casefile.route('/<tenant_name>/calendar/add_event', methods=['GET', 'POST'])
def add_event(tenant_name):
    clients = Client.query.filter_by(tenant_id=session['tenant_id']).all()
    casefiles = Casefile.query.filter_by(tenant_id=session['tenant_id']).all()
    if request.method == 'POST':
        event_name = request.form['event_name']
        description = request.form.get('description')
        client_id = request.form['client_id']
        casefile_id = request.form['casefile_id']
        event_type = request.form['event_type']

        start_datetime = datetime.strptime(request.form['start_datetime'], "%Y-%m-%dT%H:%M")
        end_datetime = datetime.strptime(request.form['end_datetime'], "%Y-%m-%dT%H:%M")

        # Create new calendar event
        event = CalendarEvent(
            tenant_id=session['tenant_id'],
            casefile_id=casefile_id,
            client_id=client_id,
            event_name=event_name,
            start_datetime=start_datetime,
            end_datetime=end_datetime,
            description=description,
            event_type=event_type
        )
        db.session.add(event)
        db.session.commit()
        
        flash("Event created successfully!", "success")
        return redirect(url_for('casefile.view_calendar', tenant_name=tenant_name))
    
    return render_template('add_event.html',clients=clients,casefiles=casefiles, tenant_name=tenant_name)
@casefile.route('/<tenant_name>/calendar/edit_event/<int:event_id>', methods=['GET', 'POST'])
def edit_event(tenant_name, event_id):
    event = CalendarEvent.query.get_or_404(event_id)
    clients = Client.query.filter_by(tenant_id=session['tenant_id']).all()
    casefiles = Casefile.query.filter_by(tenant_id=session['tenant_id']).all()
    if request.method == 'POST':
        event.event_name=request.form.get('event_name')
        event.start_datetime = datetime.strptime(request.form['start_datetime'], "%Y-%m-%dT%H:%M")
        event.end_datetime = datetime.strptime(request.form['end_datetime'], "%Y-%m-%dT%H:%M")
        event.description = request.form.get('description')
        event.client_id = request.form['client_id']
        event.casefile_id = request.form['casefile_id']
        event.event_type = request.form['event_type']

        db.session.commit()
        
        flash("Event updated successfully!", "success")
        return redirect(url_for('casefile.view_calendar', tenant_name=tenant_name))
    
    return render_template('edit_event.html', tenant_name=tenant_name,clients=clients,casefiles=casefiles, event=event)
@casefile.route('/<tenant_name>/calendar/delete_event/<int:event_id>', methods=['POST'])
def delete_event(tenant_name, event_id):
    event = CalendarEvent.query.get_or_404(event_id)
    
    db.session.delete(event)
    db.session.commit()
    
    flash("Event deleted successfully!", "success")
    return redirect(url_for('casefile.view_calendar', tenant_name=tenant_name))
# @casefile.route('/<tenant_name>/close_casefile/casefile/<int:casefile_id>', methods=[ 'POST'])
# def close_casefile(casefile_id):
#     casefile = Casefile.query.filter_by(id=casefile_id, tenant_id=session['tenant_id']).first_or_404()
    
#     casefile.closed = True  # Mark casefile as closed
#     db.session.commit()
    
#     flash("Case file has been moved to Closed Case Files.", "success")
#     return redirect(url_for('index'))
# from flask import request, jsonify

# @casefile.route('/<tenant_name>/close_casefile/casefile/<int:casefile_id>', methods=['POST'])
# def close_casefile(tenant_name, casefile_id):
#     casefile = Casefile.query.filter_by(id=casefile_id, tenant_name=tenant_name).first()
    
#     if not casefile:
#         return jsonify({"success": False, "error": "Casefile not found"}), 404

#     try:
#         casefile.closed = True  # Update the Boolean field
#         db.session.commit()
#         return jsonify({"success": True, "message": "Casefile successfully moved to closed!"})
    
#     except Exception as e:
#         db.session.rollback()
#         return jsonify({"success": False, "error": str(e)}), 500
from flask import request, jsonify, flash, redirect, url_for

@casefile.route('/<tenant_name>/close_casefile/casefile/<int:casefile_id>', methods=['POST'])
def close_casefile(tenant_name, casefile_id):
    casefile = Casefile.query.filter_by(id=casefile_id, tenant_id=session['tenant_id']).first()
    
    if not casefile:
        return jsonify({"success": False, "error": "Casefile not found"}), 404

    try:
        # Mark the casefile as closed
        casefile.closed = True  
        db.session.commit()
        
        # Flash message for success and return success response
        flash("Case file has been moved to Closed Case Files.", "success")
        return jsonify({"success": True, "message": "Casefile successfully moved to closed!"})
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "error": str(e)}), 500

@casefile.route('/<tenant_name>/closed_casefiles')
def closed_casefiles(tenant_name):
    casefiles = Casefile.query.filter_by(tenant_id=session['tenant_id'] , closed=True).all()
    return render_template('closed_casefiles.html',tenant_name=tenant_name, casefiles=casefiles)




