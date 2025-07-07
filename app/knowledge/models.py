from app import db
from datetime import datetime
from flask import url_for

class Documento(db.Model):
    """Modelo para documentos subidos al módulo Knowledge."""
    __tablename__ = 'documentos'

    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(150), nullable=False, comment="Nombre descriptivo del documento")
    tipo = db.Column(db.String(20), nullable=False, comment="Tipo de documento: Registro, Procedimiento, etc.")
    categoria = db.Column(db.String(50), nullable=False, index=True, comment="Categoría: Operaciones, Consultoría, etc.")
    archivo = db.Column(db.String(200), nullable=False, comment="Ruta relativa del archivo guardado")
    fecha_carga = db.Column(db.DateTime, default=datetime.utcnow, index=True, comment="Fecha de carga")

    def __repr__(self):
        return f"<Documento id={self.id} nombre='{self.nombre}' categoria='{self.categoria}' tipo='{self.tipo}'>"

    @property
    def filename(self):
        """Devuelve solo el nombre del archivo (sin ruta)."""
        return self.archivo.split('/')[-1]

    def download_url(self):
        """Devuelve la URL Flask para descargar el archivo."""
        return url_for('knowledge.descargar_archivo', archivo=self.archivo)

    # Puedes agregar validaciones adicionales aquí si lo deseas
