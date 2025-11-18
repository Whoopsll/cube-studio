FROM python:3.9

ENV TZ=Asia/Shanghai
ENV DEBIAN_FRONTEND=noninteractive

RUN pip install kubernetes==25.3.0 pysnooper psutil requests

COPY service/AccessMgt/deploy-accessmgt/ /app/

WORKDIR /app
ENV PYTHONPATH=/app:${PYTHONPATH:-}

ENTRYPOINT ["python3", "launcher.py"]

