# Librerías de interfaz (si usas Tkinter)
import tkinter as tk
from tkinter import messagebox
import sqlite3
import csv
from turtle import undo
from flask import Flask, render_template, redirect, url_for, request, flash
from flask_sqlalchemy import SQLAlchemy



# Conexión directa con sqlite3 que será reemplazada
conexion = sqlite3.connect('database.db')
conexion.row_factory = sqlite3.Row
cursor = conexion.cursor()
conexion.execute("PRAGMA foreign_keys = ON;")
# Crear tablas si no existen
cursor.execute("""
CREATE TABLE IF NOT EXISTS referido (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT NOT NULL,
    correo TEXT UNIQUE NOT NULL,
    telefono TEXT NOT NULL
);
""")
cursor.execute("""CREATE TABLE IF NOT EXISTS nota (
    id_nota INTEGER PRIMARY KEY AUTOINCREMENT,
    id_referido INTEGER NOT NULL,
    nota TEXT NOT NULL,
    FOREIGN KEY(id_referido) REFERENCES referido(id_referido)
);
""")

cursor.execute("""CREATE TABLE IF NOT EXISTS usuarios(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT NOT NULL,
    correo TEXT UNIQUE NOT NULL,
    contraseña TEXT NOT NULL
);
""")
conexion.commit()

# Función para insertar un nuevo referido
def insertar_referido(nombre, correo, telefono):
    """Agrega un nuevo referido a la base de datos."""
    if not all([nombre, correo, telefono]):  # Validación simplificada de campos vacíos
        raise ValueError("Error: Todos los campos (nombre, correo y teléfono) son obligatorios.")
    
    try:
        cursor.execute(
            "INSERT INTO referido (nombre, correo, telefono) VALUES (?, ?, ?);",
            (nombre, correo, telefono)
        )
        conexion.commit()
        print("Referido agregado con éxito.")
    except sqlite3.Error as e:
        raise Exception(f"Error al insertar el referido: {e}")

# Función para consultar todos los referidos
def consultar_referido():
    """Consulta y muestra todos los referidos registrados."""
    try:
        cursor.execute("SELECT * FROM referido;")
        referidos = cursor.fetchall()
        if referidos:
            print("\nLista de referidos:")
            for referido in referidos:
                print(f"ID: {referido[0]}, Nombre: {referido[1]}, Correo: {referido[2]}, Teléfono: {referido[3]}")
        else:
            return referidos
    except sqlite3.Error as e:
        raise Exception(f"Error al consultar referidos: {e}")
# Función para actualizar un referido existente
def actualizar_referidos(id_referido, nombre, correo, telefono):
    """Actualiza la información de un referido según su ID."""
    if not nombre or not correo or not telefono:
        raise ValueError("Error: Todos los campos son obligatorios.")

    try:
        cursor.execute(
            "UPDATE referido SET nombre = ?, correo = ?, telefono = ? WHERE id_referido = ?;",
            (nombre, correo, telefono, id_referido))
        if cursor.rowcount == 0:
            raise LookupError(f"No se encontró ningún referido con ID {id_referido}.")
        else:
            conexion.commit()
            print("Referido actualizado con éxito.")
    except sqlite3.Error as e:
        raise Exception(f"Error al actualizar el referido: {e}")
# Función para eliminar un referido
def eliminar_referidos(id_referido):
    """Elimina un referido de la base de datos."""
    try:
        cursor.execute("DELETE FROM referido WHERE id_referido = ?;", (id_referido,))
        if cursor.rowcount == 0:
            raise LookupError(f"No se encontró ningún referido con ID {id_referido}.")
        else:
            conexion.commit()
            print("Referido eliminado con éxito.")
    except sqlite3.Error as e:
        raise Exception(f"Error al eliminar el referido: {e}")
