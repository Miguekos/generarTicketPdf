FROM python:3.6

COPY ["requeriments.txt" ,  "/app/"]

WORKDIR /app

ADD https://github.com/wkhtmltopdf/packaging/releases/download/0.12.6-1/wkhtmltox_0.12.6-1.buster_amd64.deb /app
#RUN apt-get update
#RUN apt-get install wkhtmltopdf -y
RUN apt-get install ./app/wkhtmltox_0.12.6-1.buster_amd64.deb -y
RUN pip install -r requeriments.txt

COPY ["." ,  "/app/"]
#COPY . /app

EXPOSE 5238

CMD [ "python" , "app.py" ]