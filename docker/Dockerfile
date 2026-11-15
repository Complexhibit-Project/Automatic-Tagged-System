# Complexhibit: extractor de información de catálogos de exposiciones
FROM python:3.11-slim

WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1

# PyTorch para CPU (para GPU, sustituir por la imagen base de PyTorch con CUDA)
RUN pip install --no-cache-dir torch --index-url https://download.pytorch.org/whl/cpu
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY complexhibit_ie.py complexhibit_rdf.py extraer.py ./

# Los modelos entrenados se montan en /modelos (nivel1/, nivel2/, atributos/);
# los datos de entrada y salida, en /datos.
VOLUME ["/modelos", "/datos"]
ENTRYPOINT ["python", "extraer.py"]
CMD ["--help"]
