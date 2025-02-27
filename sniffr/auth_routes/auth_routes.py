from sqlite3 import IntegrityError
from traitlets import Integer
from flask import Blueprint, request, jsonify, session
from sniffr.models import User, db
import jwt
from datetime import datetime, timedelta
import os
from sqlalchemy.exc import IntegrityError

SECRET_KEY = os.getenv("SECRET_KEY")

# Blueprint Configuration
auth_bp = Blueprint("auth_bp", __name__)

# Login route
@auth_bp.route("/login", methods=["POST"])
def login():
    """When a correct email and password is given, provide a success prompt"""
    content = request.json
    email = content["email"].lower()
    passwd = content["password"]

    # Make sure email and password are provided
    if email and passwd:
        result = db.session.query(User).filter_by(email=f"{email}").first()

        # Check that there is a valid result and a correct password
        if result and result.verify_password(password=passwd):

            # generates the JWT Token
            session['id'] = result.user_id
            token = jwt.encode(
                {
                    "user_id": result.user_id,
                    "exp": datetime.utcnow() + timedelta(days=7),
                },
                SECRET_KEY,
            )
            return jsonify({"token": token}), 201

        else:
            return jsonify({'error': 'Invalid login'}), 400

    else:
        return jsonify({'error': 'Email or password missing'}), 400


# Create user route
@auth_bp.route("/register", methods=["POST"])
def register():
    """Creates a user when an email and new password is supplied."""

    # Grab json content
    content = request.json
    email = content["email"].lower()
    passwd = content["password"]

    # Create user
    new_user = User(password=passwd, email=email)

    try:
        db.session.add(new_user)
        db.session.commit()
        return {
            "user_id": new_user.user_id,
            "email": new_user.email,
            }

    except IntegrityError:
        return jsonify({'error': 'Email already exists in database'}), 400
