from flask import render_template, request, jsonify
from app.crecehs import bp_crecehs
from app.cursos.models import Categoria, Curso
from app import db

@bp_crecehs.route('/')
def index():
    return render_template('index.html')

@bp_crecehs.route('/categorias', methods=['GET'])
def get_categorias():
    categorias = Categoria.query.all()
    return jsonify([{'id': c.id, 'nombre': c.nombre} for c in categorias])

@bp_crecehs.route('/cursos/<int:categoria_id>', methods=['GET'])
def get_cursos_por_categoria(categoria_id):
    cursos = Curso.query.filter_by(categoria_id=categoria_id).all()
    return jsonify([{'id': c.id, 'nombre': c.nombre, 'descripcion': c.descripcion} for c in cursos])

@bp_crecehs.route('/categorias', methods=['POST'])
def crear_categoria():
    data = request.get_json()
    nueva_categoria = Categoria(nombre=data['nombre'])
    db.session.add(nueva_categoria)
    db.session.commit()
    return jsonify({'id': nueva_categoria.id, 'nombre': nueva_categoria.nombre}), 201

@bp_crecehs.route('/cursos', methods=['POST'])
def crear_curso():
    data = request.get_json()
    nuevo_curso = Curso(nombre=data['nombre'], descripcion=data['descripcion'], categoria_id=data['categoria_id'])
    db.session.add(nuevo_curso)
    db.session.commit()
    return jsonify({'id': nuevo_curso.id, 'nombre': nuevo_curso.nombre, 'descripcion': nuevo_curso.descripcion}), 201
