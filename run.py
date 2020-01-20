from app import app, db

if __name__ == "__main__" :
    db.create_all()
    app.secret_key = "72a719743bbee8d9a97adf2e75faa92a"
    app.run(debug = True)