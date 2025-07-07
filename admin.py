from models import User, db

def get_pending_users():
    """
    Returns a list of users who have not yet been approved.
    """
    pending = User.query.filter_by(approved=False).all()
    return [{"email": u.email, "id": idx} for idx, u in enumerate(pending)]

def approve_user(user_email):
    """
    Approves a user account.
    """
    user = User.query.filter_by(email=user_email).first()
    if user and not user.approved:
        user.approved = True
        db.session.commit()

def remove_user(user_email):
    """
    Removes a user from the database if they are not an admin.
    """
    user = User.query.filter_by(email=user_email).first()
    if user and not user.is_admin:
        db.session.delete(user)
        db.session.commit()
