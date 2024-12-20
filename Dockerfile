# https://developers.home-assistant.io/docs/add-ons/configuration#add-on-dockerfile
# FROM python:3.9-slim

# ENV PYTHONUNBUFFERED=1

# COPY src /

# HEALTHCHECK --interval=2m --timeout=3s \
#     CMD curl -f http://localhost:5000/health || exit 1

# WORKDIR /

# RUN pip3 install -r requirements.txt
# CMD ["python3", "main.py"]


# https://developers.home-assistant.io/docs/add-ons/configuration#add-on-dockerfile
FROM python:3.9-slim

ENV PYTHONUNBUFFERED=1

COPY src /

HEALTHCHECK --interval=2m --timeout=3s \
    CMD curl -f http://localhost:5000/health || exit 1

WORKDIR /

RUN pip3 install -r requirements.txt
CMD ["python3", "main.py"]

