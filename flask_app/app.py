from flask import Flask, request, jsonify, session
from conexion import obtener_conexion
from flask_cors import CORS #para peticiones externas
from datetime import datetime
from decimal import Decimal
from flask import Flask, render_template
from flask import Flask, render_template, request, jsonify, redirect, url_for, session
import os
from flask import Blueprint, send_file
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
import io

app = Flask(__name__)
app.secret_key= os.urandom(24)
origins = [
    "http://127.0.0.1:5500",  # Para VS Code Live Server
    "http://localhost",        

]
CORS(app, origins=origins, supports_credentials=True)


@app.route("/register", methods=["POST"])
def register():
    data = request.get_json()
    usuario = data.get("usuario")
    password = data.get("password") 
    telefono = data.get("telefono")

    feche_actual = datetime.now()
    saldo_inicial = 0

    if not usuario or not password:
        return jsonify({"exito": False, "mensaje": "Datos incompletos"}), 400

    conexion = None
    try:
        conexion = obtener_conexion()
        if not conexion:
            return jsonify({"exito": False, "mensaje": "Error al conectar con la bd"})
        
        cursor = conexion.cursor(dictionary=True)

        # 1. Verificar si el usuario ya existe
        sql_check = "SELECT * FROM usuarios WHERE nombre = %s"
        
      
        cursor.execute(sql_check, (usuario,)) 
        
        if cursor.fetchone():
            return jsonify({"exito": False, "mensaje": "El nombre de usuario ya existe"})

        # 2. Si no existe, insertarlo
        sql_insert = """
            INSERT INTO usuarios (nombre, password, telefono, fecha_registro, saldo) 
            VALUES (%s, %s, %s, %s, %s)
        """
        parametros =(usuario, password, telefono, feche_actual, saldo_inicial)
        cursor.execute(sql_insert, parametros) 
        
        conexion.commit() 

        return jsonify({"exito": True, "mensaje": "Usuario registrado con éxito"})

    except Exception as e:
        if conexion:
            conexion.rollback() 
        print(f"Error durante el registro: {e}") 
        return jsonify({"exito": False, "mensaje": "Error en el servidor"}), 500
    finally:
        if conexion:
            conexion.close()

@app.route("/login", methods=["POST"])
def login():
    data =request.get_json()
    usuario = data.get("usuario")
    password = data.get("password")

    conexion = obtener_conexion()
    if not conexion:
        return jsonify({"exito": False, "mensaje": "Error al conectar con la bd"})
    
    cursor = conexion.cursor(dictionary=True)
    cursor.execute("SELECT * FROM usuarios where nombre = %s and password =%s", (usuario, password))
    resultado = cursor.fetchone()
    conexion.close()

    if resultado: 
        session.clear()

        session['user_id']= resultado['id_usuario']
        session['user_nombre']= resultado['nombre']

        return jsonify({"exito": True, "usuaario": resultado['nombre']})

    if resultado:
        return jsonify({"exito": True, "usuario": usuario})
    else:
        return jsonify({"exito": False})

# app.py

@app.route("/api/perfil", methods =["GET"])
def get_perfil():
    
    if 'user_id' not in session:
        return jsonify({"exito": False, "mensaje": "No autorizado. Inicia sesión."}), 401
    
    user_id_actual = session['user_id']
    conexion = None
    try:
        conexion = obtener_conexion()
        if not conexion:
            return jsonify({"exito":False, "mensaje":"error al conectar a la base de datos"}), 500
            
        cursor = conexion.cursor(dictionary=True)
        
        sql_query = "SELECT id_usuario, nombre, telefono, saldo from usuarios where id_usuario = %s"
        
        cursor.execute(sql_query, (user_id_actual,))
        usuario = cursor.fetchone()

        if not usuario:
            session.clear() 
            return jsonify({"exito": False, "mensaje": "Usuario no encontrado"}), 404
            
        return jsonify({"exito": True, "datos_usuario":usuario})
    
    except Exception as e:
        # ¡El error real aparecerá en tu terminal de Flask!
        print(f"Error en api/perfil GET:{e}" )
        return jsonify({"exito": False, "mensaje": "Error en el servidor"}), 500
    finally:
        if conexion:
            conexion.close()
