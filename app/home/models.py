from datetime import datetime
from app import db
from app.auth.models import User
from sqlalchemy import Enum

# Tabla de asociación para la relación many-to-many entre Post y Proyecto
post_proyectos = db.Table('post_proyectos',
    db.Column('post_id', db.Integer, db.ForeignKey('post.id'), primary_key=True),
    db.Column('proyecto_id', db.Integer, db.ForeignKey('proyectos.id'), primary_key=True)
)

class Post(db.Model):
    __tablename__ = 'post'

    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    image_filename = db.Column(db.String(255), nullable=True)  # Para ruta de imagen
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False, index=True)
    visible_para_todos = db.Column(db.Boolean, default=False, nullable=False)  # True si es visible para todos los proyectos

    user = db.relationship('User', backref='posts')
    proyectos_visibles = db.relationship('Proyecto', secondary=post_proyectos, 
                                        backref=db.backref('posts', lazy='dynamic'))

    comments = db.relationship('Comment', backref='post', lazy='dynamic', cascade='all, delete-orphan')
    reactions = db.relationship('Reaction', backref='post', lazy='dynamic', cascade='all, delete-orphan')

    def get_proyectos_nombres(self):
        """Retorna una lista con los nombres de los proyectos que pueden ver esta publicación"""
        if self.visible_para_todos:
            return ['Todos los proyectos']
        return [proyecto.nombre for proyecto in self.proyectos_visibles]

    def puede_ver_usuario(self, usuario):
        """Verifica si un usuario puede ver esta publicación basado en su proyecto"""
        if self.visible_para_todos:
            return True
        if not usuario.proyecto:
            return False
        return usuario.proyecto in self.proyectos_visibles

class Comment(db.Model):
    __tablename__ = 'comment'

    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(500), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'), nullable=False, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False, index=True)

    user = db.relationship('User', backref='comments')

class Reaction(db.Model):
    __tablename__ = 'reaction'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False, index=True)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'), nullable=False, index=True)
    type = db.Column(db.String(20), nullable=False, default='love')

    user = db.relationship('User', backref='reactions')

    # La existencia de este registro indica que el usuario reaccionó con "love" a ese post
    __table_args__ = (
        db.UniqueConstraint('user_id', 'post_id', name='uix_user_post_reaction'),
    )

class Evento(db.Model):
    __tablename__ = 'evento'

    id = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(100), nullable=False)
    descripcion = db.Column(db.Text, nullable=True)
    fecha = db.Column(db.Date, nullable=False, index=True)
    hora = db.Column(db.Time, nullable=True)
    link_teams = db.Column(db.String(255), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, index=True)
