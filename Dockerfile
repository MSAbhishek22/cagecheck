# CageCheck — Vultr VM image. NOT built locally in this sandbox (no docker binary).
# On the Vultr VM: docker build -t cagecheck . && docker run --cap-drop=ALL --read-only \
#   --security-opt=no-new-privileges -p 8080:8080 -e HOST=0.0.0.0 -e PORT=8080 \
#   -e CAGE_TIER="docker-per-check (throwaway container, destroyed after each check)" cagecheck
# No secrets are baked into the image. Vultr Inference keys come from VM env vars only.
FROM python:3.12-slim
WORKDIR /app
COPY app/ app/
COPY run.py .
RUN mkdir -p runs
EXPOSE 8080
CMD ["python3", "run.py"]
