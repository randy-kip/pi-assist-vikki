from piassist import create_app, db
from piassist.models import Admin
from werkzeug.security import generate_password_hash
import random
import string

def generate_random_password(length=12):
    characters = string.ascii_lowercase + string.ascii_uppercase + string.digits
    password = ''.join(random.choice(characters) for i in range(length))
    return password

app = create_app()

with app.app_context():
    email = input("Enter admin email: ")
    password = input("Enter the password: ")
    hashed_password = generate_password_hash(password)
    print("Password", password)
    new_admin = Admin(
        email=email,
        password=hashed_password,
        role='super_admin'  # Ensure the role is set to 'super_admin' for this admin
    )
    
    db.session.add(new_admin)
    db.session.commit()
    
    print(f"Admin user '{email}' created with password: {password}")
