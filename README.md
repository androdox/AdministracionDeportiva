# _Sistema de gestion de unidad deportiva de la Universidad Distrital_
## Creadores

- Nicolas Andrade Perdomo
- Sebastian Solano Villada
- Luis Felipe Corredor Espinosa

Este es un proyecto aprendizaje desarrollado durante la materia de Bases de datos II, con el se pretende gestionar la unidad deportiva, los elementos, personal, estudiantes, designaciones y tener un control sobre las actividades que realizan todas las personas con vinculo con unidad deportiva de la universidad.

## Tecnologias utilizadas:

- Flask (framework de desarrollo web con Python)
- Bootstrap (framework de frontend)
- Oracle Database (21c Express Edition)

## Instalación:

Para ejecutar el programa se debe tener instalado python, ademas de ciertas librerias instaladas, antes de instalarlas es recomentable crear un ambiente virtual de python en donde se almacenaran las librerias necesarias para ejecutar el programa. Las siguentes son las instrucciones para el sistema operativo Windows.

Para crear el ambiente virtual 
```sh
python -m venv nombreDelEntorno
```
Para activar el entorno virtual entramos al propmt

```sh
nombreDelEntorno\Scripts\activate
```

Para ejecutar el servidor ejecutamos el archivo app.py
```sh
python app.py
```
### Base de datos:

Para crear la base de datos, en la carpeta llamada scripts-db se encuentra el scrip llamado scriptModulo Para ejecutarlo desde la consola que nos ofrece oracle usamos:
```sh
start (unicacion del archivo)/scriptModulo
```
El aplicativo usa un metodo para obtener las credenciales de acceso a la base de datos. Este metodo lee un archivo PY con dichas credenciales. Es necesario crear este archivo (credentials.json) y escribir las credenciales como en el siguiente ejemplo:
```sh
{
 "username = 'modulo1'
  password = 'modulo1'
  dsn = 'localhost/orcl'
  port=1512
  encoding='UTF-8'"
}
```
### Creacion de PDF's:

Para que la funcion de crear PDF's funcione de manera correcta hay que tener en cuenta la libreria **PDFkit**, sin embargo hay que tener en cuenta el SO en el que se va a desplegar el servidor, o en donde este instalado el programa.

```
  pip install pdfkit
```

Primero se debe instalar wkhtmltopdf, una dependencia vital para pdfkit, que se puede conseguir del siguiente repo: [wkhtmltopdf](https://github.com/wkhtmltopdf/wkhtmltopdf).

Ademas de la instalacion, se debe verificar que se instale en el disco duro o la memoria en donde se va a alojar la aplicacion, ademas de que se agregue el path en las variables de entorno del sistema como del usuario.

### Modelo base de datos:

Para la creacion del modelo de la base de datos, se utilizo PowerDesigner V16.5. (version de prueba)