@app.route("/logout", methods=["POST"])
def logout():
    session.clear() # Borra todos los datos de la sesión
    return jsonify({"exito": True, "mensaje": "Sesión cerrada"})

@app.route("/api/perfil", methods=["PUT"]) # Usamos PUT para "Actualizar"
def update_perfil():
    # 1. Verificar si el usuario ha iniciado sesión
    if 'user_id' not in session:
        return jsonify({"exito": False, "mensaje": "No autorizado. Inicia sesión."}), 401
    
    user_id_actual = session['user_id']
    
    # 2. Obtener los nuevos datos del JSON que envió el JS
    data = request.get_json()
    nuevo_usuario = data.get("usuario")
    nuevo_telefono = data.get("telefono")

    if not nuevo_usuario or not nuevo_telefono:
        return jsonify({"exito": False, "mensaje": "Datos incompletos"}), 400

    conexion = None
    try:
        conexion = obtener_conexion()
        if not conexion:
            return jsonify({"exito": False, "mensaje": "Error al conectar con la bd"}), 500
        
        cursor = conexion.cursor(dictionary=True)
        
        # 3. (Opcional pero recomendado) Verificar que el *nuevo* nombre de usuario no esté ya en uso por OTRA persona
        sql_check = "SELECT * FROM usuarios WHERE nombre = %s AND id != %s"
        cursor.execute(sql_check, (nuevo_usuario, user_id_actual))
        if cursor.fetchone():
            return jsonify({"exito": False, "mensaje": "Ese nombre de usuario ya está en uso."})

        # 4. Ejecutar la actualización (UPDATE)
        sql_update = "UPDATE usuarios SET nombre = %s, telefono = %s WHERE id = %s"
        cursor.execute(sql_update, (nuevo_usuario, nuevo_telefono, user_id_actual))
        conexion.commit() # ¡Muy importante el commit para guardar!

        # 5. Actualizar el nombre en la sesión, por si cambió
        session['user_nombre'] = nuevo_usuario

        return jsonify({"exito": True, "mensaje": "Datos actualizados correctamente"})

    except Exception as e:
        if conexion:
            conexion.rollback()
        print(f"Error en /api/perfil PUT: {e}")
        return jsonify({"exito": False, "mensaje": "Error en el servidor"}), 500
    finally:
        if conexion:
            conexion.close()

@app.route("/api/perfil", methods=["DELETE"]) # Usamos el método DELETE
def delete_perfil():
    # 1. Verificar si el usuario ha iniciado sesión
    if 'user_id' not in session:
        return jsonify({"exito": False, "mensaje": "No autorizado"}), 401
    
    user_id_actual = session['user_id']
    conexion = None

    try:
        conexion = obtener_conexion()
        if not conexion:
            return jsonify({"exito": False, "mensaje": "Error al conectar con la bd"}), 500
        
        cursor = conexion.cursor() 
        
        # 2. Ejecutar el DELETE
        sql_delete = "DELETE FROM usuarios WHERE id = %s"
        cursor.execute(sql_delete, (user_id_actual,))
        conexion.commit() #

        # 3. Limpiar la sesión (hacer logout)
        session.clear() 

        return jsonify({"exito": True, "mensaje": "Cuenta eliminada correctamente"})

    except Exception as e:
        if conexion:
            conexion.rollback() # Revertir si algo falla
        print(f"Error en /api/perfil DELETE: {e}")
        return jsonify({"exito": False, "mensaje": "Error en el servidor"}), 500
    finally:
        if conexion:
            conexion.close()

