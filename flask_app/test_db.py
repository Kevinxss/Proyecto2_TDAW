from conexion import obtener_conexion

conexion = obtener_conexion()

if conexion:
    print("✅ Conexión exitosa a MySQL")
    conexion.close()
else:
    print(" No se pudo conectar con la base de datos")
