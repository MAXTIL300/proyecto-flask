
from flask import Flask, flash, redirect, url_for, render_template, request, url_for, session
from flask_login import login_user, logout_user, current_user, login_required, UserMixin
from flask_login import LoginManager
# from login import login, logout, register, home, profile
import MySQLdb.cursors
import MySQLdb.cursors
import re
import hashlib
from datetime import datetime
from flask_mysqldb import MySQL
import requests
from werkzeug.utils import secure_filename
import os


app = Flask(__name__)

# clave secreta para los mensajes
app.secret_key = 'clave_secreta'
# CONEXION db


app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'proyectoflask'

mysql = MySQL(app)

# Configuración de Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'logined'


# usuario y contrasena pagina
# root
# 1234


@login_manager.user_loader
def load_user(user_id):
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM accounts WHERE id = %s', (user_id,))
    user = cursor.fetchone()
    cursor.close()
    if user:
        return user
    return None


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


# Registrando las rutas del login
# app.register_blueprint(login)
# folders imagenes
# UPLOAD_FOLDER = 'static/uploads'
UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# context procesors


@app.context_processor
def date_now():
    return {
        'now': datetime.utcnow()
    }


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


# end points


@app.route("/")
def index():

    edad = 120
    personas = ['victor', 'paco', f'rancisco']

    return render_template('index.html',
                           edad=edad,
                           personas=personas,
                           dato1="valor",
                           dato2="valor2",
                           lista="uno",
                           lista2=["uno", "dos", "tres"]
                           )


@app.route("/informacion")
@app.route("/informacion/<nombre>/<apellidos>")
def informacion(nombre="None", apellidos="None"):

    texto = ""
    if nombre != "None":
        texto = f"Bienvenido, {nombre} {apellidos}"

    return render_template("informacion.html", texto=texto)


@app.route("/contacto", methods=['GET', 'POST'])
def contacto():
    if request.method == 'POST':
        nombre = request.form['nombre']
        email = request.form['email']
        mensaje = request.form['mensaje']
        archivo = request.files['archivo']

        # Guardar el archivo adjunto
        if archivo and allowed_file(archivo.filename):
            filename = secure_filename(archivo.filename)
            archivo.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        else:
            filename = None

        # Guardar la información en la base de datos
        cursor = mysql.connection.cursor()
        cursor.execute(
            "INSERT INTO mensajes (nombre, email, mensaje, archivo) VALUES (%s, %s, %s, %s)",
            (nombre, email, mensaje, filename)
        )
        mysql.connection.commit()
        cursor.close()

        flash(
            "¡Gracias por tu mensaje! Nos pondremos en contacto contigo pronto.", "success")
        return redirect(url_for('index'))

    return render_template('contacto.html')


# @app.route("/lenguajes-de-programacion")
# def lenguajes():
#     return render_template("lenguajes.html")
# ****************************APIS***********************************


@app.route("/api")
def apis():
    # Realizar la solicitud a la URL de Google
    url = "https://httpbin.org/get"
    response = requests.get(url)

    if response.status_code == 200:
        content = response.content
    else:
        content = "Error al realizar la solicitud: {}".format(
            response.status_code)

    # Renderizar el template con el contenido de la solicitud
    return content

# ******************************************************************************
# crear coches


# @app.route('/crear-coche', methods=['GET', 'POST'])
# def crear_coche():
#     if request.method == 'POST':
#         marca = request.form['marca']
#         modelo = request.form['modelo']
#         precio = request.form['precio']
#         ciudad = request.form['ciudad']

#         # Manejar la carga de la imagen
#         if 'imagen' not in request.files:
#             flash('No se ha seleccionado ningún archivo.')
#             return redirect(request.url)
#         imagen = request.files['imagen']
#         if imagen.filename == '':
#             flash('No se ha seleccionado ningún archivo.')
#             return redirect(request.url)
#         if imagen and allowed_file(imagen.filename):
#             filename = secure_filename(imagen.filename)
#             imagen.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

#         cursor = mysql.connection.cursor()
#         cursor.execute(
#             "INSERT INTO coches VALUES(NULL,%s,%s,%s,%s,%s)", (marca, modelo, precio, ciudad, filename))
#         cursor.connection.commit()
#         flash("Coche creado con éxito")
#         return redirect(url_for('index'))

#     return render_template('crear_coche.html')

