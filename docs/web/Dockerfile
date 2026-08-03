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

# git is the only extra tool the build needs; bun ships with the base image.
# ca-certificates is only a *recommended* package of git, so --no-install-recommends
# drops it and the clone then fails on "Problem with the SSL CA cert".
RUN apt-get update && apt-get install -y --no-install-recommends git ca-certificates && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app
RUN git clone --depth 1 --branch "${REPO_REF}" "${REPO_URL}" .

WORKDIR /app/docs/web
RUN bun install --frozen-lockfile

# scripts/build-search-index.ts reads ../../docs and ../../python_package, and fetches
# objects.inv for the API symbols — it warns without failing when that is unreachable.
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
