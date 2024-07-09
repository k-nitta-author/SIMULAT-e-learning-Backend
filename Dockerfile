FROM python:3.12

ADD main.py .
ADD config.py .

EXPOSE 5000


COPY ./resources ./resources

RUN pip install mysqlclient
RUN pip install sqlalchemy
RUN pip install flask
RUN pip install marshmallow
RUN pip install Flask-RESTful

CMD [ "python", "./main.py"]