# Función para exportar referidos a CSV
def exportar_datos(nombre_archivo="referidos.csv"):
    """Exporta referidos registrados a un archivo CSV."""
    try:
        cursor.execute("SELECT * FROM referido;")
        datos = cursor.fetchall()
        if not datos:
            raise ValueError("No hay datos en la base de datos para exportar.")
        with open(nombre_archivo, mode="w", newline="") as archivo_csv:
            escritor = csv.writer(archivo_csv)
            escritor.writerow(["ID", "Nombre", "Correo", "Teléfono"])
            escritor.writerows(datos)
        print(f"Datos exportados exitosamente a {nombre_archivo}.")
    except (sqlite3.Error, IOError) as e:
        raise Exception(f"Error al exportar los datos: {e}")
# Función para agregar una nota a un referido
def agregar_nota(id_referido, nota):
    """Agrega una nota asociada a un referido."""
    if not nota:
        raise ValueError("Error: La nota no puede estar vacía.")

    try:
        cursor.execute("SELECT * FROM referido WHERE id_referido = ?;", (id_referido,))
        if not cursor.fetchone():
            raise LookupError(f"No existe ningún referido con ID {id_referido}.")
            return
        cursor.execute("INSERT INTO nota (id_referido, nota) VALUES (?, ?);", (id_referido, nota))
        conexion.commit()
        print("Nota agregada con éxito.")
    except sqlite3.Error as e:
        raise Exception(f"Error al agregar la nota: {e}")
# Función para consultar notas
def consultar_nota(id_referido):
    """Consulta las notas asociadas a un referido usando su ID."""
    try:
        cursor.execute("SELECT nota FROM nota WHERE id_referido = ?;", (id_referido,))
        notas = cursor.fetchall()
        if notas:
            print(f"\nNotas registradas para el referido {id_referido}:")
            for i, nota in enumerate(notas, 1):
                print(f"{i}. {nota[0]}")
        else:
            raise LookupError(f"No hay notas registradas para el referido {id_referido}.")
    except sqlite3.Error as e:
        raise Exception(f"Error al consultar las notas: {e}")
# Menú principal
while True:
    print("\nMenú Principal")
    print("1. Agregar referido")
    print("2. Consultar referidos")
    print("3. Actualizar datos de referido")
    print("4. Eliminar referido")
    print("5. Exportar referidos a CSV")
    print("6. Agregar nota a referido")
    print("7. Consultar notas de referido")
    print("8. Salir")
    opcion = input("Seleccione una opción: ").strip()

    if opcion == "1":
        nombre = input("Nombre: ").strip()
        correo = input("Correo: ").strip()
        telefono = input("Teléfono: ").strip()
        insertar_referido(nombre, correo, telefono)
    elif opcion == "2":
        consultar_referido()
    elif opcion == "3":
        try:
            id_referido = int(input("ID del referido a actualizar: ").strip())
            nombre = input("Nuevo nombre: ").strip()
            correo = input("Nuevo correo: ").strip()
            telefono = input("Teléfono actualizado: ").strip()
            telefono = input("Teléfono nuevo: ").strip()
        except ValueError:
            print("Error: El ID debe ser un número válido.")
    elif opcion == "4":
        try:
            id_referido = int(input("ID del referido a eliminar: ").strip())
            eliminar_referidos(id_referido)
        except ValueError:
            print("Error: El ID debe ser un número válido.")
    elif opcion == "5":
        exportar_datos()
    elif opcion == "6":
        try:
            id_referido = int(input("ID del referido: ").strip())
            nota = input("Nota: ").strip()
            agregar_nota(id_referido, nota)
        except ValueError:
            print("Error: El ID debe ser un número válido.")
    elif opcion == "7":
        try:
            id_referido = int(input("ID del referido: ").strip())
            consultar_nota(id_referido)
        except ValueError:
            print("Error: El ID debe ser un número válido.")
    elif opcion == "8":
        print("Saliendo del programa...")
        break
    else:
        print("Opción no válida. Inténtelo de nuevo.")
if __name__ == "__main__":
    menu()

