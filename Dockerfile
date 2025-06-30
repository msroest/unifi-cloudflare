FROM ghcr.io/opentofu/opentofu:minimal AS tofu

FROM python:3-alpine

COPY --from=tofu /usr/local/bin/tofu /usr/local/bin/tofu

COPY generate.py /generate.py
COPY generate.sh /generate.sh
COPY requirements.txt /requirements.txt
ADD terraform /terraform
RUN apk add --update --no-cache curl bash && \
python3 -m venv .venv &&\
.venv/bin/pip3 install -r /requirements.txt && rm -rf requirements.txt

ENTRYPOINT ["/generate.sh"]