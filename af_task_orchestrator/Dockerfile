FROM python:3.9-slim-buster
ENV LANG=C.UTF-8 LC_ALL=C.UTF-8 PYTHONUNBUFFERED=1
ENV LOG_LEVEL info
ENV PYTHONPATH "${PYTHONPATH}:/app/"
WORKDIR /app/
COPY . /app/

RUN apt-get update && apt-get install -y dirmngr gnupg apt-transport-https ca-certificates software-properties-common
RUN apt-key adv --keyserver keyserver.ubuntu.com --recv-keys E298A3A825C0D65DFD57CBB651716619E084DAB9
# RUN add-apt-repository 'deb https://cloud.r-project.org/bin/linux/ubuntu focal-cran40/'

# RUN apt-get update && pip3 install  -r requirements.txt
RUN pip3 install  -r requirements.txt

ENV PATH="/app/scripts:${PATH}"

ENTRYPOINT [ "./start-worker.sh" ]
