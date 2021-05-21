from doctest import debug

from flask import Flask, render_template, make_response, request, send_from_directory
import pdfkit
import pytz
import requests
import json
import os
from datetime import datetime
import qrcode  # Importamos el modulo necesario para trabajar con codigos QR

app = Flask(__name__)
app.config['PDF_FOLDER'] = 'fileserver/'
app.config['TEMPLATE_FOLDER'] = 'templates/'


def current_date_format(date):
    months = (
        "Enero", "Febrero", "Marzo", "Abri", "Mayo", "Junio", "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre",
        "Diciembre")
    day = date.day
    month = months[date.month - 1]
    year = date.year
    messsage = "{} de {} del {}".format(day, month, year)
    return messsage


global options, config
path_wkthmltopdf = 'wkhtmltox/bin/wkhtmltopdf.exe'
config = pdfkit.configuration(wkhtmltopdf=path_wkthmltopdf)
options = {
    'page-size': 'A4',
    'dpi': 300,
    # 'disable-smart-shrinking': '',
    'margin-top': '0.2in',
    'margin-right': '0.0in',
    # 'margin-bottom': '0.3in',
    'margin-left': '0.0in',
    'margin-bottom': '0.3in',
    'encoding': "UTF-8",
    # 'footer-right': '[page] de [topage]',
    'custom-header': [
        ('Accept-Encoding', 'gzip')
    ],
    # 'quiet': '',
    'cookie': [
        ('cookie-name1', 'cookie-value1'),
        ('cookie-name2', 'cookie-value2'),
    ],
    'no-outline': None
}


@app.route('/fileserver/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['PDF_FOLDER'],
                               filename)


@app.route('/imprimirticketpdf', methods=['POST'])
def index():
    lima = pytz.timezone('America/Lima')
    li_time = datetime.now(lima)
    _json = request.json
    _json['registro']['registro'] = int(_json['registro']['registro'])
    _json['registro']['created_at'] = "{}".format(_json['registro']['created_at'])
    id = _json['id']
    imagen = qrcode.make("{}".format(id))
    archivo_imagen = open(app.config['PDF_FOLDER'] + '{}.png'.format(_json['registro']['registro']), 'wb')
    imagen.save(archivo_imagen)
    archivo_imagen.close()
    pdffile = app.config['PDF_FOLDER'] + '{}.pdf'.format(_json['registro']['registro'])
    # path_wkthmltopdf = 'wkhtmltox/bin/wkhtmltopdf.exe'
    # config = pdfkit.configuration(wkhtmltopdf=path_wkthmltopdf)
    rendered = render_template('test.html', json=_json,
                               pdf="http://127.0.0.1:5238/fileserver/tickets/{}.png".format(
                                   _json['registro']['registro']),
                               qr="http://127.0.0.1:5238/fileserver/tickets/{}.png".format(
                                   _json['registro']['registro']))
    # css = ['estado.css']
    print("http://127.0.0.1:5238/fileserver/tickets/{}.png".format(_json['registro']['registro']))
    pdf = pdfkit.from_string(rendered, pdffile)
    # pdf = pdfkit.from_string(rendered, False, css=css, configuration=config)
    # pdf = pdfkit.from_string(rendered, pdffile, configuration=config)

    return "http://95.111.235.214:5238/fileserver/tickets/{}.pdf".format(_json['registro']['registro'])

    # response = make_response(pdf)
    # response.headers['Content-Type'] = 'aplication/pdf'
    # response.headers['Content-Disposition'] = 'attachment; filename=outout.pdf'
    # print(response)
    # return response


