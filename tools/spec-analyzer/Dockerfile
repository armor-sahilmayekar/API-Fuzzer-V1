FROM python:3.12.0-slim-bullseye as builder
RUN addgroup --system armorgroup && adduser --system --ingroup armorgroup armoruser
ENV DEBIAN_FRONTEND=noninteractive
ENV PIP_NO_CACHE_DIR=1
RUN apt update && apt upgrade -y
COPY validate.py /app/openapi_spec_validator.py
COPY requirements.txt /app/requirements.txt
WORKDIR /app
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt
USER armoruser
CMD ["python", "/app/openapi_spec_validator.py"]