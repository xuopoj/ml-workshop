// Tiny reverse proxy that injects a script to fix OpenClaw's WebSocket URL.
// Sits between JupyterHub (port 8888) and the real Gateway (port 18789).
// Intercepts HTML responses to inject a script that sets the correct gatewayUrl
// based on the browser's current location, so WebSocket connects to the right path.

import http from 'node:http';

const GATEWAY_PORT = 18789;
const LISTEN_PORT = 8888;
const GATEWAY_TOKEN = process.env.OPENCLAW_GATEWAY_TOKEN || '';

const server = http.createServer((req, res) => {
  const proxyReq = http.request(
    { hostname: '127.0.0.1', port: GATEWAY_PORT, path: req.url, method: req.method, headers: req.headers },
    (proxyRes) => {
      const contentType = proxyRes.headers['content-type'] || '';
      if (contentType.includes('text/html')) {
        // Buffer HTML response to inject script
        let body = '';
        proxyRes.on('data', (chunk) => body += chunk);
        proxyRes.on('end', () => {
          // Inject script that fixes gatewayUrl before the app loads
          const inject = `<script>
(function() {
  var key = "openclaw.control.settings.v1";
  var proto = location.protocol === "https:" ? "wss" : "ws";
  var correctUrl = proto + "://" + location.host + location.pathname.replace(/\\/$/, "");
  var token = "${GATEWAY_TOKEN}";
  try {
    var s = JSON.parse(localStorage.getItem(key) || "{}");
    var changed = false;
    if (s.gatewayUrl !== correctUrl) { s.gatewayUrl = correctUrl; changed = true; }
    if (s.token !== token) { s.token = token; changed = true; }
    if (changed) localStorage.setItem(key, JSON.stringify(s));
  } catch(e) {
    localStorage.setItem(key, JSON.stringify({ gatewayUrl: correctUrl, token: token }));
  }
})();
</script>`;
          body = body.replace('<head>', '<head>' + inject);
          const headers = { ...proxyRes.headers };
          delete headers['content-length']; // length changed
          delete headers['content-encoding']; // ensure no gzip issues
          res.writeHead(proxyRes.statusCode, headers);
          res.end(body);
        });
      } else {
        // Pass through non-HTML responses
        res.writeHead(proxyRes.statusCode, proxyRes.headers);
        proxyRes.pipe(res);
      }
    }
  );
  req.pipe(proxyReq);
  proxyReq.on('error', (err) => {
    res.writeHead(502);
    res.end('Bad Gateway');
  });
});

// Handle WebSocket upgrades — pass through to Gateway
server.on('upgrade', (req, socket, head) => {
  const proxyReq = http.request({
    hostname: '127.0.0.1',
    port: GATEWAY_PORT,
    path: req.url,
    method: req.method,
    headers: req.headers,
  });
  proxyReq.on('upgrade', (proxyRes, proxySocket, proxyHead) => {
    socket.write(
      `HTTP/1.1 101 Switching Protocols\r\n` +
      Object.entries(proxyRes.headers).map(([k, v]) => `${k}: ${v}`).join('\r\n') +
      '\r\n\r\n'
    );
    if (proxyHead.length) socket.write(proxyHead);
    proxySocket.pipe(socket);
    socket.pipe(proxySocket);
  });
  proxyReq.on('error', () => socket.destroy());
  proxyReq.end();
});

server.listen(LISTEN_PORT, '0.0.0.0', () => {
  console.log(`OpenClaw proxy listening on port ${LISTEN_PORT}, forwarding to Gateway on ${GATEWAY_PORT}`);
});