@app.route('/actadeservicios', methods=['GET'])
def actadeservicios():
    lima = pytz.timezone('America/Lima')
    li_time = datetime.now(lima)
    # _json = request.json
    _json = "request.json"
    # _json['registro']['registro'] = int(_json['registro']['registro'])
    # _json['registro']['created_at'] = "{}".format(_json['registro']['created_at'])
    # id = _json['id']
    # imagen = qrcode.make("{}".format(id))
    # archivo_imagen = open(app.config['PDF_FOLDER'] + '{}.png'.format(_json['registro']['registro']), 'wb')
    # imagen.save(archivo_imagen)
    # archivo_imagen.close()
    # pdffile = app.config['PDF_FOLDER'] + '{}.pdf'.format(_json['registro']['registro'])
    pdffile = app.config['PDF_FOLDER'] + '{}.pdf'.format("prueba")
    path_wkthmltopdf = 'wkhtmltox/bin/wkhtmltopdf.exe'
    config = pdfkit.configuration(wkhtmltopdf=path_wkthmltopdf)
    rendered = render_template('actadeservicios.html', json=_json,
                               logo="http://127.0.0.1:5238/fileserver/{}.png".format("logoreinveintg"), )
    # css = ['estado.css']
    # print("http://127.0.0.1:5238/fileserver/tickets/{}.png".format(_json['registro']['registro']))
    # pdf = pdfkit.from_string(rendered, pdffile)
    # pdf = pdfkit.from_string(rendered, False, css=css, configuration=config)
    pdf = pdfkit.from_string(rendered, pdffile, configuration=config)

    # return "http://95.111.235.214:5238/fileserver/tickets/{}.pdf".format(_json['registro']['registro'])
    return "http://127.0.0.1:5238/fileserver/{}.pdf".format("prueba")

    # response = make_response(pdf)
    # response.headers['Content-Type'] = 'aplication/pdf'
    # response.headers['Content-Disposition'] = 'attachment; filename=outout.pdf'
    # print(response)
    # return response


@app.route('/reporte_equas/<lote>/<tipo>', methods=['GET'])
def reporte_equas(lote, tipo):
    try:
        print(lote)
        url = 'https://api.apps.com.pe/equas/get_report/muestreos'
        headers = {'content-type': 'application/json'}
        body = {
            "id": lote
        }
        data = json.dumps(body)
        x = requests.post(url, data=data, headers=headers)
        response = json.loads(x.content)
        print("cuenta", response)
        if response['codRes'] == "00":
            pdffile = app.config['PDF_FOLDER'] + '{}.pdf'.format(lote)
            lima = pytz.timezone('America/Lima')
            fechaactual = current_date_format(datetime.now(lima))
            print(fechaactual)
            rendered = render_template('reporte_equas.html', json=response, fecha=fechaactual,
                                       logo="http://127.0.0.1:5238/fileserver/{}.png".format("logo_equas_solid"), )

            if tipo == "1":
                pdf = pdfkit.from_string(rendered, False, options=options) if os.name != "nt" else pdfkit.from_string(
                    rendered, False, options=options, configuration=config)
                response = make_response(pdf)
                response.headers['Content-Type'] = 'aplication/pdf'
                response.headers['Content-Disposition'] = 'attachment; filename=reporte_equas_{}.pdf'.format(lote)
                return response
            if tipo == "2":
                pdfkit.from_string(rendered, pdffile, options=options) if os.name != "nt" else pdfkit.from_string(
                    rendered, pdffile, options=options, configuration=config)
                return {
                    "codRes": "00",
                    "message": "{}/fileserver/{}.pdf".format("http://127.0.0.1:5238", lote)
                }
            # pdf = pdfkit.from_string(rendered, pdffile, options=options, configuration=config)

            # return "http://95.111.235.214:5238/fileserver/tickets/{}.pdf".format(_json['registro']['registro'])
            # return "http://127.0.0.1:5238/fileserver/{}.pdf".format("prueba")


        else:
            return "Error Controlado"
    except ValueError:
        print(ValueError)
        return {
            "codRes": "99",
            "message": "Error Controlado"
        }


if __name__ == '__main__':
    app.run(debug=True, port=5238, host="0.0.0.0")