#Agregar a favoritos
@app.route("/agregar_favorito", methods=["POST"])
def agregar_favorito():
    if 'user_id' not in session:
        return jsonify({"exito": False, "mensaje": "No autorizado"}), 401

    user_id = session["user_id"]
    data = request.get_json()
    pokemon_id = data.get("id_pokemon")

    if not pokemon_id:
        return jsonify({"exito": False, "mensaje": "No se recibió id_pokemon"}), 400

    conexion = None
    try:
        conexion = obtener_conexion()
        cursor = conexion.cursor(dictionary=True)
        
        
        sql_check = "SELECT * FROM favoritos WHERE id_usuario = %s AND id_pokemon = %s"
        cursor.execute(sql_check, (user_id, pokemon_id))
        if cursor.fetchone():
            return jsonify({"exito": False, "mensaje": "Ya está en favoritos"})

        # Insertamos solo los campos que existen 
        sql_insert = "INSERT INTO favoritos (id_usuario, id_pokemon) VALUES (%s, %s)"
        cursor.execute(sql_insert, (user_id, pokemon_id))
        conexion.commit()
        
        return jsonify({"exito": True, "mensaje": "Agregado a favoritos"})

    except Exception as e:
        if conexion: conexion.rollback()
        print(f"Error en /agregar_favorito: {e}") # (Mejorado el print)
        return jsonify({"exito": False, "mensaje": "Error en el servidor"}), 500
    finally:
        if conexion: conexion.close()

#Agregar al carrito 
# app.py

@app.route("/agregar_carrito", methods=["POST"])
def agregar_carrito():
    if 'user_id' not in session:
        return jsonify({"exito": False, "mensaje": "No autorizado"}), 401
    
    user_id = session['user_id']
    data = request.get_json()
    pokemon_id = data.get("id_pokemon")
    cantidad = data.get('cantidad', 1)

    if not pokemon_id:
        return jsonify({"exito": False, "mensaje": "No recibido id_pokemon"}), 400
    
    conexion = None
    try:
        conexion = obtener_conexion()
        cursor = conexion.cursor(dictionary=True)

        sql_check ="SELECT * FROM carrito WHERE id_usuario = %s AND id_pokemon = %s"
        cursor.execute(sql_check,(user_id, pokemon_id))
        item_existente = cursor.fetchone()

        if item_existente:
            nueva_cantidad = item_existente['cantidad'] + cantidad 
            sql_update = "UPDATE carrito SET cantidad = %s WHERE id_carrito = %s"
            cursor.execute(sql_update, (nueva_cantidad, item_existente['id_carrito']))
        else:
           
            sql_insert = "INSERT INTO carrito (id_usuario, id_pokemon, cantidad) VALUES (%s, %s, %s)"
            cursor.execute(sql_insert, (user_id, pokemon_id, cantidad))
            
        conexion.commit()
        return jsonify({"exito": True, "mensaje": "Agregado al carrito"})

    except Exception as e:
        if conexion: conexion.rollback()
        print(f"Error en /agregar_carrito: {e}") 
        return jsonify({"exito": False, "mensaje": "Error en el servidor"}), 500
    finally:
        if conexion: conexion.close()

#compras 
@app.route("/comprar", methods=["POST"])
def comprar():
    if 'user_id' not in session:
        return jsonify({"exito": False, "mensaje": "No autorizado"}), 401
        
    user_id = session['user_id']
    data = request.get_json()
    pokemon_id = data.get('id_pokemon')
    cantidad = 1
    precio_js = data.get('precio') # Obtenemos el precio 

    
    if not pokemon_id:
        
        return jsonify({"exito": False, "mensaje": "No se recibió id_pokemon"}), 400
    
    if precio_js is None:
        
        return jsonify({"exito": False, "mensaje": "El JS no envió un 'precio'"}), 400
    
    
    
    conexion = None
    try: 
        precio_total = Decimal(str(precio_js))
        
        conexion = obtener_conexion()
        cursor = conexion.cursor(dictionary=True)

        sql_saldo = "SELECT saldo FROM usuarios WHERE id_usuario = %s"
        cursor.execute(sql_saldo, (user_id, ))
        usuario = cursor.fetchone()

        if not usuario:
            return jsonify({"exito": False, "mensaje": "Usuario no encontrado"}), 404
        
        saldo_actual = usuario['saldo']
        
        if saldo_actual < precio_total:
            return jsonify({"exito": False, "mensaje": f"Saldo insuficiente. Tienes ${saldo_actual}"})
        
        nuevo_saldo = saldo_actual - precio_total 

        sql_update_saldo = "UPDATE usuarios SET saldo = %s WHERE id_usuario = %s"
        cursor.execute(sql_update_saldo, (nuevo_saldo, user_id))

        
        sql_insert_compra = "INSERT INTO compras (id_usuario, total, fecha_compra) VALUES (%s, %s, %s)"
        cursor.execute(sql_insert_compra,(user_id, precio_total, datetime.now()))

        id_compra_nueva = cursor.lastrowid

        
        sql_insert_detalle = "INSERT INTO detalle_compra (id_compra, id_pokemon, cantidad, subtotal) VALUES (%s, %s, %s, %s)"
        cursor.execute(sql_insert_detalle, (id_compra_nueva, pokemon_id, cantidad, precio_total))

        conexion.commit()

        
        return jsonify({"exito": True, "mensaje": "Compra exitosa", "nuevo_saldo": nuevo_saldo})
    
    except Exception as e :
        if conexion: conexion.rollback()
        print(f"Error en /comprar: {e}") 
        return jsonify({"exito": False, "mensaje": "Error en el servidor"}), 500
    finally:
        if conexion: conexion.close()

