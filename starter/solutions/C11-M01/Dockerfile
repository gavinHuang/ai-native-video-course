# ComfyUI server with pinned versions. Reference solution for C11·M01.
#
# NVIDIA GPU (default, CUDA 12.8 wheels):
#   docker build -t comfyui:0.38.0 .
#   docker run --gpus all -p 8188:8188 -v /data/models:/opt/ComfyUI/models \
#     -v /data/output:/opt/ComfyUI/output -v /data/input:/opt/ComfyUI/input comfyui:0.38.0
# CPU only (to test the image and the API on a laptop; generation is too slow for real work):
#   docker build --build-arg TORCH_INDEX=https://download.pytorch.org/whl/cpu -t comfyui:0.38.0-cpu .
#   docker run -p 8188:8188 comfyui:0.38.0-cpu --cpu
#
# Models are NOT in the image. Mount them as a volume and download them with
# starter/comfyui/download_models.py, which checks each SHA-256 hash.
FROM python:3.12-slim

ARG COMFYUI_COMMIT=f1072eb0350638a3390ddb6afbcaa8c6b237c6fd
ARG TORCH_INDEX=https://download.pytorch.org/whl/cu128

RUN apt-get update && apt-get install -y --no-install-recommends git ffmpeg libgl1 libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

RUN useradd -m -u 1000 comfy && mkdir -p /opt/ComfyUI && chown comfy /opt/ComfyUI
USER comfy
WORKDIR /opt/ComfyUI

# Pin ComfyUI to one commit. Record this commit in every run log (C11·M04).
RUN git init -q . && git remote add origin https://github.com/comfyanonymous/ComfyUI.git \
    && git fetch -q --depth 1 origin ${COMFYUI_COMMIT} && git checkout -q FETCH_HEAD

ENV VIRTUAL_ENV=/opt/ComfyUI/.venv PATH=/opt/ComfyUI/.venv/bin:$PATH PYTHONUNBUFFERED=1
RUN python -m venv $VIRTUAL_ENV \
    && pip install --no-cache-dir torch torchvision torchaudio --index-url ${TORCH_INDEX} \
    && pip install --no-cache-dir -r requirements.txt

EXPOSE 8188
HEALTHCHECK --interval=30s --timeout=5s --start-period=120s CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8188/system_stats', timeout=4)"
ENTRYPOINT ["python", "main.py", "--listen", "0.0.0.0", "--port", "8188"]
