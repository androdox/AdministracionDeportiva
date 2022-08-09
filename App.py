from urllib import request
import cx_Oracle
from flask import Flask, render_template, request, redirect, url_for, flash
import datetime
import config
import smtplib


app = Flask(__name__)

# conexion con oracle
connection = None
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
    print(rows)

    #oracle = oracle(app)
    for row in rows:
        print(row)
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
    print(sql)
    cursor.execute('SELECT  e.nomempleado nombre, e.apellempleado nombre, c.descargo FROM empleado e, cargo c, empleado_cargo ec where ec.idcargo = c.idcargo and ec.codempleado = e.codempleado')
    data = cursor.fetchall()
    cursor.execute('SELECT * FROM cargo')
    cargos = cursor.fetchall()
    print(data)
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
        print(sql)
        cursor.execute(sql, [cod])
        data = cursor.fetchall()
        connection.commit()
        print(data)
        if (len(data) > 0):
            sqlinsert = """INSERT INTO EMPLEADO_CARGO (IDCARGO, CODEMPLEADO, CODESPACIO, FECHACARGO, FECHAFINCAR) VALUES  (
            :cargo, :empleado, :espacio, sysdate, sysdate)"""
            cursor = connection.cursor()
            cursor.execute(sqlinsert, [data[0][4], data[0][5], data[0][6]])
            cursor.execute(sql, [cod])
            data = cursor.fetchall()
            connection.commit()
            return render_template('registroauxiliar.html', datos=data[0])
        else:
            flash('Codigo auxiliar incorrecto')
            return redirect(url_for('loginauxiliar'))


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
