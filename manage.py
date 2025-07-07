from app import create_app, db
from flask_migrate import Migrate
from app.auth.models import User  # importa todos los modelos
from flask.cli import with_appcontext
import click

app = create_app()
migrate = Migrate(app, db)

@click.command('list-users')
@with_appcontext
def list_users():
    users = User.query.all()
    for u in users:
        print(f"ID: {u.id} | Nombre: {u.nombre} | Email: {u.email}")

app.cli.add_command(list_users)

if __name__ == '__main__':
    app.run(debug=True)
