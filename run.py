from piassist import create_app
from extension import mail
app = create_app()


mail.init_app(app)


if __name__ == "__main__":
    print("Initializing the Flask app...")
    # run_folder_creation_tasks()szbi cpfj aeob xkce  # This ensures the folder creation runs when the app startshost="0.0.0.0", port=80,
    app.run( host = '0.0.0.0', port = 5000, debug=True,ssl_context=('certs/server.crt', 'certs/server.key'))
    
