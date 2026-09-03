# The sealed local-build packet must supply a complete
# registry/repository@sha256:<64-lowercase-hex> reference. There is no default,
# package installation, remote ADD, or build-time command in this recipe.
ARG PYTHON_BASE_IMAGE
FROM ${PYTHON_BASE_IMAGE}
ARG SOURCE_DATE_EPOCH=946684800

LABEL org.opencontainers.image.title="EBU AWS-C0 synthetic worker"
LABEL org.opencontainers.image.description="Inert dependency-free AWS-C0 durability workload"
LABEL org.opencontainers.image.source="repository-local aws/c0/container"

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONHASHSEED=0 \
    PYTHONNOUSERSITE=1

COPY --chown=65534:65534 --chmod=0555 synthetic_worker.py /opt/ebu-c0/synthetic_worker.py
WORKDIR /work
USER 65534:65534
STOPSIGNAL SIGTERM
ENTRYPOINT ["/usr/local/bin/python3", "/opt/ebu-c0/synthetic_worker.py"]
