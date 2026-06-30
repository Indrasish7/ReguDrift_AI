FROM python:3.12-slim

WORKDIR /app

# Install streamlit, HTTP client, and dataframe dependencies
RUN pip install --no-cache-dir \
    streamlit==1.41.0 \
    httpx==0.28.1 \
    pandas==2.2.2 \
    fpdf2==2.8.2

# Copy the app source files
COPY app.py reporter.py ./

# Streamlit port exposure boundary
EXPOSE 8501

ENV PYTHONUNBUFFERED=1

# Command invocation targeting container bridge parameters
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
