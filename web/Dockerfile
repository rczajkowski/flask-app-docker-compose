FROM python:2.7

WORKDIR /app/web

ADD . /app/web
RUN pip install -r requirements.txt

EXPOSE 80
CMD python microblog.py