@app.route("/api/favoritos", methods = ["GET"])
def get_favoritos():
    if 'user_id'  not in session:
        return jsonify({"exito": False, "mensaje":"No autorizado"}), 401
    
    user_id = session['user_id']
    conexion = None

    try:
        conexion = obtener_conexion()
        cursor = conexion.cursor(dictionary=True)

        sql = "SELECT id_pokemon From favoritos WHERE id_usuario = %s"
        cursor.execute(sql, (user_id, ))
        favoritos = cursor.fetchall() #obtenemos todos y mandamos en lista

        return jsonify({"exito": True, "favoritos":favoritos})
    
    except Exception as e:
        print(f"Error en /api/favorto",{e})
        return jsonify({"exito": False, "mensaje":"Error en el servidor"}), 500
    finally:
        if conexion: conexion.close()


@app.route("/api/favoritos/<int:pokemon_id>", methods = ["DELETE"])
def delete_favorito(pokemon_id):
    if 'user_id' not in session:
        return jsonify({"exito": False, "mensaje": "No autorizado"}), 401
    
    user_id = session['user_id']
    conexion = None

    try:
        conexion = obtener_conexion()
        cursor = conexion.cursor()

        sql = "DELETE FROM favoritos WHERE id_usuario = %s AND id_pokemon = %s"
        cursor.execute(sql, (user_id, pokemon_id))
        conexion.commit()

        if cursor.rowcount == 0:
            return jsonify({"exito": False, "mensaje": "favorito no encontrado"}) 

        return jsonify({"exito": True, "mensaje": "Eliminado de favoritos"})
    except Exception as e:
        print(f"Error en /api/favoritos DELETE: ", {e})
        return jsonify({"exito": False, "mensaje": "Error en el servidor"}), 500
    finally:
        if conexion: conexion.close()

@app.route("/api/carrito", methods = ["GET"])
def get_carrito():
    if 'user_id' not in session:
        return jsonify({"exito": False, "mensaje": "No autorizado"}), 401
    
    user_id = session['user_id']
    conexion = None

    try:
        conexion = obtener_conexion()
        cursor = conexion.cursor(dictionary=True)

        sql = "SELECT id_pokemon, cantidad from carrito where id_usuario = %s"
        cursor.execute(sql,(user_id, ))
        items = cursor.fetchall() 

        return jsonify({"exito": True, "items": items})
    except Exception as e:
        print(f"Error en /api/carrito GET:",{e})
        return jsonify({"exito": False, "mensaje": "Error en el servidor"}), 500
    finally:
        if conexion: conexion.close()

@app.route("/api/carrito/<int:pokemon_id>", methods = ["DELETE"])
def delete_item_carrito(pokemon_id):
    if 'user_id' not in session:
        return jsonify({"exito": False, "mensaje": "No autorizado"}), 401
    
    user_id = session['user_id']
    conexion = None

    try:
        conexion = obtener_conexion()
        cursor = conexion.cursor(dictionary=True)

        sql ="DELETE FROM carrtio where id_usuario = %s AND id_pokemon = %s"
        cursor.execute(sql, (user_id, pokemon_id))
        conexion.commit()

        if cursor.rowcount == 0:
            return jsonify({"exito": False, "mensaje": "item  no encontrado"})
        
        return jsonify({"exito": True, "mensaje": "eliminado del carrito"})
    except Exception as e:
        print(f"Error en /api/carrtio DELETE: ", {e})
        return jsonify({"exito": False, "mensaje": "Error en el servidor"}), 500
    finally: 
        if conexion: conexion.close()

