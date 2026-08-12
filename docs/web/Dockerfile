# syntax=docker/dockerfile:1
#
# Self-contained: the build clones the repository itself, so it needs no build
# context and can sit next to docker-compose.yml on the deployment host.
#
#   docker compose build --no-cache && docker compose up -d --force-recreate
#
# There is no auto-update loop inside the container: deploy.sh rebuilds the image
# on every push, so a long-lived container would only ever serve a stale build.

ARG BUN_IMAGE=oven/bun:1-slim

FROM ${BUN_IMAGE} AS build
ARG REPO_URL=https://github.com/Stoupy51/StewBeet.git
ARG REPO_REF=main

# git clones the sources, curl fetches uv. Both are absent from the slim image, and
# ca-certificates is only a *recommended* package of git, so --no-install-recommends
# drops it and the clone then fails on "Problem with the SSL CA cert".
RUN apt-get update && apt-get install -y --no-install-recommends git ca-certificates curl && \
    rm -rf /var/lib/apt/lists/*

# uv brings its own Python, so this image never needs a Python base or a system interpreter.
RUN curl -LsSf https://astral.sh/uv/install.sh | sh
ENV PATH="/root/.local/bin:${PATH}"

WORKDIR /app
RUN git clone --depth 1 --branch "${REPO_REF}" "${REPO_URL}" .

# Builds docs/web/playground/hero with StewBeet itself and writes the file tree, the file contents
# and the PNGs the landing page hero shows, over whatever the repository had committed. Doing it
# here means the deployed hero can never show a build older than the code being deployed.
#
# uv reads requires-python from python_package/pyproject.toml and downloads that interpreter.
# The build needs no display and no network of its own: docs/web/playground/hero/iso_renders holds
# the renders, so model_resolver, and the OpenGL context behind it, is never reached.
WORKDIR /app/python_package
RUN uv run scripts/build_hero_output.py

WORKDIR /app/docs/web
RUN bun install --frozen-lockfile

# scripts/build-search-index.ts reads ../../docs and ../../python_package, and fetches
# objects.inv for the API symbols — it warns without failing when that is unreachable.
# scripts/prehighlight.ts reads the hero output written just above.
RUN bun run build


FROM ${BUN_IMAGE} AS runtime
WORKDIR /app/docs/web
ENV NODE_ENV=production

# Runtime deps only: server.tsx imports nothing from vite, typescript or eslint
COPY --from=build /app/docs/web/package.json /app/docs/web/bun.lock ./
RUN bun install --frozen-lockfile --production

# server.tsx renders the React routes on demand for /markdown, so the runtime needs
# the sources too, not just dist/.
COPY --from=build /app/docs/web/dist ./dist
COPY --from=build /app/docs/web/src ./src
COPY --from=build /app/docs/web/server.tsx ./server.tsx

USER bun
EXPOSE 4173

HEALTHCHECK --interval=30s --timeout=5s --start-period=15s --retries=3 \
    CMD bun --eval "const r = await fetch('http://127.0.0.1:4173/'); process.exit(r.ok ? 0 : 1)"

CMD ["bun", "server.tsx"]
