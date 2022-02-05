FROM python:3.7

WORKDIR /app

COPY ["requeriments.txt" ,  "/app/"]


RUN apt-get update
RUN apt-get install wkhtmltopdf -y
RUN pip install -r requeriments.txt

COPY ["." ,  "/app/"]

EXPOSE 5454

CMD [ "python" , "app.py" ]