ventana = tk.Tk()
ventana.title("Gestor de referidos")
label_busqueda = tk.Label(ventana, text="Buscar Referido por Nombre") # Updated capitalization for clarity

label_busqueda.grid(row=0, column=0, pady=5, padx=5) # Add padding for UI consistency
entry_busqueda = tk.Entry(ventana, width=30)
entry_busqueda.grid(row=0, column=1, pady=5, padx=5)
boton_buscar = tk.Button(ventana, text="Buscar", command=lambda: buscar_referidos_por_nombre(entry_busqueda.get()))
boton_buscar.grid(row=0, column=2, pady=5, padx=5)

def mostrar_resultados(resultados):
    texto_resultados = tk.Text(ventana, width=40, height=10)
    texto_resultados.grid(row=1, column=0, columnspan=3, pady=5, padx=5)
    texto_resultados.insert(tk.END, "Resultados de la búsqueda:\n")
    for resultado in resultados:
        texto_resultados.insert(tk.END, f"ID: {resultado[0]}, Nombre: {resultado[1]}, Correo: {resultado[2]}, Teléfono: {resultado[3]}\n")
    texto_resultados.configure(state='disabled') # Make results readonly



def buscar_referidos_por_nombre(nombre): # Updated function name for clarity
    try:
        cursor.execute("SELECT * FROM referido WHERE LOWER(nombre) LIKE LOWER(?);", ("%"+nombre+"%",))
        resultados = cursor.fetchall()
        if not resultados:
            messagebox.showinfo("Información", "No se encontraron resultados.")
            return
        mostrar_resultados(resultados)
    except sqlite3.Error as e:
        messagebox.showerror("Error", f"Error al buscar referidos: {e}")


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SECRET_KEY'] = 'Wilmer84699822'
db = SQLAlchemy(app)

