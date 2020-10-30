FROM python:3.6

COPY . /app

WORKDIR /app

RUN apt-get update
RUN apt-get install wkhtmltopdf -y
RUN pip install -r requeriment.txt

EXPOSE 5454

CMD [ "python" , "app.py" ]