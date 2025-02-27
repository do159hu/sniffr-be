from flask import Blueprint, request, session, jsonify
from sniffr.models import User, db, token_required, process_record
import datetime

user_bp = Blueprint("user_bp", __name__)


@user_bp.route("/user", methods=["DELETE"])
@token_required
def delete_user(current_user):
    user_id = current_user.user_id
    queried_user = db.session.query(User).filter(User.user_id == user_id).first()

    if queried_user:
        db.session.delete(queried_user)
        db.session.commit()
        session['id'] = None
        return {}, 200

    else:
        response = {}
        return response, 204


@user_bp.route("/user/edit", methods=["POST"])
@token_required
def edit_user(current_user):
    """Edits a user."""
    content = request.json

    user_id = current_user.user_id
    queried_user = db.session.query(User).filter(User.user_id == user_id).first()

    if queried_user:
        edit_birthday = content["birthday"].split(', ')[1]
        edit_birthday = datetime.datetime.strptime(edit_birthday, '%d %b %Y %H:%M:%S %Z')
        queried_user.email = content["email"].lower()
        queried_user.birthday = edit_birthday
        queried_user.gender = content["gender"]
        queried_user.max_distance = content["max_distance"]
        queried_user.name = content["name"]
        queried_user.user_bio = content["user_bio"]
        queried_user.zipcode = content["zipcode"]
        queried_user.user_pic = content["user_pic"]

        db.session.commit()

        response = process_record(queried_user)
        return response

    else:
        return jsonify({'error': 'User not found'}), 400


@user_bp.route("/user", methods=["GET"])
def get_user():
    user_id = session.get('id', None)
    if(user_id is None):
        return jsonify({'error': 'No current user logged in'}), 403
    current_user = db.session.query(User).filter(User.user_id == user_id).first()
    current_user = process_record(current_user)

    return jsonify({"current_user": current_user}), 200

# TODO - when create logout endpoint always clear: session['id'] = None