#comprar todo el carrito
@app.route("/checkout", methods = ["POST"])
def checkout():
    if 'user_id' not in session:
        return jsonify({"exito": False, "mensaje": "No autorizado"}), 401
    
    user_id = session['user_id']
    Precio = 500

    conexion = None
    try:
        conexion = obtener_conexion()
        cursor = conexion.cursor(dictionary=True)

        sql_carrito = "SELECT id_pokemon, cantidad From carrito WHERE id_usuario = %s"
        cursor.execute(sql_carrito, (user_id, ))
        items_carritos = cursor.fetchall()

        if not items_carritos:
            return jsonify({"exito": False, "mensaje": "Tu carrito esta vacio"})
        
        precio_total = sum(item['cantidad'] * Precio for item in items_carritos)

        sql_saldo = "SELECT saldo From usuarios Where id_usuario =%s"
        cursor.execute(sql_saldo, (user_id, ))
        usuario = cursor.fetchone()
        saldo_acutual = usuario['saldo']

        #verificacion de saldo
        if saldo_acutual < precio_total:
            return jsonify({"exito": False, "mensaje": "Fondos insuficientes"})
        
        #Transacciones a mano xd
        #actualizamos el precio
        nuevo_saldo = saldo_acutual - precio_total
        sql_update_saldo ="UPDATE usuarios SET saldo = %s WHERE id_usuario = %s"
        cursor.execute(sql_update_saldo,(nuevo_saldo, user_id))

        #creamos registro
        sql_insert_compra = "INSERT INTO compras (id_usuario, total, fecha_compra) VALUES (%s, %s, %s)"
        cursor.execute(sql_insert_compra, (user_id, precio_total, datetime.now()))
        id_compra_nueva = cursor.lastrowid

        #mover los items
        sql_insert_detalle ="INSET INTO detalle_compra (id_compra, id_pokemon, cantidad, subtotal) VALUES (%s, %s, %s, %s, )"
        for i in items_carritos:
            subtotal_i = i['cantidad'] * Precio
            cursor.execute(sql_insert_detalle, (id_compra_nueva, i['id_pokemon'], i['cantidad'], subtotal_i))

        #borramos carrito
        sql_delete_carrito = "DELETE  FROM carrito WHERE id_usuario = %s"
        cursor.execute(sql_delete_carrito, (user_id,))


        conexion.commit()
        
        return jsonify({"exito": True, "mensaje": "¡Compra exitosa!", "nuevo_saldo": nuevo_saldo})

    except Exception as e:
        if conexion: conexion.rollback() 
        print(f"Error en /checkout: {e}")
        return jsonify({"exito": False, "mensaje": "Error en el servidor"}), 500
    finally:
        if conexion: conexion.close()

# ---------------------------------------------------------------
# RUTA PARA OBTENER EL HISTORIAL DE COMPRAS
# ---------------------------------------------------------------
@app.route("/api/compras", methods=["GET"])
def get_compras():
    if 'user_id' not in session:
        return jsonify({"exito": False, "mensaje": "No autorizado"}), 401
    
    user_id = session['user_id']
    conexion = None
    historial = {} 
    
    try:
        conexion = obtener_conexion()
        cursor = conexion.cursor(dictionary=True)
        
        sql = """
            SELECT 
                c.id_compra, c.total, c.fecha_compra,
                d.id_pokemon, d.cantidad, d.subtotal
            FROM compras c
            JOIN detalle_compra d ON c.id_compra = d.id_compra
            WHERE c.id_usuario = %s
            ORDER BY c.fecha_compra DESC
        """
        cursor.execute(sql, (user_id,))
        resultados = cursor.fetchall()
        
        
        for fila in resultados:
            id_compra = fila['id_compra']
            if id_compra not in historial:
                historial[id_compra] = {
                    "id_compra": id_compra,
                    "total": fila['total'],
                    "fecha_compra": fila['fecha_compra'].strftime('%Y-%m-%d %H:%M:%S'),
                    "detalles": [] # Una lista para sus items
                }
            
         
            historial[id_compra]['detalles'].append({
                "id_pokemon": fila['id_pokemon'],
                "cantidad": fila['cantidad'],
                "subtotal": fila['subtotal']
            })
            
        
        lista_historial = list(historial.values())
        
        return jsonify({"exito": True, "compras": lista_historial})
        
    except Exception as e:
        print(f"Error en /api/compras: {e}")
        return jsonify({"exito": False, "mensaje": "Error en el servidor"}), 500
    finally:
        if conexion: conexion.close()