# *****************************************************************************************************
#                                    CREAR UN COCHE                                                 *
#                                                                                                     *
# *****************************************************************************************************


@app.route('/crear-camiseta', methods=['GET', 'POST'])
def crear_coche():
    if 'loggedin' not in session:
        return redirect(url_for('logined'))

    if request.method == 'POST':
        marca = request.form['marca']
        modelo = request.form['modelo']
        precio = request.form['precio']
        precio = float(precio) * 1000
        Talla = request.form['Talla']
        # Convertir el precio a formato de pesos colombianos
        precio_pesos_colombianos = "{:,.0f}".format(precio) + ' COP'
        # Obtener la imagen

        imagen = request.files['imagen']

        # Guardar la imagen en el servidor

        ruta_destino = os.path.join(
            app.config['UPLOAD_FOLDER'], imagen.filename)

        imagen.save(ruta_destino)
        cursor = mysql.connection.cursor()
        cursor.execute(f"INSERT INTO coches VALUES (NULL, %s, %s, %s, %s, %s)",
                       (marca, modelo, precio_pesos_colombianos, Talla, imagen.filename))
        cursor.connection.commit()
        cursor.close()
        flash("Camiseta creada con éxito")
        return redirect(url_for('index'))
    return render_template('crear_camiseta.html')
# *****************************************************************************************************
#                                     Tienda                                            *
#                                                                                                     *
# *****************************************************************************************************


@app.route('/Tienda')
def Tienda():
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM coches ORDER BY id DESC")
    coches = cursor.fetchall()

    cursor.close()
    # Formatear el precio en pesos colombianos
    coches_formateados = []
    for coche in coches:
        precio_pesos_colombianos = "{:,.0f} COP".format(coche[3] * 1000)
        coche_formateado = list(coche)
        # Reemplazar el precio original con el precio formateado
        coche_formateado[3] = precio_pesos_colombianos
        coches_formateados.append(tuple(coche_formateado))

    return render_template('Tienda.html', coches=coches_formateados)
# *****************************************************************************************************
#                                     # detalles camiseta                                             *
#                                                                                                     *
# *****************************************************************************************************


@app.route('/coche/<coche_id>')
def coche(coche_id):
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM coches WHERE id = %s", (coche_id,))
    coche = cursor.fetchall()
    cursor.close()

    # Formatear el precio en pesos colombianos
    precio_pesos_colombianos = "{:,.0f} COP".format(coche[0][3] * 1000)
    coche_formateado = list(coche[0])
    # Reemplazar el precio original con el precio formateado
    coche_formateado[3] = precio_pesos_colombianos
    coche = tuple(coche_formateado)

    return render_template('coches.html', coche=coche)


# *****************************************************************************************************
#                                     # eliminar camiseta                                           *
#                                                                                                     *
# *****************************************************************************************************


@app.route('/borrar-coche/<coche_id>')
def borrar_coche(coche_id):
    cursor = mysql.connection.cursor()
    cursor.execute(f"DELETE FROM coches WHERE id = %s", (coche_id,))
    mysql.connection.commit()

    flash("Articulo borrado con exito")
    return redirect(url_for('Tienda'))


# *****************************************************************************************************
#                                     # modificar camiseta                                              *
#                                                                                                     *
# *****************************************************************************************************

@app.route('/editar-coche/<coche_id>', methods=['GET', 'POST'])
def editar_coche(coche_id):
    if request.method == 'POST':
        marca = request.form['marca']
        modelo = request.form['modelo']
        precio = request.form['precio']
        Talla = request.form['Talla']

        # Obtener la imagen cargada
        imagen = request.files['imagen']
        # Guardar la imagen en el directorio de imágenes
        imagen.save(os.path.join(app.config['UPLOAD_FOLDER'], imagen.filename))

        # Formatear el precio para almacenarlo en la base de datos
        precio_decimal = float(precio.replace(',', '')) / 1000

        cursor = mysql.connection.cursor()
        cursor.execute(
            "UPDATE coches SET marca = %s, modelo = %s, precio = %s, Talla = %s, imagen = %s WHERE id = %s",
            (marca, modelo, precio_decimal, Talla, imagen.filename, coche_id)
        )
        mysql.connection.commit()
        cursor.close()

        flash("Camiseta modificada con éxito")
        return redirect(url_for('Tienda'))

    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM coches WHERE id = %s", (coche_id,))
    coche = cursor.fetchone()
    cursor.close()

    # Formatear el precio en pesos colombianos para mostrarlo en el formulario
    precio_pesos_colombianos = "{:,.2f} COP".format(coche[3] * 1000)

    return render_template('crear_camiseta.html', coche=coche, precio=precio_pesos_colombianos)


