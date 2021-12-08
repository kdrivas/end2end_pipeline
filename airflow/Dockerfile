FROM apache/airflow:2.2.2

USER root
RUN apt update && \
    apt install -y locales && \
	sed -i -e 's/# es_ES.UTF-8 UTF-8/es_ES.UTF-8 UTF-8/' /etc/locale.gen && \
	dpkg-reconfigure --frontend=noninteractive locales

ENV LANG es_ES.UTF-8
ENV LC_ALL es_ES.UTF-8

USER airflow
RUN pip install --upgrade pip setuptools wheel

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY setup.py .
RUN pip install -e .