# --------------------------
# IMPORTS
# --------------------------
from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt

# --------------------------
# FLASK APP SETUP
# --------------------------
app = Flask(__name__)
app.secret_key = "woodenbranch"  # Simple secret key (fine for testing)

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
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    instagram = db.Column(db.String(100))
    discord = db.Column(db.String(100))

class BuddyRequest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    receiver_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    status = db.Column(db.String(20), default='pending')  # pending / accepted

# Create tables
with app.app_context():
    db.create_all()

# --------------------------
# ROUTES
# --------------------------

# Home → redirect to login
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

        # Hash password
        hashed_pw = bcrypt.generate_password_hash(password).decode('utf-8')

        # Save user
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
@app.route("/dashboard")
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for("login"))

    user = User.query.get(session['user_id'])
    users = User.query.filter(User.id != user.id).all()
    incoming_requests = BuddyRequest.query.filter_by(receiver_id=user.id, status='pending').all()
    accepted_requests = BuddyRequest.query.filter_by(sender_id=user.id, status='accepted').all()
    accepted_users = [User.query.get(r.receiver_id) for r in accepted_requests]

    return render_template("dashboard.html",
                           user=user,
                           users=users,
                           incoming_requests=incoming_requests,
                           accepted_users=accepted_users)

# LOGOUT
@app.route("/logout")
def logout():
    session.pop('user_id', None)
    return redirect(url_for("login"))

# SEND REQUEST
@app.route("/send_request/<int:receiver_id>")
def send_request(receiver_id):
    if 'user_id' not in session:
        return redirect(url_for("login"))
    sender_id = session['user_id']

    # Don’t send duplicate requests
    existing = BuddyRequest.query.filter_by(sender_id=sender_id, receiver_id=receiver_id).first()
    if not existing:
        req = BuddyRequest(sender_id=sender_id, receiver_id=receiver_id)
        db.session.add(req)
        db.session.commit()

    return redirect(url_for("dashboard"))

# ACCEPT REQUEST
@app.route("/accept_request/<int:request_id>")
def accept_request(request_id):
    if 'user_id' not in session:
        return redirect(url_for("login"))

    buddy_request = BuddyRequest.query.get(request_id)
    if buddy_request and buddy_request.receiver_id == session['user_id']:
        buddy_request.status = "accepted"
        db.session.commit()

    return redirect(url_for("dashboard"))

# --------------------------
# RUN APP
# --------------------------
if __name__ == "__main__":
    app.run(debug=True)
