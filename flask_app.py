from flask import Flask, render_template, redirect, url_for, flash, session, request
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
# Configuración básica de la app Flask
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///Sqlitedatos.db'
app.config['SECRET_KEY'] = 'MI_CLAVE_SECRETA'  # Usa variables de entorno en producción

db = SQLAlchemy(app)


# Modelo de Usuario
class Usuario(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    correo = db.Column(db.String(100), nullable=False, unique=True)
    contraseña = db.Column(db.String(100), nullable=False)


# Modelo de Referido
class Referido(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    correo = db.Column(db.String(100), nullable=False, unique=True)
    telefono = db.Column(db.String(100), nullable=False)


# Modelo de Nota
class Nota(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    id_referido = db.Column(db.Integer, db.ForeignKey('referido.id'), nullable=False)
    texto = db.Column(db.Text, nullable=False)
    referido = db.relationship('Referido', backref=db.backref('notas', lazy=True))


# Función auxiliar para verificar autenticación
def es_autenticado():
    return "usuario_id" in session


# Ruta: Registro de usuarios
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        nombre = request.form["nombre"]
        correo = request.form["correo"]
        contraseña = generate_password_hash(request.form["contraseña"])
        nuevo_usuario = Usuario(nombre=nombre, correo=correo, contraseña=contraseña)
        try:
            db.session.add(nuevo_usuario)
            db.session.commit()
            flash("Usuario registrado exitosamente", "success")
            return redirect(url_for('login'))
        except:
            flash("El correo ya está registrado", "danger")
    return render_template('register.html')  # Crea esta plantilla


# Ruta: Inicio de sesión
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        correo = request.form["correo"]
        contraseña = request.form["contraseña"]
        usuario = Usuario.query.filter_by(correo=correo).first()
        if usuario and check_password_hash(usuario.contraseña, contraseña):
            session["usuario_id"] = usuario.id
            session["usuario_nombre"] = usuario.nombre
            flash("Inicio de sesión exitoso", "success")
            return redirect(url_for('index'))
        else:
            flash("Correo o contraseña incorrectos", "danger")
    return render_template('login.html')  # Crea esta plantilla


# Ruta: Cerrar sesión
@app.route('/logout')
def logout():
    session.clear()
    flash("Sesión cerrada", "info")
    return redirect(url_for('login'))


# Ruta: Página de inicio
@app.route('/')
def index():
    if es_autenticado():
        referidos = Referido.query.all()
        return render_template('index.html', referidos=referidos)  # Plantilla para listado de referidos
    else:
        return redirect(url_for('login'))


# Ruta: Crear un referido
@app.route('/referidos/nuevo', methods=['GET', 'POST'])
def agregar_referido():
    if es_autenticado():
        if request.method == 'POST':
            nombre = request.form["nombre"]
            correo = request.form["correo"]
            telefono = request.form["telefono"]
            nuevo_referido = Referido(nombre=nombre, correo=correo, telefono=telefono)
            try:
                db.session.add(nuevo_referido)
                db.session.commit()
                flash("Referido agregado correctamente", "success")
                return redirect(url_for('index'))
            except:
                flash("Error: El correo ya existe", "danger")
        return render_template('plantilla_agregar_referido.html')
    else:
        return redirect(url_for('login'))


# Ruta: Actualizar información del referido
@app.route('/referidos/<int:id>/editar', methods=['GET', 'POST'])
def editar_referido(id):
    if es_autenticado():
        referido = Referido.query.get_or_404(id)
        if request.method == 'POST':
            referido.nombre = request.form["nombre"]
            referido.correo = request.form["correo"]
            referido.telefono = request.form["telefono"]
            try:
                db.session.commit()
                flash("Referido actualizado correctamente", "success")
                return redirect(url_for('index'))
            except:
                flash("Error al actualizar el referido", "danger")
        return render_template('plantilla_editar_referido.html', referido=referido)
    else:
        return redirect(url_for('login'))


# Ruta: Eliminar referido
@app.route('/referidos/<int:id>/eliminar', methods=['POST'])
def eliminar_referido(id):
    if es_autenticado():
        referido = Referido.query.get_or_404(id)
        try:
            db.session.delete(referido)
            db.session.commit()
            flash("Referido eliminado correctamente", "success")
        except:
            flash("Error al eliminar el referido", "danger")
        return redirect(url_for('index'))
    else:
        return redirect(url_for('login'))


# Ruta: Añadir nota a un referido
@app.route('/referidos/<int:id>/nota', methods=['GET', 'POST'])
def agregar_nota(id):
    if es_autenticado():
        referido = Referido.query.get_or_404(id)
        if request.method == 'POST':
            texto = request.form["texto"]
            nueva_nota = Nota(id_referido=referido.id, texto=texto)
            db.session.add(nueva_nota)
            db.session.commit()
            flash("Nota añadida correctamente", "success")
            return redirect(url_for('index'))
        return render_template('nueva_nota.html', referido=referido)  # Plantilla para agregar notas
    else:
        return redirect(url_for('login'))


# Crear la base de datos al inicializar
@app.before_first_request
def crear_db():
    db.create_all()  # Crea las tablas si no existen


if __name__ == '__main__':
    app.run(debug=True)