######Agregar saldo
###################
###### Agregar saldo ######
@app.route("/api/saldo", methods=["POST"])
def agregar_saldo():
    if 'user_id' not in session:
        return jsonify({"exito": False, "mensaje": "No autorizado"}), 401

    data = request.get_json()
    monto = data.get("monto")

    if not monto or monto <= 0:
        return jsonify({"exito": False, "mensaje": "Monto inválido"}), 400

    user_id = session['user_id']
    conexion = None

    try:
        conexion = obtener_conexion()
        cursor = conexion.cursor(dictionary=True)

        # Actualizar saldo
        cursor.execute("UPDATE usuarios SET saldo = saldo + %s WHERE id_usuario = %s", (monto, user_id))
        conexion.commit()

        # Obtener nuevo saldo del usuario
        cursor.execute("SELECT saldo FROM usuarios WHERE id_usuario = %s", (user_id,))
        nuevo_saldo = cursor.fetchone()['saldo']

        return jsonify({
            "exito": True,
            "mensaje": "Saldo agregado correctamente",
            "nuevo_saldo": float(nuevo_saldo)
        })

    except Exception as e:
        print("Error en /api/saldo:", e)
        return jsonify({"exito": False, "mensaje": "Error en el servidor"}), 500

    finally:
        if conexion:
            conexion.close()
# app.py
from datetime import datetime 

@app.route("/api/comentarios", methods=["POST"])
def guardar_comentario():
    
    if 'user_id' not in session:
        return jsonify({"exito": False, "mensaje": "No autorizado, inicia sesión primero"}), 401

    data = request.get_json() or {} 
    
    
    id_usuario = session.get("user_id")
    usuario_nombre = session.get("user_nombre") 
    
   
    comentario = data.get("comentario")

    
    if not comentario:
        return jsonify({"exito": False, "mensaje": "El comentario no puede estar vacío."}), 400

    try:
        conexion = obtener_conexion()
        if not conexion:
            return jsonify({"exito": False, "mensaje": "Error al conectar con la BD"}), 500

        cursor = conexion.cursor(dictionary=True)
        
        
        sql = """
            INSERT INTO comentarios (id_usuario, usuario, comentario, fecha_realizado)
            VALUES (%s, %s, %s, NOW())
        """
        
       
        cursor.execute(sql, (id_usuario, usuario_nombre, comentario))
        conexion.commit()
        cursor.close()
        conexion.close()

        return jsonify({"exito": True, "mensaje": "Comentario guardado correctamente"}), 201

    except Exception as e:
        if conexion:
            try:
                conexion.rollback()
                conexion.close()
            except:
                pass
        
        print(f"Error en /api/comentarios: {e}") 
        return jsonify({"exito": False, "mensaje": "Error en el servidor"}), 500
@app.route("/api/ventas", methods=["GET"])
def get_ventas():
    
    conexion = None
    try:
        conexion = obtener_conexion()
        cursor = conexion.cursor(dictionary=True)
        
        sql_query = """
            SELECT 
                v.id_venta, 
                v.id_pokemon, 
                v.nombre_pokemon, 
                v.precio_venta,
                u.nombre AS nombre_vendedor 
            FROM ventas v
            JOIN usuarios u ON v.id_usuario = u.id_usuario
            WHERE v.id_usuario != %s -- (Opcional: para no ver tus propias ventas)
        """
        
        
        user_id = session.get('user_id', 0) 
        
        cursor.execute(sql_query, (user_id,))
        ventas = cursor.fetchall()
        
        return jsonify({"exito": True, "ventas": ventas})

    except Exception as e:
        print(f"Error en /api/ventas: {e}")
        return jsonify({"exito": False, "mensaje": "Error en el servidor"}), 500
    finally:
        if conexion: conexion.close()

