from piassist import create_app, db  # Adjust the import based on your project structure

app = create_app()

with app.app_context():
    # Drop all existing tables
    db.drop_all()

    # Create all tables with the new schema
    db.create_all()

    print("Database updated successfully.")