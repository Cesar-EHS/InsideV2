# Inside Intranet

## Descripción
Intranet modular para gestión de usuarios, cursos, logros, tickets y base de conocimiento, desarrollada con Flask y Blueprints.

## Estructura de carpetas
- `app/` - Código principal y módulos
- `migrations/` - Migraciones de base de datos
- `instance/` - Base de datos SQLite
- `venv/` - Entorno virtual Python
- `tests/` - Pruebas unitarias y de integración

## Instalación rápida
```bash
python -m venv venv
venv\Scripts\activate  # En Windows
pip install -r requirements.txt
```

## Ejecución
```bash
python manage.py
```

## Variables de entorno
- Configura tu archivo `.env` con las variables necesarias (ver `config.py`).

## Módulos principales
- Autenticación (`auth`)
- Cursos (`cursos`)
- Home/Dashboard (`home`)
- Knowledge Base (`knowledge`)
- Logros (`logros`)
- Perfil de usuario (`perfil`)
- Tickets/Soporte (`tickets`)
- Búsqueda global (`search`)

## Buenas prácticas implementadas
- Estructura modular y escalable usando Blueprints.
- Separación clara de modelos, rutas, formularios y plantillas por módulo.
- Uso de variables de entorno y configuración centralizada.
- Migraciones de base de datos con Alembic.
- Pruebas unitarias en carpeta `tests/`.
- Documentación y comentarios en el código.
- Control de acceso y roles en rutas sensibles.
- Recursos estáticos centralizados y reutilizables.

## Contacto
Desarrollado por el equipo Inside.
