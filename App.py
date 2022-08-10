from urllib import request
import cx_Oracle
from flask import Flask, render_template, request, redirect, url_for, flash
import datetime
import config
import smtplib


app = Flask(__name__)

# conexion con oracle
connection = None
datosauxiliar = []
fecha = ''
programa = []
try:
    connection = cx_Oracle.connect(
        config.username,
        config.password,
        config.dsn,
        encoding=config.encoding)

    # imprime la version de la base de datos
    print("conectado", connection.version)
    cursor = connection.cursor()
    sentencia = cursor.execute("SELECT * FROM empleado")
    rows = cursor.fetchall()
    # print(rows)

    #oracle = oracle(app)

except cx_Oracle.Error as error:
    print(error)

finally:
    # release the connection
    if connection:
        print("cerrar conexion")
        # connection.close()

# configuracion de session
app.secret_key = 'mysecretkey'


@app.route('/')
def Index():
    cursor = connection.cursor()
    sql = 'SELECT  e.nomempleado ||" "|| e.apellempleado nombre, c.descargo FROM empleado e, cargo c, empleado_cargo ec where ec.idcargo = c.idcargo and ec.codempleado = e.codempleado;'
    # print(sql)
    cursor.execute('SELECT  e.nomempleado nombre, e.apellempleado nombre, c.descargo FROM empleado e, cargo c, empleado_cargo ec where ec.idcargo = c.idcargo and ec.codempleado = e.codempleado')
    data = cursor.fetchall()
    cursor.execute('SELECT * FROM cargo')
    cargos = cursor.fetchall()
    # print(data)
    return render_template('index.html', datos=data, cargos=cargos)


@app.route('/empleados', methods=['POST'])
def empleados():
    if request.method == 'POST':
        nombre = request.form['nombre']
        apellido = request.form['apellido']
        idcargo = request.form['cargos']
        cursor = connection.cursor()
        cursor.execute('INSERT INTO empleado(nombre, apellido, idcargo) VALUES (:nombre, :apellido, :idcargo )', [
                       nombre, apellido, idcargo])
        connection.commit()
        flash('Empleado agregado')
        return redirect(url_for('Index'))


@app.route('/loginauxiliar')
def loginauxiliar():
    return render_template('auxiliar.html')


@app.route('/auxiliar', methods=['POST'])
def auxiliar():
    if request.method == 'POST':
        cod = request.form['cod']
        sql = """select e.nomempleado nombre, e.apellempleado nombre, c.descargo cargo, ec.fechacargo, c.idcargo, e.codempleado, s.codespacio 
        FROM empleado e, cargo c, empleado_cargo ec, espacio s 
        where ec.idcargo = c.idcargo and ec.codempleado = e.codempleado and s.codespacio = ec.codespacio and c.descargo = \'Auxiliar\' and e.codempleado = :cod order by ec.fechacargo desc"""
        cursor = connection.cursor()

        cursor.execute(sql, [cod])
        data = cursor.fetchall()
        connection.commit()

        if (len(data) > 0):
            sqlinsert = """SELECT TO_CHAR
    (SYSDATE, \'MM-DD-YYYY HH24:MI:SS\') "NOW"
     FROM DUAL"""
            cursor = connection.cursor()
            cursor.execute(sqlinsert)
            fechatemp = cursor.fetchall()
            cursor.execute(sql, [cod])
            data = cursor.fetchall()
            global fecha
            fecha = fechatemp[0]
            print(fecha)
            global datosauxiliar
            datosauxiliar = data[0]
            print(datosauxiliar)
            connection.commit()
            return render_template('registroauxiliar.html', datos=data[0], fecha=fecha)
        else:
            flash('Codigo auxiliar incorrecto')
            return redirect(url_for('loginauxiliar'))


@app.route('/docente', methods=['GET'])
def docente():
    if request.method == 'GET':
        nombre = request.args.get('nom')
        apellido = request.args.get('apel')
        sql = """SELECT  e.nomempleado nombre, e.apellempleado nombre, c.descargo , s.nomespacio, e.codempleado
        FROM empleado e, cargo c, empleado_cargo ec, espacio s 
        where ec.idcargo = c.idcargo and ec.codempleado = e.codempleado and c.descargo = \'Docente\' 
        and lower(e.nomempleado) = lower(:nombre) and lower(e.APELLEMPLEADO) = lower(:apellido) and s.codespacio = ec.codespacio"""
        cursor = connection.cursor()
        cursor.execute(sql, [nombre, apellido])
        data = cursor.fetchall()
        if (len(data) > 0):
            docente = data[0]
            sqlpro = """select r.fechafin, r.fechaini, a.descactividad, d.nomdeporte, s.nomespacio, p.cupo 
            from responsable r, programacion p, actividad a, deporte d, espacio s 
            where r.codempleado = :empleado and r.consecprogra = p.consecprogra 
            and a.idactividad = p.idactividad and d.iddeporte = p.iddeporte and s.codespacio = p.codespacio"""
            cursor = connection.cursor()
            empleado = data[0][4]
            cursor.execute(sqlpro, [empleado])
            data = cursor.fetchall()
            print(data)
            if (len(data) > 0):
                programa = data[0]
            else:
                programa = None

        else:
            docente = None
            programa = None
        connection.commit()
        global datosauxiliar
        return render_template('registroauxiliar.html', datos=datosauxiliar, docente=docente, fecha=fecha, programa=programa)


@app.route('/eliminar/<idempleado>')
def eliminarEmpleado(idempleado):
    cursor = connection.cursor()
    cursor.execute(
        'DELETE FROM empleado WHERE idempleado = :idempleado', [idempleado])
    connection.commit()
    flash('Empleado eliminado')
    return redirect(url_for('Index'))


@app.route('/editar/<idempleado>')
def editarEmpleado(idempleado):
    cursor = connection.cursor()
    cursor.execute(
        'SELECT * FROM empleado WHERE idempleado = :idempleado', [idempleado])
    data = cursor.fetchall()
    cursor.execute('SELECT * FROM cargo')
    cargos = cursor.fetchall()
    return render_template('editarEmpleado.html', dato=data[0], cargos=cargos)


@app.route('/actualizarEmpleado/<idempleado>', methods=['POST'])
def actualizarEmpleado(idempleado):
    if request.method == 'POST':
        nombre = request.form['nombre']
        apellido = request.form['apellido']
        idcargo = request.form['cargos']
        cursor = connection.cursor()
        cursor.execute('UPDATE empleado SET nombre = :nombre, apellido = :apellido, idcargo = :idcargo WHERE idempleado = :idempleado', [
                       nombre, apellido, idcargo, idempleado])
        connection.commit()
        flash('Empleado actualizado')
        return redirect(url_for('Index'))


if __name__ == '__main__':
    app.run(port=3000, debug=True)
