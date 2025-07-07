from app import db
from app.cursos.models import Curso  # Reutilizar el modelo existente

# Eliminar el modelo duplicado
# class Curso(db.Model):
#     __tablename__ = 'cursos'
#
#     id = db.Column(db.Integer, primary_key=True)
#     nombre = db.Column(db.String(150), nullable=False)
#     descripcion = db.Column(db.Text, nullable=True)
#     categoria_id = db.Column(db.Integer, db.ForeignKey('categorias.id'), nullable=False)
#     categoria = db.relationship('Categoria', back_populates='cursos')
#
#     def __repr__(self):
#         return f'<Curso {self.nombre}>'
