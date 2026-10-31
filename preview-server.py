#!/usr/bin/env python3
"""Servidor de prévia do painel no Mac.

Serve os arquivos do projeto e faz a ponte com o álbum compartilhado do iCloud
em /api/album?token=..., porque o navegador comum não pode chamar o iCloud
direto (CORS). Na TV, o app Tizen chama o iCloud sem passar por aqui.

Uso: python3 preview-server.py [porta]
"""
import json, os, sys, time, urllib.request, urllib.error
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from urllib.parse import urlparse, parse_qs

ROOT = os.path.dirname(os.path.abspath(__file__))
PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 8765
_cache = {}  # token -> (expira_em, resposta)


def icloud_post(host, token, path, body):
    req = urllib.request.Request(
        f"https://{host}/{token}/sharedstreams/{path}",
        data=json.dumps(body).encode(),
        headers={"Content-Type": "text/plain", "User-Agent": "Mozilla/5.0"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return r.status, json.loads(r.read().decode())
    except urllib.error.HTTPError as e:
        raw = e.read().decode(errors="replace")
        try:
            return e.code, json.loads(raw)
        except Exception:
            return e.code, {"erro": raw[:200]}


def album(token):
    now = time.time()
    if token in _cache and _cache[token][0] > now:
        return _cache[token][1]
    first = token[0]
    b62 = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"
    n = b62.index(token[1]) if first == "A" else b62.index(token[1]) * 62 + b62.index(token[2])
    host = f"p{n:02d}-sharedstreams.icloud.com"
    st, d = icloud_post(host, token, "webstream", {"streamCtag": None})
    if st == 330 and d.get("X-Apple-MMe-Host"):
        host = d["X-Apple-MMe-Host"]
        st, d = icloud_post(host, token, "webstream", {"streamCtag": None})
    if st != 200:
        return {"erro": f"webstream {st}", "urls": []}
    guids, best = [], {}
    for p in d.get("photos", []):
        if p.get("mediaAssetType") == "video" or not p.get("derivatives"):
            continue
        ders = p["derivatives"]
        k = max(ders, key=lambda k: int(ders[k].get("width", 0)))
        best[ders[k]["checksum"]] = (int(ders[k].get("width", 0)), int(ders[k].get("height", 0)))
        guids.append(p["photoGuid"])
    st, u = icloud_post(host, token, "webasseturls", {"photoGuids": guids})
    urls = []
    for cs, (w, h) in best.items():
        it = u.get("items", {}).get(cs)
        if it:
            urls.append({"url": "https://" + it["url_location"] + it["url_path"], "w": w, "h": h})
    out = {"album": d.get("streamName"), "urls": urls}
    _cache[token] = (now + 600, out)
    return out


class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *a, **kw):
        super().__init__(*a, directory=ROOT, **kw)

    def do_GET(self):
        u = urlparse(self.path)
        if u.path == "/api/album":
            token = parse_qs(u.query).get("token", [""])[0]
            body = json.dumps(album(token) if token else {"erro": "sem token", "urls": []}).encode()
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Cache-Control", "no-store")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            return
        return super().do_GET()

    def end_headers(self):
        self.send_header("Cache-Control", "no-store")
        super().end_headers()

    def log_message(self, fmt, *args):
        sys.stderr.write("%s %s\n" % (self.address_string(), fmt % args))


if __name__ == "__main__":
    print(f"Prévia em http://0.0.0.0:{PORT}/  (pasta {ROOT})", flush=True)
    ThreadingHTTPServer(("0.0.0.0", PORT), Handler).serve_forever()
