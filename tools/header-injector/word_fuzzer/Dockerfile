FROM python:3.12.0-slim-bullseye as builder
RUN addgroup --system armorgroup && adduser --system --ingroup armorgroup armoruser
ENV DEBIAN_FRONTEND=noninteractive
ENV PIP_NO_CACHE_DIR=1
RUN apt update && apt upgrade -y
WORKDIR /app
COPY .. /app
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt
USER armoruser
CMD ["python", "scanner.py"]