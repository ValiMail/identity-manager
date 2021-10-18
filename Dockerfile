FROM python:3.9-bullseye
WORKDIR /usr/src

ENV CRYPTO_PATH=/etc/dane_id/
ENV APP_UID=0

COPY app/depends/requirements.txt /tmp/depends/requirements.txt

RUN apt-get update && \
    apt-get install -y \
        rustc \
        cargo && \
    pip3 install --upgrade pip && \
    pip3 install -r /tmp/depends/requirements.txt && \
    dpkg -r \
        rustc \
        cargo && \
    apt-get autoremove -y && \
    apt-get clean

COPY app/src .

RUN mkdir -p CRYPTO_PATH

CMD python3 ./update_certificate_from_dns.py