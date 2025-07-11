FROM hashicorp/terraform:1.12 AS terraform

FROM python:3-alpine

COPY --from=terraform /bin/terraform /usr/local/bin/terraform

COPY generate.py /generate.py
COPY generate.sh /generate.sh
COPY requirements.txt /requirements.txt
ADD terraform /terraform
RUN apk add --update --no-cache curl bash && \
python3 -m venv .venv &&\
.venv/bin/pip3 install -r /requirements.txt && rm -rf requirements.txt && \
cd terraform && terraform init && cd ..

ENTRYPOINT ["/generate.sh"]