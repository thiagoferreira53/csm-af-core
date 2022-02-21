FROM python:3.9-slim-buster
WORKDIR /app
ENV LANG=C.UTF-8 LC_ALL=C.UTF-8 PYTHONUNBUFFERED=1
ENV LOG_LEVEL info
ENV PYTHONPATH "${PYTHONPATH}:/app/"
COPY . /app/
# RUN apt-get update & pip3 install  -r requirements.txt
RUN pip3 install  -r requirements.txt
ENTRYPOINT [ "./gunicorn.sh" ]