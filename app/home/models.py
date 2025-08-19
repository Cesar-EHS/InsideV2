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
        try:
            return [proyecto.nombre for proyecto in self.proyectos_visibles.all()]
        except:
            return []

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
    duracion_minutos = db.Column(db.Integer, nullable=True, default=60)  # Duración en minutos
    link_teams = db.Column(db.String(255), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, index=True)

    # Relación con participantes
    participantes = db.relationship('ParticipanteEvento', backref='evento', lazy='dynamic', cascade='all, delete-orphan')

    def get_hora_fin(self):
        """Retorna la hora de finalización calculada basada en la duración"""
        if self.hora and self.duracion_minutos:
            from datetime import datetime, timedelta
            # Convertir time a datetime para hacer cálculos
            inicio = datetime.combine(self.fecha, self.hora)
            fin = inicio + timedelta(minutes=self.duracion_minutos)
            return fin.time()
        return None

    def get_participantes_confirmados(self):
        """Retorna los participantes que confirmaron asistencia"""
        return self.participantes.filter_by(estado='confirmado').all()

    def get_participantes_declinados(self):
        """Retorna los participantes que declinaron asistencia"""
        return self.participantes.filter_by(estado='declinado').all()

    def get_participantes_pendientes(self):
        """Retorna los participantes pendientes"""
        return self.participantes.filter_by(estado='pendiente').all()

    def get_estado_usuario(self, user_id):
        """Retorna el estado del usuario para este evento"""
        participante = self.participantes.filter_by(user_id=user_id).first()
        return participante.estado if participante else 'pendiente'


class ParticipanteEvento(db.Model):
    __tablename__ = 'participante_evento'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    evento_id = db.Column(db.Integer, db.ForeignKey('evento.id'), nullable=False)
    estado = db.Column(Enum('confirmado', 'declinado', 'pendiente', name='estado_participacion'), 
                      default='pendiente', nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    user = db.relationship('User', backref='participaciones_eventos')

    __table_args__ = (
        db.UniqueConstraint('user_id', 'evento_id', name='uix_user_evento'),
    )
