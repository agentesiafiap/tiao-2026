# Força a arquitetura x86_64 (amd64)
FROM --platform=linux/amd64 python:3.10-slim

# Configurações de ambiente base
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV DEBIAN_FRONTEND=noninteractive

# Bloqueio de Prompts Interativos (Corrige o erro EOF do YOLO)
ENV WANDB_MODE=disabled
ENV ULTRALYTICS_INTERACTIVE=False
ENV YOLOGCV_TELEMETRY=False
ENV GIT_TERMINAL_PROMPT=0

WORKDIR /app

# Instalação do R, OpenCV e pacotes R PRÉ-COMPILADOS (r-cran-httr e r-cran-jsonlite)
# Isto elimina a necessidade de compilação em C/C++ e resolve os erros do R!
RUN apt-get update && apt-get install -y --no-install-recommends \
    r-base \
    r-cran-httr \
    r-cran-jsonlite \
    libgl1 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Otimização com cache do pip e instalação ultrarrápida via UV
COPY requirements.txt /app/
RUN --mount=type=cache,target=/root/.cache/pip \
    pip install uv && uv pip install --system -r requirements.txt

# Copia o resto do projeto
COPY . /app/

EXPOSE 8501
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]