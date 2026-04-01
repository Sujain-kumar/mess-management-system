from flask import Flask, request, jsonify
from pymongo import MongoClient
from flask_cors import CORS
from datetime import datetime

app = Flask(__name__)
CORS(app)

client = MongoClient("mongodb://localhost:27017/")
db = client["messdb"]

users = db["users"]
menu = db["menu"]
attendance = db["attendance"]
complaints = db["complaints"]


@app.route("/")
def home():
    return "Mess Management Backend Running"


# ------------------- AUTH -------------------

@app.route("/register", methods=["POST"])
def register():
    data = request.json

    existing = users.find_one({"email": data["email"]})
    if existing:
        return jsonify({"message": "Email already exists"})

    users.insert_one(data)
    return jsonify({"message": "User Registered"})


@app.route("/login", methods=["POST"])
def login():
    data = request.json

    user = users.find_one({
        "email": data["email"],
        "password": data["password"]
    })

    if user:
        return jsonify({
            "message": "Login Successful",
            "role": user["role"],
            "name": user["name"]
        })
    else:
        return jsonify({"message": "Invalid email or password"})


# ------------------- USERS -------------------

@app.route("/users", methods=["GET"])
def get_users():
    data = list(users.find({}, {"_id": 0}))
    return jsonify(data)


@app.route("/delete_user/<email>", methods=["DELETE"])
def delete_user(email):
    users.delete_one({"email": email})
    return jsonify({"message": "User Deleted"})


# ------------------- MENU -------------------

@app.route("/menu", methods=["POST"])
def add_menu():
    data = request.json

    existing = menu.find_one({"day": data["day"]})
    if existing:
        return jsonify({"message": "Menu already exists"})

    menu.insert_one(data)
    return jsonify({"message": "Menu Added"})


@app.route("/menu/<day>", methods=["PUT"])
def update_menu(day):
    data = request.json

    menu.update_one(
        {"day": day},
        {"$set": {
            "breakfast": data["breakfast"],
            "lunch": data["lunch"],
            "dinner": data["dinner"]
        }},
        upsert=True
    )

    return jsonify({"message": "Menu Updated"})


@app.route("/menu", methods=["GET"])
def get_menu():
    today = datetime.today().strftime("%A")
    data = menu.find_one({"day": today}, {"_id": 0})
    return jsonify(data)


# 🔥 NEW API (IMPORTANT)
@app.route("/menu_all", methods=["GET"])
def get_all_menu():
    data = list(menu.find({}, {"_id": 0}))
    return jsonify(data)


# ------------------- ATTENDANCE -------------------

@app.route("/attendance", methods=["POST"])
def mark_attendance():
    data = request.json

    user = data["user"].strip().lower()

    existing = attendance.find_one({
        "user": user,
        "date": data["date"],
        "meal": data["meal"]
    })

    if existing:
        return jsonify({"message": f"{data['meal']} already marked today"})

    attendance.insert_one({
        "user": user,
        "date": data["date"],
        "meal": data["meal"]
    })

    return jsonify({"message": f"{data['meal']} marked successfully"})


@app.route("/attendance", methods=["GET"])
def get_attendance():
    data = list(attendance.find({}, {"_id": 0}))
    return jsonify(data)


# ------------------- BILL -------------------

@app.route("/bill/<user>", methods=["GET"])
def calculate_bill(user):

    user = user.strip().lower()

    meals = list(attendance.find({"user": user}))

    total_meals = len(meals)
    total_amount = total_meals * 50

    return jsonify({
        "user": user,
        "total_meals": total_meals,
        "amount": total_amount
    })


# ------------------- COMPLAINT -------------------

@app.route("/complaint", methods=["POST"])
def add_complaint():
    data = request.json
    complaints.insert_one(data)
    return jsonify({"message": "Complaint Submitted"})


@app.route("/complaints", methods=["GET"])
def get_complaints():
    data = list(complaints.find({}, {"_id": 0}))
    return jsonify(data)


# ------------------- RUN -------------------

if __name__ == "__main__":
    app.run(port=5000)