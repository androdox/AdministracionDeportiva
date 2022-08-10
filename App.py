from urllib import request
import cx_Oracle
from flask import Flask, make_response, render_template, request, redirect, url_for, flash
import datetime
import config
import smtplib
import pdfkit


app = Flask(__name__)

# conexion con oracle
connection = None
datosauxiliar = []
fecha = ''
programa = []
docente = []
elemento = []
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
            global datosauxiliar
            datosauxiliar = data[0]
            connection.commit()
            return render_template('registroauxiliar.html', datos=data[0], fecha=fecha)
        else:
            flash('Codigo auxiliar incorrecto')
            return redirect(url_for('loginauxiliar'))


@app.route('/docente', methods=['GET'])
def docente():
    if request.method == 'GET':
        global docente
        global fecha
        global programa
        global elemento
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
            sqlpro = """select r.fechafin, r.fechaini, a.descactividad, d.nomdeporte, s.nomespacio, p.cupo, CASE
            WHEN r.fechafin >= sysdate AND r.fechaini <= sysdate THEN 'SI'
            Else 'NO'
            END AS tiempo, s.codespacio, p.CONSECPROGRA, r.CONSECRES
            from responsable r, programacion p, actividad a, deporte d, espacio s
            where r.codempleado = :empleado and r.consecprogra = p.consecprogra 
            and a.idactividad = p.idactividad and d.iddeporte = p.iddeporte and s.codespacio = p.codespacio"""
            cursor = connection.cursor()
            empleado = data[0][4]
            cursor.execute(sqlpro, [empleado])
            data = cursor.fetchall()
            if (len(data) > 0):
                programa = data[0]
                if (str(data[0][6]) == 'SI'):
                    sql = """select ed.consecelemento, te.desctipoelemento from elemendeportivo ed,  tipoelemento te 
                    where ed.idtipoelemento= te.idtipoelemento and ed.idestado = \'1\' and ed.codespacio = :espacio"""
                    cursor.execute(sql, [data[0][7]])
                    elemento = cursor.fetchall()
                    sql = """INSERT INTO asistirresponsable (CONSECPROGRA, CONSECRES, FECHAASISRES, HORAASISRES)
                    VALUES (:programa, :responsable, sysdate, sysdate)"""
                    cursor.execute(sql, [data[0][8], data[0][9]])
                else:
                    elemento = None
            else:
                programa = None
                elemento = None

        else:
            docente = None
            programa = None
            elemento = None
        connection.commit()
        global datosauxiliar
        return render_template('registroauxiliar.html', datos=datosauxiliar, docente=docente, fecha=fecha, programa=programa, elemento=elemento)

@app.route('/asignar/<dato>')
def asignar(dato):
    global docente
    global fecha
    global programa
    global elemento
    global datosauxiliar
    print(dato)
    cursor = connection.cursor()
    sql = """ select a.consecasisres from asistirresponsable a where a.CONSECPROGRA = :programa and a.CONSECRES = :responsable order by a.fechaasisres desc"""
    cursor.execute(sql, [programa[8], programa[9]])
    datos = cursor.fetchall()
    id = datos[0]
    sql = """INSERT INTO prestamo (CONSECPROGRA, CONSECRES, CONSECASISRES, CONSECELEMENTO) 
    VALUES (:programa, :responsabel, :id, :dato) """
    cursor.execute(sql, [programa[8], programa[9], id[0], dato])
    sql = """update elemendeportivo set idestado=\'2\' where  CONSECELEMENTO = :dato"""
    cursor.execute(sql,[dato])
    sql = """select ed.consecelemento, te.desctipoelemento from elemendeportivo ed,  tipoelemento te 
    where ed.idtipoelemento= te.idtipoelemento and ed.idestado = \'1\' and ed.codespacio = :espacio"""
                    
    cursor.execute(sql, [programa[7]])
    elemento = cursor.fetchall()
    connection.commit()
    return render_template('registroauxiliar.html', datos=datosauxiliar, docente=docente, fecha=fecha, programa=programa, elemento=elemento)

@app.route('/logindirdepor')
def logindirdepor():
    return render_template('logindirdepor.html')


@app.route('/dirdepor', methods=['POST'])
def dirdepor():
    if request.method == 'POST':
        cod = request.form['cod']
        sql = """SELECT E.NOMEMPLEADO "Nombre", E.APELLEMPLEADO "Apellido", ES.NOMESPACIO "Sede",
        E.FECHAREGISTRO "Fecha" FROM EMPLEADO E LEFT JOIN EMPLEADO_CARGO EC 
        ON E.CODEMPLEADO = EC.CODEMPLEADO LEFT JOIN ESPACIO ES 
        ON EC.CODESPACIO = ES.CODESPACIO WHERE ES.IDTIPOESPACIO = 2 AND EC.IDCARGO = 3
        AND E.CODEMPLEADO = :cod"""
        cursor = connection.cursor()
        print(sql)
        cursor.execute(sql, [cod])
        data = cursor.fetchall()
        connection.commit()
        print(data)
        if (len(data) > 0):
            cursor = connection.cursor()
            cursor.execute(sql, [cod])
            data = cursor.fetchall()
            connection.commit()
            return render_template('dirdepor.html', datos=data)
        else:
            flash('El código ingresado no corresponde a un Director Deportivo')
            return redirect(url_for('logindirdepor'))

@app.route('/rep_pasantes')
def rep_pasantes():
     
    res = render_template('rep_pasantes.html')
    responsestring = pdfkit.from_string(res, False)
    response = make_response(responsestring)
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = 'inline;filename=output.pdf'
    return response

@app.route('/rep_miembros')
def rep_miembros():
    
    cursor = connection.cursor()
    sql = """SELECT E.CONSEEQUIPO "Id", EM.NOMEMPLEADO ||' '|| EM.APELLEMPLEADO "Docente",
    D.NOMDEPORTE "Deporte" FROM EQUIPO E LEFT JOIN EMPLEADO EM 
    ON E.CODEMPLEADO = EM.CODEMPLEADO LEFT JOIN DEPORTE D 
    ON E.IDDEPORTE = D.IDDEPORTE ORDER BY E.CONSEEQUIPO ASC"""
    cursor.execute(sql)
    equipo = cursor.fetchall()
    sql = """SELECT DISTINCT ME.CONSEEQUIPO "Id Equipo", E.NOMESTU ||' '|| 
    E.APELESTU "Nombre", CASE WHEN (P.HOR_IDHORA-P.IDHORA) IS NOT NULL 
    THEN (P.HOR_IDHORA-P.IDHORA) ELSE 0 END "Horas" FROM ESTUDIANTE E 
    LEFT JOIN MIEMBROEQUIPO ME ON E.CODESTU = ME.CODESTU LEFT JOIN EQUIPO EQ
    ON ME.CONSEEQUIPO = EQ.CONSEEQUIPO LEFT JOIN ASISMIEMBROEQUIPO AME 
    ON AME.CONSEEQUIPO = EQ.CONSEEQUIPO LEFT JOIN PROGRAMACION P
    ON P.CONSECPROGRA = AME.CONSECPROGRA WHERE ME.CONSEEQUIPO IS NOT NULL 
    ORDER BY ME.CONSEEQUIPO ASC"""
    cursor.execute(sql)
    estudiante = cursor.fetchall()

    res = render_template('rep_miembros.html', equipo=equipo, estudiante=estudiante)
    responsestring = pdfkit.from_string(res, False)
    response = make_response(responsestring)
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = 'inline;filename=output.pdf'
    return response

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

