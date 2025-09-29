from celery import Celery
from flask_mail import Message
from datetime import timedelta
from models import MedicalBill

def make_celery(app):
    celery = Celery(app.import_name, backend=app.config['CELERY_RESULT_BACKEND'],
                    broker=app.config['CELERY_BROKER_URL'])
    celery.conf.update(app.config)
    return celery

@celery.task
def send_reminder_email(bill_id):
    medical_bill = MedicalBill.query.get(bill_id)
    msg = Message(f'Reminder for Medical Bill {medical_bill.id}',
                  recipients=[medical_bill.client.email])
    msg.body = f"Reminder: You have a pending medical bill with {medical_bill.provider.name}."
    mail.send(msg)

# Schedule the task (you can use Celery beat for this)