#################
# ============================
# ADMINISTRADOR: MENU GENERAL
# ============================

###conexion

import mysql.connector


def obtener_conexion():
    return mysql.connector.connect(
        host="10.93.44.91",
        user="flaskuser",
        password="12345",
        database="pokemon"
    )

# Página de login admin
@app.route("/login_admin", methods=["GET"])
def login_admin_page():
    return render_template("login_admin.html")

# Verificación de acceso admin
# Verificación de acceso admin
@app.route("/login_admin", methods=["POST"])
def login_admin():
    data = request.get_json()
    usuario = data.get("usuario")
    contrasena = data.get("contrasena")

    conexion = obtener_conexion()
    cursor = conexion.cursor(dictionary=True)
    cursor.execute("SELECT * FROM usuarios WHERE nombre = %s AND password = %s", (usuario, contrasena))
    admin = cursor.fetchone()
    conexion.close()

    if admin and admin.get("es_admin") == 1:
        session["user_id"] = admin["id_usuario"]
        session["es_admin"] = True
        return jsonify({
            "exito": True,
            "mensaje": "Bienvenido administrador",
            "es_admin": True  
        })
    else:
        return jsonify({
            "exito": False,
            "mensaje": "No eres administrador o credenciales incorrectas",
            "es_admin": False
        })



# ====================================
# DASHBOARD ADMIN
# ====================================
@app.route("/admin_dashboard", methods=["GET"])
def admin_dashboard():
    if 'user_id' not in session or not session.get('es_admin', False):
        return redirect(url_for("login_admin_page"))
    return render_template("admin_dashboard.html")

#############
#########top#
#############

@app.route("/api/top_pokemones_compras")
def top_pokemones_compras():
    conexion = obtener_conexion()
    cursor = conexion.cursor(dictionary=True)
    cursor.execute("""
        SELECT d.id_pokemon, SUM(d.cantidad) AS total_compras
        FROM detalle_compra d
        GROUP BY d.id_pokemon
        ORDER BY total_compras DESC
        LIMIT 10
    """)
    datos = cursor.fetchall()
    conexion.close()
    return jsonify(datos)


@app.route("/api/top_usuarios_compras")
def top_usuarios_compras():
    conexion = obtener_conexion()
    cursor = conexion.cursor(dictionary=True)
    cursor.execute("""
        SELECT c.id_usuario, COUNT(c.id_compra) AS total_compras
        FROM compras c
        GROUP BY c.id_usuario
        ORDER BY total_compras DESC
        LIMIT 10
    """)
    datos = cursor.fetchall()
    conexion.close()
    return jsonify(datos)


@app.route("/api/top_pokemones_favoritos")
def top_pokemones_favoritos():
    conexion = obtener_conexion()
    cursor = conexion.cursor(dictionary=True)
    cursor.execute("""
        SELECT f.id_pokemon, COUNT(f.id_favorito) AS total_favoritos
        FROM favoritos f
        GROUP BY f.id_pokemon
        ORDER BY total_favoritos DESC
        LIMIT 10
    """)
    datos = cursor.fetchall()
    conexion.close()
    return jsonify(datos)

