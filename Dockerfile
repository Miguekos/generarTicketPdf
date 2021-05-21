FROM python:3.6

COPY ["requeriments.txt" ,  "/app/"]

WORKDIR /app

RUN apt-get update
RUN apt-get install wkhtmltopdf -y
RUN pip install -r requeriments.txt

COPY ["." ,  "/app/"]
#COPY . /app

EXPOSE 5238

CMD [ "python" , "app.py" ]