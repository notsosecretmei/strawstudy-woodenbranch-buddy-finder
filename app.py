# --------------------------
# IMPORTS
# --------------------------
from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
import random  # For random buddy feature

# --------------------------
# FLASK APP SETUP
# --------------------------
app = Flask(__name__)
app.secret_key = "woodenbranch"  # Change this to anything secret

# --------------------------
# DATABASE SETUP
# --------------------------
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)

# --------------------------
# DATABASE TABLES
# --------------------------
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)  # usernames must be unique
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    instagram = db.Column(db.String(100))
    discord = db.Column(db.String(100))

class BuddyRequest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    receiver_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    status = db.Column(db.String(20), default='pending')  # pending / accepted

# Create tables if they don't exist
with app.app_context():
    db.create_all()

# --------------------------
# ROUTES
# --------------------------

@app.route("/")
def home():
    return redirect(url_for("login"))

# REGISTER
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        instagram = request.form['instagram']
        discord = request.form['discord']

        hashed_pw = bcrypt.generate_password_hash(password).decode('utf-8')

        new_user = User(name=name, email=email, password=hashed_pw,
                        instagram=instagram, discord=discord)
        db.session.add(new_user)
        db.session.commit()

        flash("Registration successful! Please login.", "success")
        return redirect(url_for("login"))
    return render_template("register.html")

# LOGIN
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form['email']
        password = request.form['password']

        user = User.query.filter_by(email=email).first()
        if user and bcrypt.check_password_hash(user.password, password):
            session['user_id'] = user.id
            return redirect(url_for("dashboard"))
        else:
            flash("Invalid email or password", "danger")
    return render_template("login.html")

# DASHBOARD
@app.route("/dashboard", methods=["GET", "POST"])
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for("login"))

    user = User.query.get(session['user_id'])

    # Search functionality
    search_results = []
    if request.method == "POST":
        search_username = request.form['search']
        search_results = User.query.filter(User.name.contains(search_username), User.id != user.id).all()

    # Incoming requests
    incoming_requests = BuddyRequest.query.filter_by(receiver_id=user.id, status='pending').all()

    # Accepted requests
    accepted_requests = BuddyRequest.query.filter_by(sender_id=user.id, status='accepted').all()
    accepted_users = [User.query.get(r.receiver_id) for r in accepted_requests]

    return render_template("dashboard.html",
                           user=user,
                           search_results=search_results,
                           incoming_requests=incoming_requests,
                           accepted_users=accepted_users)

# RANDOM BUDDY FEATURE
@app.route("/find_random")
def find_random():
    if 'user_id' not in session:
        return redirect(url_for("login"))

    user = User.query.get(session['user_id'])
    all_users = User.query.filter(User.id != user.id).all()

    if not all_users:
        flash("No other users found!", "info")
        return redirect(url_for("dashboard"))

    random_user = random.choice(all_users)  # Pick a random buddy
    return render_template("random.html", random_user=random_user)

# SEND REQUEST
@app.route("/send_request/<int:receiver_id>")
def send_request(receiver_id):
    if 'user_id' not in session:
        return redirect(url_for("login"))
    sender_id = session['user_id']

    existing = BuddyRequest.query.filter_by(sender_id=sender_id, receiver_id=receiver_id).first()
    if not existing:
        req = BuddyRequest(sender_id=sender_id, receiver_id=receiver_id)
        db.session.add(req)
        db.session.commit()
        flash("Buddy request sent!", "success")
    else:
        flash("You already sent a request to this user!", "warning")

    return redirect(url_for("dashboard"))

# ACCEPT REQUEST
@app.route("/accept_request/<int:request_id>")
def accept_request(request_id):
    if 'user_id' not in session:
        return redirect(url_for("login"))

    req = BuddyRequest.query.get(request_id)
    if req and req.receiver_id == session['user_id']:
        req.status = "accepted"
        db.session.commit()
        flash("Request accepted!", "success")

    return redirect(url_for("dashboard"))

# LOGOUT
@app.route("/logout")
def logout():
    session.pop('user_id', None)
    return redirect(url_for("login"))

# --------------------------
# RUN APP
# --------------------------

if __name__ == "__main__":
<<<<<<< HEAD
    import os
    port = int(os.environ.get("PORT", 5000))  # Use Render's PORT or default 5000
    app.run(host="0.0.0.0", port=port, debug=True)
=======
import os
    port = int(os.environ.get("PORT", 5000))  # Use Render's PORT or default 5000
    app.run(host="0.0.0.0", port=port, debug=True)

>>>>>>> 363830b294bb7c79fa9ca7beec07a4e132793488