class Usuario(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    correo = db.Column(db.String(100), nullable=False, unique=True)
    contraseña = db.Column(db.String(100), nullable=False)

class Referido(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    correo = db.Column(db.String(100), nullable=False, unique=True)
    telefono = db.Column(db.String(100), nullable=False)

def es_autenticado():
    return "usuario_id" in session

@app.route("/")
def index():
    if es_autenticado():
        return render_template("index.html")
    else:
        return redirect(url_for("login"))

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        correo = request.form["correo"]
        contraseña = request.form["contraseña"]
        usuario = Usuario.query.filter_by(correo=correo).first()
        if usuario and check_password_hash(usuario.contraseña, contraseña):
            session["usuario_id"] = usuario.id
            return redirect(url_for("index"))
        else:
            flash("Credenciales incorrectas", "danger")
    return render_template("login.html")

if __name__ == "__main__":
    app.run(debug=True)

def es_autenticado():
    return "usuario_id" in session
@app.route("/")
def index():
    if es_autenticado():
        return render_template("index.html")
    else:
        return redirect(url_for("login"))
@app.route("/logout")
def logout():
    session.clear()
    from flask import Flask, render_template, redirect, url_for, session, request, flash
    from flask_sqlalchemy import SQLAlchemy
    from werkzeug.security import generate_password_hash, check_password_hash
    
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
    app.config['SECRET_KEY'] = 'Wilmer84699822'
    db = SQLAlchemy(app)
    
    class Usuario(db.Model):
        id = db.Column(db.Integer, primary_key=True)
        nombre = db.Column(db.String(100), nullable=False)
        correo = db.Column(db.String(100), nullable=False, unique=True)
        contraseña = db.Column(db.String(100), nullable=False)
    
    class Referido(db.Model):
        id = db.Column(db.Integer, primary_key=True)
        nombre = db.Column(db.String(100), nullable=False)
        correo = db.Column(db.String(100), nullable=False, unique=True)
        telefono = db.Column(db.String(100), nullable=False)
    
    def es_autenticado():
        return "usuario_id" in session
    
    @app.route("/")
    def index():
        if es_autenticado():
            return render_template("index.html")
        else:
            return redirect(url_for("login"))
    
    @app.route("/logout")
    def logout():
        session.clear()
        return redirect(url_for("login"))
    
    @app.route("/login", methods=["GET", "POST"])
    def login():
        if request.method == "POST":
            correo = request.form["correo"]
            contraseña = request.form["contraseña"]
            usuario = Usuario.query.filter_by(correo=correo).first()
            if usuario and check_password_hash(usuario.contraseña, contraseña):
                session["usuario_id"] = usuario.id
                return redirect(url_for("index"))
            else:
                flash("Credenciales incorrectas", "danger")
        return render_template("login.html")
    
    @app.route("/buscar_referidos", methods=["GET", "POST"])
    def buscar_referidos():
        referidos = []
        if request.method == "POST":
            nombre_o_correo = request.form["nombre_o_correo"]
            referidos = Referido.query.filter(
                (Referido.nombre.ilike(f"%{nombre_o_correo}%")) |
                (Referido.correo.ilike(f"%{nombre_o_correo}%"))
            ).all()
        return render_template("buscar_referidos.html", referidos=referidos)
    
    if __name__ == "__main__":
        app.run(debug=True)
class Usuario(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    correo = db.Column(db.String(100), nullable=False, unique=True)
    contraseña = db.Column(db.String(100), nullable=False)

class Referido(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    correo = db.Column(db.String(100), nullable=False, unique=True)
    telefono = db.Column(db.String(100), nullable=False)

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        correo = request.form["correo"]
        contraseña = request.form["contraseña"]
        usuario = Usuario.query.filter_by(correo=correo).first()
    if usuario and check_password_hash(usuario.contraseña, contraseña):
        session["usuario_id"] = usuario.id
        return redirect(url_for("index"))
    else:
        flash("Credenciales incorrectas", "danger")

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

@app.route("/")
def index():
    if "usuario_id" in session:
        return render_template("index.html")
    else:
        return redirect(url_for("login"))

@app.route("/referidos", methods=["GET", "POST"])
def gestionar_referidos():
    if "usuario_id" in session:
        if request.method == "POST":
            nombre = request.form["nombre"]
            correo = request.form["correo"]
            telefono = request.form["telefono"]
            if not nombre or not correo or not telefono:
                flash("Todos los campos son obligatorios", "danger")
            else:
                nuevo_referido = Referido(nombre=nombre, correo=correo, telefono=telefono)
                db.session.add(nuevo_referido)
                db.session.commit()
                flash("Referido agregado exitosamente", "success")
        todos_referidos = Referido.query.all()
        return render_template("plantilla_referidos.html", referidos=todos_referidos)
    else:
        return redirect(url_for("login"))

@app.route("/referidos/<int:id>/editar", methods=["GET", "POST"])
def editar_referido(id):
    if "usuario_id" in session:
        referido = Referido.query.get(id)
        if request.method == "POST":
            nombre = request.form["nombre"]
            correo = request.form["correo"]
            telefono = request.form["telefono"]
            if not nombre or not correo or not telefono:
                flash("Todos los campos son obligatorios", "danger")
            else:
                referido.nombre = nombre
                referido.correo = correo
                referido.telefono = telefono
                db.session.commit()
                flash("Referido actualizado exitosamente", "success")
        return render_template("plantilla_editar_referido.html", referido=referido)
    else:
        return redirect(url_for("login"))

if __name__ == "__main__":
    app.run(debug=True)

@app.route("/referidos/buscar", methods=["GET", "POST"])
def buscar_referidos():
    if request.method == "POST":
        nombre_o_correo = request.form["nombre_o_correo"]
        referidos = Referido.query.filter(
            (Referido.nombre.like(f"%{nombre_o_correo}%")) |
            (Referido.correo.like(f"%{nombre_o_correo}%"))
        ).all()
        return render_template("referidos.html", referidos=referidos)
    return render_template("buscar_referidos.html")