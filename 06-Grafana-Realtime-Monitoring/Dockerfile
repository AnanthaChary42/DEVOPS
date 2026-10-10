FROM python:3.10-slim
WORKDIR /app
COPY delivery_metrics.py /app/
RUN pip install prometheus-client
EXPOSE 8000
CMD ["python", "delivery_metrics.py"]
