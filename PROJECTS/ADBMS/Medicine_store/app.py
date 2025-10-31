from flask import Flask, render_template, request, redirect, session, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

app = Flask(__name__)
app.secret_key = "secret123"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///database.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

# -------------------- MODELS --------------------
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    purchases = db.relationship("Purchase", backref="buyer", lazy=True)

class Medicine(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Float, nullable=False)
    stock = db.Column(db.Integer, nullable=False)

class Purchase(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    medicine_id = db.Column(db.Integer, db.ForeignKey("medicine.id"), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    total_price = db.Column(db.Float, nullable=False)
    date = db.Column(db.DateTime, default=datetime.utcnow)
    medicine = db.relationship("Medicine")

# -------------------- ROUTES --------------------
@app.route("/")
def index():
    if "user" not in session:
        return redirect(url_for("login"))
    medicines = Medicine.query.all()
    return render_template("home.html", medicines=medicines, user=session["user"])

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            session["user"] = user.username
            session["uid"] = user.id
            return redirect(url_for("index"))
        else:
            flash("Invalid username or password")
    return render_template("login.html")

@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        username = request.form["username"]
        password = generate_password_hash(request.form["password"])
        if User.query.filter_by(username=username).first():
            flash("Username already exists")
        else:
            new_user = User(username=username, password=password)
            db.session.add(new_user)
            db.session.commit()
            flash("Signup successful! Please login.")
            return redirect(url_for("login"))
    return render_template("signup.html")

@app.route("/logout")
def logout():
    session.clear()
    flash("You have logged out.")
    return redirect(url_for("login"))

@app.route("/buy/<int:medicine_id>", methods=["POST"])
def buy_medicine(medicine_id):
    if "user" not in session:
        flash("Please log in to purchase.")
        return redirect(url_for("login"))

    quantity = int(request.form["quantity"])
    med = Medicine.query.get(medicine_id)
    if not med or med.stock < quantity:
        flash("Not enough stock available.")
        return redirect(url_for("index"))

    total = med.price * quantity
    purchase = Purchase(
        user_id=session["uid"],
        medicine_id=medicine_id,
        quantity=quantity,
        total_price=total
    )
    med.stock -= quantity
    db.session.add(purchase)
    db.session.commit()
    flash(f"Purchased {quantity} x {med.name} successfully!")
    return redirect(url_for("index"))

@app.route("/purchases")
def view_purchases():
    if "user" not in session:
        return redirect(url_for("login"))
    purchases = Purchase.query.filter_by(user_id=session["uid"]).all()
    return render_template("purchases.html", purchases=purchases)

# -------------------- DATABASE INIT --------------------
def create_tables():
    with app.app_context():
        db.create_all()
        if not Medicine.query.first():
            meds = [
                Medicine(name="Paracetamol", price=25.0, stock=50),
                Medicine(name="Amoxicillin", price=80.0, stock=30),
                Medicine(name="Cough Syrup", price=60.0, stock=40),
                Medicine(name="Pain Relief Gel", price=100.0, stock=20)
            ]
            db.session.bulk_save_objects(meds)
            db.session.commit()

# -------------------- MAIN --------------------
if __name__ == "__main__":
    create_tables()
    app.run(debug=True)
