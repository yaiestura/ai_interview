FROM python:3.6-stretch
MAINTAINER Pavel Tsvetov <patsvetov@edu.hse.ru>
WORKDIR /app/
RUN virtualenv venv
RUN /bin/bash -c "source venv/bin/activate"
RUN pip install -r requirements.txt