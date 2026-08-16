# syntax=docker/dockerfile:1
#
# The playground sandbox: runs submitted Python, so it is built to be the thing that gets attacked.
#
# Self-contained like docs/web/Dockerfile: it clones what it needs and takes no build context
# beyond this directory.
#
#   docker build -t stewbeet-playground docs/web/playground/sandbox
#
# Nothing here is a security control on its own. The container is: see docker-compose.example.yml
# for the `internal: true` network, the read-only rootfs and the memory cgroup that make this safe.

ARG BASE=debian:trixie-slim
ARG REPO_URL=https://github.com/Stoupy51/StewBeet.git
ARG REPO_REF=main


# ── Textures and renders─────────────────────
# Its own stage so that editing the worker never re-clones three repositories.
#
# Sparse and blobless: only the asset folders are fetched, and .git goes in the same layer so the
# history never reaches the image. iso_renders comes along with the textures because it is what
# lets auto.text_renders emit a real glyph for a known item instead of skipping it.
FROM ${BASE} AS assets
ARG REPO_URL
ARG REPO_REF

RUN apt-get update && apt-get install -y --no-install-recommends git ca-certificates && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /clones

RUN git clone --depth 1 --filter=blob:none --sparse https://github.com/Stoupy51/SimplEnergy.git simplenergy && \
    git -C simplenergy sparse-checkout set assets/textures iso_renders && \
    rm -rf simplenergy/.git

RUN git clone --depth 1 --filter=blob:none --sparse https://github.com/Stoupy51/StardustFragment.git stardust && \
    git -C stardust sparse-checkout set assets/textures iso_renders && \
    rm -rf stardust/.git

RUN git clone --depth 1 --filter=blob:none --sparse --branch "${REPO_REF}" "${REPO_URL}" extensive && \
    git -C extensive sparse-checkout set templates/extensive/assets/textures templates/extensive/iso_renders && \
    rm -rf extensive/.git


# ── The venv, the assets and the selftest────
FROM ${BASE} AS build
ARG REPO_URL
ARG REPO_REF

RUN apt-get update && apt-get install -y --no-install-recommends git ca-certificates curl && \
    rm -rf /var/lib/apt/lists/*

# uv brings its own Python, so this image needs no Python base and no system interpreter, exactly
# like docs/web/Dockerfile. UV_PYTHON_INSTALL_DIR puts that interpreter under /srv so the single
# COPY into the runtime stage takes it along.
RUN curl -LsSf https://astral.sh/uv/install.sh | sh
ENV PATH="/root/.local/bin:${PATH}"
ENV UV_PYTHON_INSTALL_DIR=/srv/python

WORKDIR /source
RUN git clone --depth 1 --branch "${REPO_REF}" "${REPO_URL}" .

# StewBeet comes from the clone rather than from PyPI so the playground can never disagree with
# the documentation deployed beside it.
RUN uv python install 3.14 && \
    uv venv --python 3.14 --python-preference only-managed /srv/.venv && \
    uv pip install --python /srv/.venv/bin/python ./python_package

COPY --from=assets /clones /clones
COPY merge_assets.py /srv/merge_assets.py
RUN /srv/.venv/bin/python /srv/merge_assets.py /clones /srv/assets && rm -rf /clones

COPY worker.py runner.py /srv/
COPY project /srv/project

# A read-only rootfs can never write a .pyc, so every one of them has to exist already.
RUN /srv/.venv/bin/python -m compileall -q /srv

# Builds twice, once with an item that has a bundled render and once with an item that has none.
# The second case is what fails the image build the day a pipeline change starts reaching for
# model_resolver, instead of letting a visitor discover it as a fifteen second hang.
RUN /srv/.venv/bin/python /srv/worker.py --selftest


# ── Runtime──────────────────────────────────
FROM ${BASE} AS runtime

COPY --from=build /srv /srv

RUN groupadd -g 10001 sandbox && \
    useradd -u 10001 -g 10001 -M -d /nonexistent -s /usr/sbin/nologin sandbox

# The venv was assembled in a stage that had git, curl and ca-certificates installed. This proves
# the interpreter still has every shared library it needs in a base that has none of them.
RUN /srv/.venv/bin/python -c "import stewbeet, beet, PIL"

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

USER 10001:10001
EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD ["/srv/.venv/bin/python", "-c", "import urllib.request, sys; sys.exit(0 if urllib.request.urlopen('http://127.0.0.1:8000/health', timeout=3).status == 200 else 1)"]

CMD ["/srv/.venv/bin/python", "/srv/worker.py"]
