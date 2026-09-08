FROM python:3.12-slim

RUN apt-get update && apt-get install -y \
    build-essential \
    libgomp1 \
    git \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir \
    ipython \
    numpy \
    scipy \
    matplotlib \
    pillow \
    jupyterlab \
    notebook

EXPOSE 8888
WORKDIR /workspace
CMD ["jupyter", "lab", "--ip=0.0.0.0", "--allow-root", "--no-browser"]
