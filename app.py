from doctest import debug

from flask import Flask, render_template, make_response, request, send_from_directory
import pdfkit
import pytz
from datetime import datetime
import qrcode  # Importamos el modulo necesario para trabajar con codigos QR

app = Flask(__name__)
app.config['PDF_FOLDER'] = 'fileserver/'
app.config['TEMPLATE_FOLDER'] = 'templates/'

@app.route('/fileserver/tickets/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['PDF_FOLDER'],
                               filename)

@app.route('/ticketpdf', methods=['POST'])
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
                               pdf="http://127.0.0.1:5454/fileserver/uploads/{}.png".format(_json['registro']['registro']),
                               qr="http://127.0.0.1:5454/fileserver/uploads/{}.png".format(
                                   _json['registro']['registro']))
    # css = ['estado.css']
    pdf = pdfkit.from_string(rendered, pdffile)
    # pdf = pdfkit.from_string(rendered, False, css=css, configuration=config)
    # pdf = pdfkit.from_string(rendered, pdffile, configuration=config)

    return "http://95.111.235.214:5454/fileserver/tickets/{}.pdf".format(_json['registro']['registro'])

    # response = make_response(pdf)
    # response.headers['Content-Type'] = 'aplication/pdf'
    # response.headers['Content-Disposition'] = 'attachment; filename=outout.pdf'
    # print(response)
    # return response

if __name__ == '__main__':
    app.run(debug=True, port=5454, host="0.0.0.0")
