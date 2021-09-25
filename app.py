from doctest import debug

from flask import Flask, render_template, make_response, request, send_from_directory
import pdfkit
import pytz
import requests
import json
import os
from datetime import datetime
import qrcode  # Importamos el modulo necesario para trabajar con codigos QR
from itertools import groupby

app = Flask(__name__)
app.config['PDF_FOLDER'] = 'fileserver/'
app.config['STATIC'] = 'static/'
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
    'header-spacing': '4',
    'footer-spacing': '2',
    'footer-font-size': '10',
    'header-font-size': '10',
    # 'margin-top': '0.2in',
    # 'margin-right': '0.0in',
    # 'margin-bottom': '0.3in',
    # 'margin-left': '0.0in',
    # 'margin-bottom': '0.3in',
    'orientation': 'Portrait',
    'disable-forms': '',
    'encoding': "UTF-8",
    'footer-right': '[page] / [topage]',
    'custom-header': [
        ('Accept-Encoding', 'gzip')
    ],
    # 'quiet': '',
    # 'cookie': [
    #     ('cookie-name1', 'cookie-value1'),
    #     ('cookie-name2', 'cookie-value2'),
    # ],
    'no-outline': None
}


def delete_files(name):
    os.remove("{}{}.pdf".format(app.config['PDF_FOLDER'], name))


@app.route('/gnrpdf/fileserverdelete/<filename>')
def delete_any_file(filename):
    delete_files(filename)
    return "Delete Finish"


