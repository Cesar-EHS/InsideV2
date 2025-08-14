import sqlite3

# Connect to database
conn = sqlite3.connect('instance/base_datos.db')

# Update user 1 to be admin
conn.execute("UPDATE usuarios SET rol = 'admin' WHERE id = 1;")
conn.commit()

# Check the update
cursor = conn.cursor()
cursor.execute("SELECT id, nombre, apellido_paterno, rol FROM usuarios WHERE id = 1;")
user = cursor.fetchone()
if user:
    print(f"User {user[0]}: {user[1]} {user[2]} - Role: {user[3]}")
else:
    print("No user found with ID 1")

conn.close()
print("Database updated successfully")