@app.route("/api/descargar_reporte_admin", methods=["GET"])
def descargar_reporte_admin():
    try:
        conexion = obtener_conexion()
        if conexion is None:
            return {"error": "No se pudo conectar a MySQL"}, 500

        cursor = conexion.cursor(dictionary=True)

        
        cursor.execute("""
            SELECT id_pokemon, SUM(cantidad) AS total_compras
            FROM detalle_compra
            GROUP BY id_pokemon
            ORDER BY total_compras DESC
            LIMIT 10
        """)
        top_pokemones = cursor.fetchall()

        
        cursor.execute("""
            SELECT id_usuario, COUNT(*) AS total_compras
            FROM compras
            GROUP BY id_usuario
            ORDER BY total_compras DESC
            LIMIT 10
        """)
        top_usuarios = cursor.fetchall()

        #Top 10 pokemones favoritos
        cursor.execute("""
            SELECT id_pokemon, COUNT(*) AS total_favoritos
            FROM favoritos
            GROUP BY id_pokemon
            ORDER BY total_favoritos DESC
            LIMIT 10
        """)
        top_favoritos = cursor.fetchall()

        cursor.close()
        conexion.close()

        # --------------------------
        # CREAR PDF EN MEMORIA
        # --------------------------
        buffer = io.BytesIO()
        pdf = canvas.Canvas(buffer, pagesize=letter)

        y = 750
        pdf.setFont("Helvetica-Bold", 16)
        pdf.drawString(50, y, "Reporte Administrador - Ventas y Favoritos")
        y -= 30

        #Pokemones comprados
        pdf.setFont("Helvetica-Bold", 14)
        pdf.drawString(50, y, "🔥 Top 10 Pokémon más comprados:")
        y -= 20
        pdf.setFont("Helvetica", 12)

        for i, item in enumerate(top_pokemones):
            pdf.drawString(50, y, f"{i+1}. Pokémon ID {item['id_pokemon']} - Compras: {item['total_compras']}")
            y -= 15

        y -= 20

        #Usuarios con más compras
        pdf.setFont("Helvetica-Bold", 14)
        pdf.drawString(50, y, "👥 Top 10 Usuarios con más compras:")
        y -= 20
        pdf.setFont("Helvetica", 12)

        for i, item in enumerate(top_usuarios):
            pdf.drawString(50, y, f"{i+1}. Usuario ID {item['id_usuario']} - Compras: {item['total_compras']}")
            y -= 15

        y -= 20

        # Pokemones favoritos
        pdf.setFont("Helvetica-Bold", 14)
        pdf.drawString(50, y, "⭐ Top 10 Pokémon más favoritos:")
        y -= 20
        pdf.setFont("Helvetica", 12)

        for i, item in enumerate(top_favoritos):
            pdf.drawString(50, y, f"{i+1}. Pokémon ID {item['id_pokemon']} - Favoritos: {item['total_favoritos']}")
            y -= 15

        pdf.save()
        buffer.seek(0)

        return send_file(
            buffer,
            as_attachment=True,
            download_name="reporte_admin.pdf",
            mimetype="application/pdf"
        )

    except Exception as e:
        print(" Error generando el PDF:", e)
        return {"error": "Error al generar el PDF"}, 500
# ---------------------------------------------------------------
# RUTA PARA PUBLICAR UNA VENTA (NUEVA)
# ---------------------------------------------------------------
@app.route("/api/vender", methods=["POST"])
def publicar_venta():
    # 1. Verificar si el usuario ha iniciado sesión
    if 'user_id' not in session:
        return jsonify({"exito": False, "mensaje": "No autorizado"}), 401
    
    # 2. Obtener el ID del vendedor (de la sesión)
    id_vendedor = session['user_id']
    
    # 3. Obtener los datos del Pokémon que envió el JS
    data = request.get_json()
    pokemon_id = data.get('id_pokemon')
    nombre_pokemon = data.get('nombre_pokemon')
    precio_js = data.get('precio') 

    if not pokemon_id or not nombre_pokemon or not precio_js:
        return jsonify({"exito": False, "mensaje": "Datos incompletos"}), 400

    conexion = None
    try:
        # 4. Convertir el precio a Decimal
        precio_venta = Decimal(str(precio_js))
        
        if precio_venta <= 0:
             return jsonify({"exito": False, "mensaje": "El precio debe ser mayor a 0"}), 400

        conexion = obtener_conexion()
        cursor = conexion.cursor()
        
        # 5. Insertar en la nueva tabla 'ventas'
        sql_insert = """
            INSERT INTO ventas (id_usuario, id_pokemon, nombre_pokemon, precio_venta, fecha_publicacion)
            VALUES (%s, %s, %s, %s, %s)
        """
        params = (id_vendedor, pokemon_id, nombre_pokemon, precio_venta, datetime.now())
        cursor.execute(sql_insert, params)
        conexion.commit()
        
        return jsonify({"exito": True, "mensaje": f"¡Has puesto a {nombre_pokemon} en venta!"}), 201

    except Exception as e:
        if conexion: conexion.rollback()
        print(f"Error en /api/vender: {e}")
        return jsonify({"exito": False, "mensaje": "Error en el servidor"}), 500
    finally:
        if conexion: conexion.close()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