@app.route('/gnrpdf/fileserver/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['PDF_FOLDER'], filename)


@app.route('/gnrpdf/static/<filename>')
def uploaded_file_static(filename):
    return send_from_directory(app.config['STATIC'], filename)


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
                               pdf="http://127.0.0.1:5238/gnrpdf/fileserver/tickets/{}.png".format(
                                   _json['registro']['registro']),
                               qr="http://127.0.0.1:5238/gnrpdf/fileserver/tickets/{}.png".format(
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


@app.route('/gnrpdf/actadeservicios/<orden>/<tipo>', methods=['GET'])
def actadeservicios(orden, tipo):
    try:
        print(orden)
        url = 'https://api.reinventing.com.pe/v2.0/pdf/js_acta_operac/{}'.format(orden)
        headers = {'content-type': 'application/json'}
        # body = {
        #     "id": orden
        # }
        # data = json.dumps(body)
        x = requests.get(url, headers=headers)
        response = json.loads(x.content)
        print("cuenta", response)
        if response['res'] == "ok":
            d = 1
            if d == 1:
                pdffile = app.config['PDF_FOLDER'] + 'actadeservicios_{}.pdf'.format(orden)
                lima = pytz.timezone('America/Lima')
                fechaactual = current_date_format(datetime.now(lima))
                print(fechaactual)
                js_servic = response['operac'][0]['f_js_acta_operac']['js_servic']
                print("js_servic", js_servic)
                js_articu = response['operac'][0]['f_js_acta_operac']['js_articu']
                print("js_servic", js_servic)
                rendered = render_template('actadeservicios_reinventing.html', orden=orden, json=response['operac'],
                                           js_servic=js_servic if js_servic else [],
                                           js_articu=js_articu if js_articu else [], fecha=fechaactual)

                if tipo == "1":
                    pdf = pdfkit.from_string(rendered, False, options=options) if os.name != "nt" else pdfkit.from_string(
                        rendered, False, options=options, configuration=config)
                    response = make_response(pdf)
                    response.headers['Content-Type'] = 'aplication/pdf'
                    response.headers['Content-Disposition'] = 'attachment; filename=actadeservicios_{}.pdf'.format(orden)
                    return response
                if tipo == "2":
                    pdfkit.from_string(rendered, pdffile, options=options) if os.name != "nt" else pdfkit.from_string(
                        rendered, pdffile, options=options, configuration=config)
                    return {
                        "codRes": "00",
                        "message": "{}/gnrpdf/fileserver/actadeservicios_{}.pdf".format("http://95.111.235.214:5238", orden)
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


@app.route('/gnrpdf/proformadeservicios/<orden>/<tipo>', methods=['GET'])
def formulario_reinventing(orden, tipo):
    try:
        print(orden)
        url = 'https://api.reinventing.com.pe/v2.0/pdf/js_proforma_operac/{}'.format(orden)
        headers = {'content-type': 'application/json'}
        # body = {
        #     "id": orden
        # }
        # data = json.dumps(body)
        x = requests.get(url, headers=headers)
        response = json.loads(x.content)
        print("cuenta", response)
        if response['res'] == "ok":
            d = 1
            if d == 1:
                pdffile = app.config['PDF_FOLDER'] + 'proforma_{}.pdf'.format(orden)
                lima = pytz.timezone('America/Lima')
                fechaactual = current_date_format(datetime.now(lima))
                print(fechaactual)
                js_servic = response['operac'][0]['f_js_proforma_operac']['js_servic']
                print("js_servic", js_servic)
                js_articu = response['operac'][0]['f_js_proforma_operac']['js_articu']
                rendered = render_template('formulario_reinventing.html', orden=orden, json=response['operac'],
                                           js_servic=js_servic if js_servic else [],
                                           js_articu=js_articu if js_articu else [], fecha=fechaactual)

                if tipo == "1":
                    pdf = pdfkit.from_string(rendered, False, options=options) if os.name != "nt" else pdfkit.from_string(
                        rendered, False, options=options, configuration=config)
                    response = make_response(pdf)
                    response.headers['Content-Type'] = 'aplication/pdf'
                    response.headers['Content-Disposition'] = 'attachment; filename=proforma_{}.pdf'.format(orden)
                    return response
                if tipo == "2":
                    pdfkit.from_string(rendered, pdffile, options=options) if os.name != "nt" else pdfkit.from_string(
                        rendered, pdffile, options=options, configuration=config)
                    return {
                        "codRes": "00",
                        "message": "{}/gnrpdf/fileserver/proforma_{}.pdf".format("http://95.111.235.214:5238", orden)
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


@app.route('/gnrpdf/reporte_equas/<lote>/<tipo>', methods=['GET'])
def reporte_equas(lote, tipo):
    try:
        options = {
            'page-size': 'A4',
            'dpi': 300,
            # 'disable-smart-shrinking': '',
            'header-spacing': '4',
            'footer-spacing': '2',
            'footer-font-size': '10',
            'header-font-size': '10',
            # 'margin-top': '0.2in',
            # 'margin-right': '0.0in',
            # 'margin-bottom': '0.3in',
            # 'margin-left': '0.0in',
            # 'margin-bottom': '0.3in',
            'orientation': 'Landscape',
            'disable-forms': '',
            'encoding': "UTF-8",
            'footer-right': '[page] / [topage]',
            'custom-header': [
                ('Accept-Encoding', 'gzip')
            ],
            # 'quiet': '',
            # 'cookie': [
            #     ('cookie-name1', 'cookie-value1'),
            #     ('cookie-name2', 'cookie-value2'),
            # ],
            'no-outline': None
        }
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
            # print(fechaactual)

            count_list = []
            cant_lotes = []
            lotes = []
            lotes_newlist = []
            cabecera = []
            cabecera_newlist = []
            punto_muestreo = []
            punto_muestreo_newlist = []
            parametros = []
            parametros_newlist = []
            unidades = []
            unidades_newlist = []

            print("len", len(response['result']))

            for x in response['result']:
                parametros.append(x['parametro'])
                unidades.append(x['unidades'])
                lotes.append(x['cod_muestra'])
                punto_muestreo.append(x['punto_muestreo'])
                # print(x['parametro'])

            for element in punto_muestreo:
                if element not in punto_muestreo_newlist:
                    punto_muestreo_newlist.append(element)

            for element in parametros:
                if element not in parametros_newlist:
                    parametros_newlist.append(element)

            for element in unidades:
                if element not in unidades_newlist:
                    unidades_newlist.append(element)

            for element in lotes:
                if element not in lotes_newlist:
                    lotes_newlist.append(element)

            # max_cant = []

            # max_cant.append(len(parametros_newlist))
            print("parametros_newlist", len(parametros_newlist))
            print("unidades_newlist", len(unidades_newlist))
            print("lotes_newlist", len(lotes_newlist))


            INFO = response['result']


            INFO_list = []

            # define a fuction for key
            def key_func(k):
                return k['cod_muestra']

            # sort INFO data by 'company' key.
            INFO = sorted(INFO, key=key_func)

            for key, value in groupby(INFO, key_func):
                # print(key)
                # print(len(list(value)))
                INFO_list.append({
                    key : list(value)
                })
                # max_cant.append(len(list(value)))
                # print("--> ",list(value))
            # print("max_cant", max_cant)
            print("INFO_list", INFO_list)
            # max_value = max(max_cant)
            # print("max_value", max_value)

            cc = 0
            while cc < len(parametros_newlist):
                count_list.append(cc)
                cc = cc + 1

            ff = 0
            while ff < len(lotes_newlist):
                cant_lotes.append(ff)
                ff = ff + 1

            nueva_unidad = []
            print("unidades_newlist[uu]", unidades_newlist[0])
            uu = 0
            while uu < len(parametros_newlist):
                nueva_unidad.append(unidades[uu])
                uu = uu + 1

            print("nueva_unidad", nueva_unidad)

            # count_list = [1,2]
            print("count_list", count_list)

            rendered = render_template('reporte_equas_new.html', INFO_list=INFO_list, punto_muestreo_newlist=punto_muestreo_newlist, count_list=count_list, json=response, lotes_newlist=lotes_newlist,
                                       unidades=nueva_unidad, cant_lotes=cant_lotes, parametros=parametros_newlist, fecha=fechaactual,
                                       logo="http://127.0.0.1:5238/gnrpdf/fileserver/{}.png".format("logo_equas_solid"), )

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
                    "message": "{}/gnrpdf/fileserver/{}.pdf".format("http://95.111.235.214:5238", lote)
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


# multiservicios_blanco
@app.route('/gnrpdf/generarreporte/<tipo>', methods=['POST'])
def generarreporte(tipo):
    _json = request.json
    try:
        options = {
            'page-size': 'A4',
            'dpi': 300,
            # 'disable-smart-shrinking': '',
            'header-spacing': '4',
            'footer-spacing': '2',
            'footer-font-size': '10',
            'header-font-size': '10',
            # 'footer-center' : 'asdasdasd',
            'footer-html': 'http://127.0.0.1:5238/gnrpdf/static/footer_multi.html',
            # 'margin-top': '0.2in',
            # 'margin-right': '0.0in',
            # 'margin-bottom': '0.3in',
            # 'margin-left': '0.0in',
            # 'margin-bottom': '0.3in',
            # 'orientation': 'Landscape',
            'orientation': 'Portrait',
            'disable-forms': '',
            'encoding': "UTF-8",
            'footer-right': '[page] / [topage]',
            'custom-header': [
                ('Accept-Encoding', 'gzip')
            ],
            # 'quiet': '',
            # 'cookie': [
            #     ('cookie-name1', 'cookie-value1'),
            #     ('cookie-name2', 'cookie-value2'),
            # ],
            'no-outline': None
        }

        name = _json['expediente']
        print("name", name)
        # try:
        #     import time
        #     delete_files(name)
        #     print("se elimino", name)
        # except Exception as e:
        #     print("Exception no se pudo eliminar", e)
        #     pass

        if True:
            pdffile = app.config['PDF_FOLDER'] + '{}.pdf'.format(name)
            lima = pytz.timezone('America/Lima')
            fechaactual = current_date_format(datetime.now(lima))
            print(fechaactual)
            print("_json['img']", _json['img'])
            logo = "https://api.apps.com.pe/servermultiblanco/files/{}".format(_json['img'])
            if len(_json['img']) > 1:
                rendered = render_template('reportemulti.html', json=_json, fecha=fechaactual, logo=logo)
            else:
                rendered = render_template('reportemulti.html', json=_json, fecha=fechaactual)
            if tipo == "1":
                pdf = pdfkit.from_string(rendered, False, options=options) if os.name != "nt" else pdfkit.from_string(
                    rendered, False, options=options, configuration=config)
                response = make_response(pdf)
                response.headers['Content-Type'] = 'aplication/pdf'
                response.headers['Content-Disposition'] = 'attachment; filename=reporte_multi_blanco_{}.pdf'.format(name)
                return response
            if tipo == "2":
                pdfkit.from_string(rendered, pdffile, options=options) if os.name != "nt" else pdfkit.from_string(
                    rendered, pdffile, options=options, configuration=config)
                return {
                    "codRes": "00",
                    "message": "{}/gnrpdf/fileserver/{}.pdf".format("http://95.111.235.214:5238", name)
                }
            # pdf = pdfkit.from_string(rendered, pdffile, options=options, configuration=config)

            # return "http://95.111.235.214:5238/fileserver/tickets/{}.pdf".format(_json['registro']['registro'])
            # return "http://127.0.0.1:5238/fileserver/{}.pdf".format("prueba")

        # else:
        #     return "Error Controlado"
    except ValueError:
        print(ValueError)
        return {
            "codRes": "99",
            "message": "Error Controlado"
        }


if __name__ == '__main__':
    app.run(debug=True, port=5238, host="0.0.0.0")
