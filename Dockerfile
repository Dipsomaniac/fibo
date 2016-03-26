FROM frolvlad/alpine-python3

MAINTAINER Kirill Klenov <horneds@gmail.com>

RUN apk add --update build-base python3-dev && \
    rm -rf /var/cache/apk/*

RUN /usr/bin/pip3 install wheel==0.26.0 cython==0.23.4 && \
    rm -rf /root/.cache

EXPOSE 80

WORKDIR /app

COPY . /app

RUN /usr/bin/pip3 install -e /app && \
    rm -rf /root/.cache

CMD ["/usr/bin/muffin", "fibo", "run", "--bind=0.0.0.0"]
