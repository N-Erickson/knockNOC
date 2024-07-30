from app import create_app, db

app = create_app()

with app.app_context():
    db.create_all()  # Ensure the database schema is created

if __name__ == '__main__':
    app.run(host="0.0.0.0", debug=True)