# *****************************************************************************************************
#                                     # LOGIN                                             *
#                                                                                                     *
# *****************************************************************************************************
@app.route('/pythonlogin/', methods=['GET', 'POST'])
def logined():
    msg = ''

    # Comprueba si existen las solicitudes POST de "username" y "password" (formulario enviado por el usuario)
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        # Crea variables para acceder fácilmente
        username = request.form['username']
        password = request.form['password']

        # Recupera la contraseña hasheada
        hash_password = hashlib.sha1(
            (password + app.secret_key).encode()).hexdigest()

        # Comprueba si la cuenta existe usando MySQL
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute(
            'SELECT * FROM proyectoflask.accounts WHERE username = %s AND password = %s', (username, hash_password,))

        # Recupera un registro y devuelve el resultado
        account = cursor.fetchone()

        # Si la cuenta existe en la tabla de cuentas en nuestra base de datos
        if account:
            # Crea datos de sesión, podemos acceder a estos datos en otras rutas
            session['loggedin'] = True
            session['id'] = account['id']
            session['username'] = account['username']
            # Redirige a la página de inicio
            return redirect(url_for('home'))
        else:
            # La cuenta no existe o el nombre de usuario/contraseña es incorrecto
            msg = '¡Nombre de usuario/contraseña incorrecto!'

    # Muestra el formulario de inicio de sesión con el mensaje (si hay alguno)
    return render_template('login.html', msg=msg)


@app.route('/pythonlogin/logout')
def logout():
    # Elimina los datos de la sesión, esto cerrará la sesión del usuario
    session.pop('loggedin', None)
    session.pop('id', None)
    session.pop('username', None)
    # Redirige a la página de inicio de sesión
    return redirect(url_for('logined'))


@app.route('/pythonlogin/register', methods=['GET', 'POST'])
def register():
    # Mensaje de salida si algo sale mal...
    msg = ''

    # Comprueba si existen las solicitudes POST de "username", "password" y "email" (formulario enviado por el usuario)
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form and 'email' in request.form:
        # Crea variables para acceder fácilmente
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']

        # Comprueba si la cuenta ya existe
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute(
            'SELECT * FROM proyectoflask.accounts WHERE username = %s', (username,))
        account = cursor.fetchone()

        if account:
            msg = '¡La cuenta ya existe!'
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            msg = '¡Dirección de correo electrónico no válida!'
        elif not re.match(r'[A-Za-z0-9]+', username):
            msg = '¡El nombre de usuario debe contener solo caracteres y números!'
        elif not username or not password or not email:
            msg = '¡Por favor, complete el formulario!'
        else:
            # Hashea la contraseña
            hash_password = hashlib.sha1(
                (password + app.secret_key).encode()).hexdigest()
            # Inserta la nueva cuenta en la base de datos
            cursor.execute('INSERT INTO proyectoflask.accounts VALUES (NULL, %s, %s, %s)',
                           (username, hash_password, email,))
            mysql.connection.commit()
            msg = '¡Te has registrado correctamente!'

    # Muestra el formulario de registro con el mensaje (si hay alguno)
    return render_template('register.html', msg=msg)


@app.route('/pythonlogin/home')
def home():
    # Check if the user is logged in
    if 'loggedin' in session:
        # User is loggedin show them the home page
        return render_template('home.html', username=session['username'])
    # User is not loggedin redirect to login page
    return redirect(url_for('login'))


# http://localhost:5000/pythinlogin/profile - this will be the profile page, only accessible for logged in users
@app.route('/pythonlogin/profile')
def profile():
    # Check if the user is logged in
    if 'loggedin' in session:
        # We need all the account info for the user so we can display it on the profile page
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM accounts WHERE id = %s',
                       (session['id'],))
        account = cursor.fetchone()
        # Show the profile page with account info
        return render_template('profile.html', account=account)
    # User is not logged in redirect to login page
    return redirect(url_for('login'))


if __name__ == "__main__":
    app.run(debug=True)
