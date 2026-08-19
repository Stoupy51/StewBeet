import { defineConfig, type Plugin } from 'vite'
import react from '@vitejs/plugin-react'

/**
 * Serve the /api routes under `bun run dev`.
 *
 * `bun run dev` is Vite and never runs server.tsx, so without this the playground and telemetry
 * pages would get dist-less 404s from the dev server and behave nothing like production. The
 * handlers are loaded through ssrLoadModule rather than imported, so editing them stays hot
 * reloadable and there is exactly one implementation of the rate limits, the cache, the build slot
 * and the daily counter.
 *
 * This is the reason src/api/*.ts may not touch any `Bun.*` API: here they run on Vite's Node server.
 *
 * The middleware is mounted unprefixed and matches the pathname itself, rather than mounting one
 * route per endpoint: connect trims a matched prefix off `req.url`, and rebuilding the original
 * URL from the remainder is exactly the kind of detail that silently drops a query string.
 */
function apiDevRoutes(): Plugin {
    return {
        name: 'api-dev-routes',
        configureServer(server) {
            server.middlewares.use(async (request, response, next) => {
                const url = new URL(request.url ?? '/', 'http://localhost')
                if (!request.method || !url.pathname.startsWith('/api/')) return next()

                const chunks: Buffer[] = []
                for await (const chunk of request) chunks.push(chunk as Buffer)

                // Node's IncomingHttpHeaders allows string[] for repeated headers, which the web
                // Headers constructor does not take, so they are joined the way HTTP sends them.
                const headers: Record<string, string> = {}
                for (const [name, value] of Object.entries(request.headers)) {
                    if (typeof value === 'string') headers[name] = value
                    else if (Array.isArray(value)) headers[name] = value.join(', ')
                }

                const webRequest = new Request(url, {
                    method: request.method,
                    headers,
                    body: chunks.length > 0 ? Buffer.concat(chunks) : undefined,
                })

                const sandbox = await server.ssrLoadModule('/src/api/sandbox.ts') as {
                    clientIpFrom: (req: Request, socketIp: string) => string
                }
                const playground = await server.ssrLoadModule('/src/api/playground.ts') as {
                    handlePlayground: (req: Request, ip: string) => Promise<Response>
                }
                const autoHeaders = await server.ssrLoadModule('/src/api/headers.ts') as {
                    handleHeaders: (req: Request, ip: string) => Promise<Response>
                }
                const telemetry = await server.ssrLoadModule('/src/api/telemetry/index.ts') as {
                    handleTelemetryBuild: (req: Request, ip: string) => Promise<Response>
                    handleTelemetryEvent: (req: Request, ip: string) => Promise<Response>
                    handleTelemetryBuilds: (url: URL) => Response
                    handleTelemetryStreams: (url: URL) => Response
                }

                const clientIp = sandbox.clientIpFrom(webRequest, request.socket.remoteAddress ?? '')
                let result: Response
                if (url.pathname === '/api/playground') result = await playground.handlePlayground(webRequest, clientIp)
                else if (url.pathname === '/api/tools/headers') result = await autoHeaders.handleHeaders(webRequest, clientIp)
                else if (url.pathname === '/api/telemetry/build') result = await telemetry.handleTelemetryBuild(webRequest, clientIp)
                else if (url.pathname === '/api/telemetry/event') result = await telemetry.handleTelemetryEvent(webRequest, clientIp)
                else if (url.pathname === '/api/telemetry/builds') result = telemetry.handleTelemetryBuilds(url)
                else if (url.pathname === '/api/telemetry/streams') result = telemetry.handleTelemetryStreams(url)
                else return next()

                response.statusCode = result.status
                result.headers.forEach((value, name) => response.setHeader(name, value))
                response.end(Buffer.from(await result.arrayBuffer()))
            })
        },
    }
}

// https://vite.dev/config/
export default defineConfig({
  plugins: [react(), apiDevRoutes()],
  server: {
    port: 4173,
  },
  preview: {
    allowedHosts: ['stewbeet.paralya.fr'],
  },
  build: {
    // Left off, this shipped a 627 kB unminified entry chunk to every visitor.
    minify: 'esbuild',
  },
})
