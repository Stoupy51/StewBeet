import { defineConfig, type Plugin } from 'vite'
import react from '@vitejs/plugin-react'

/**
 * Serve /api/playground under `bun run dev`.
 *
 * `bun run dev` is Vite and never runs server.tsx, so without this the playground page would get
 * dist-less 404s from the dev server and behave nothing like production. The handler is loaded
 * through ssrLoadModule rather than imported, so editing it stays hot reloadable and there is
 * exactly one implementation of the rate limits, the cache and the build slot.
 *
 * This is the reason src/api/playground.ts may not touch any `Bun.*` API: here it runs on Vite's
 * Node server.
 */
function playgroundDevApi(): Plugin {
    return {
        name: 'playground-dev-api',
        configureServer(server) {
            server.middlewares.use('/api/playground', async (request, response, next) => {
                if (!request.method) return next()

                const chunks: Buffer[] = []
                for await (const chunk of request) chunks.push(chunk as Buffer)

                const module = await server.ssrLoadModule('/src/api/playground.ts') as {
                    handlePlayground: (req: Request, ip: string) => Promise<Response>
                    clientIpFrom: (req: Request, socketIp: string) => string
                }

                // Node's IncomingHttpHeaders allows string[] for repeated headers, which the web
                // Headers constructor does not take, so they are joined the way HTTP sends them.
                const headers: Record<string, string> = {}
                for (const [name, value] of Object.entries(request.headers)) {
                    if (typeof value === 'string') headers[name] = value
                    else if (Array.isArray(value)) headers[name] = value.join(', ')
                }

                const webRequest = new Request('http://localhost/api/playground', {
                    method: request.method,
                    headers,
                    body: chunks.length > 0 ? Buffer.concat(chunks) : undefined,
                })
                const socketIp = request.socket.remoteAddress ?? ''
                const result = await module.handlePlayground(webRequest, module.clientIpFrom(webRequest, socketIp))

                response.statusCode = result.status
                result.headers.forEach((value, name) => response.setHeader(name, value))
                response.end(Buffer.from(await result.arrayBuffer()))
            })
        },
    }
}

// https://vite.dev/config/
export default defineConfig({
  plugins: [react(), playgroundDevApi()],
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
