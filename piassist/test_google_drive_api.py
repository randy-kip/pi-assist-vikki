from flask import Flask
from flask_mail import Mail, Message

app = Flask(__name__)

# Flask-Mail setup
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'mustafaprogrammer786@gmail.com'
app.config['MAIL_PASSWORD'] = 'kzbfiitdknsxwrym'
app.config['MAIL_DEFAULT_SENDER'] = 'mustafaprogrammer786@gmail.com'

mail = Mail(app)

@app.route('/')
def index():
    try:
        msg = Message('Test Email', recipients=['mustafaprogrammer786@gmail.com'])
        msg.body = 'This is a test email.'
        mail.send(msg)
        return "Email sent!"
    except Exception as e:
        return f"Error: {str(e)}"

if __name__ == '__main__':
    app.run(debug=True)
