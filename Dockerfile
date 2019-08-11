FROM python:3-alpine

# Note that everything is uninstalled later.
ADD requirements.txt /requirements.txt
RUN pip install -U -r /requirements.txt && rm -v /requirements.txt

ADD . /app

CMD ["python3", "/app/meteogalicia.py"]
