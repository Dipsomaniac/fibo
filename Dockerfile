FROM frolvlad/alpine-python3

MAINTAINER Kirill Klenov <horneds@gmail.com>

CMD ["/usr/bin/muffin", "fibo", "run", "--bind=0.0.0.0"]

EXPOSE 80

WORKDIR /app

COPY . /app

RUN /usr/bin/pip3 install -r /app/requirements.txt && \
    rm -rf /root/.cache
