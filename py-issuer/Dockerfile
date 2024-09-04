FROM python:3.9.2

WORKDIR /opt/py-issuer

COPY app/requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

COPY . .

EXPOSE 5000/tcp

CMD [ "flask", "--app", "app", "run", "--host=0.0.0.0" ]
