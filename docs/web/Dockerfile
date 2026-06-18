FROM debian:bookworm-slim

# Install curl, git, unzip (needed for Bun installer)
RUN apt-get update && apt-get install -y curl git unzip && \
    rm -rf /var/lib/apt/lists/*

# Install Bun
RUN curl -fsSL https://bun.sh/install | bash
ENV PATH="/root/.bun/bin:$PATH"

# Install app
WORKDIR /app
RUN rm -rf repo/ && git clone https://github.com/Stoupy51/StewBeet.git repo

WORKDIR /app/repo/docs/web
RUN bun install && bun run build

# Combine script creation into one RUN
RUN echo '#!/bin/bash\n\
while true; do\n\
  cd /app\n\
  git pull origin main\n\
  cd /app/docs/web\n\
  bun install\n\
  bun run build\n\
  echo "Updated at $(date)"\n\
  sleep 86400\n\
done' > /update.sh && chmod +x /update.sh && \
echo '#!/bin/bash\n\
/update.sh &\n\
cd /app/docs/web\n\
exec bun run my_server' > /start.sh && chmod +x /start.sh

EXPOSE 4173
CMD ["/start.sh"]