from datetime import datetime
from app import db

class UserHistoryChange(db.Model):  # type: ignore
    """Modelo para registrar cambios en los perfiles de usuario."""
    __tablename__ = 'user_history_changes'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    field_name = db.Column(db.String(50), nullable=False)
    old_value = db.Column(db.String(500))
    new_value = db.Column(db.String(500))
    changed_by_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    changed_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __init__(self, user_id: int, field_name: str, old_value: str, new_value: str, changed_by_id: int):
        self.user_id = user_id
        self.field_name = field_name
        self.old_value = old_value
        self.new_value = new_value
        self.changed_by_id = changed_by_id
