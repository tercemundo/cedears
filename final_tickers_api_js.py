#!/usr/bin/env python3
import requests
import certifi
import json
import html
import re
import sqlite3
from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import JSONResponse, HTMLResponse
import uvicorn

# --------- CONSTANTES ---------

URL_HTML = "https://www.rava.com/cotizaciones/acciones-argentinas"
HTML_FILE = Path("rava_acciones.html")
DB_PATH = Path("tickers.db")


# --------- SCRAPING RAVA ---------

def descargar_html() -> None:
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
    }
    resp = requests.get(URL_HTML, headers=headers, verify=certifi.where(), timeout=30)
    resp.raise_for_status()
    HTML_FILE.write_text(resp.text, encoding="utf-8")
    print(f"[OK] HTML guardado en {HTML_FILE}")


def extraer_simbolos_desde_html() -> list[str]:
    raw = HTML_FILE.read_text(encoding="utf-8")

    m = re.search(r'datos="({.*})"', raw)
    if not m:
        raise SystemExit('No encontré el bloque datos="{...}" en el HTML')

    datos_escapados = m.group(1)
    datos_json_text = html.unescape(datos_escapados)
    data = json.loads(datos_json_text)

    simbolos = set()
    for panel_items in data.values():
        for item in panel_items:
            simb = item.get("simbolo")
            if simb:
                simbolos.add(simb)

    ordenados = sorted(simbolos)
    print(f"[OK] Extraídos {len(ordenados)} símbolos de Rava")
    return ordenados


# --------- SQLITE ---------

def init_db(simbolos: list[str]) -> None:
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS tickers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            symbol TEXT UNIQUE NOT NULL,
            yahoo_symbol TEXT UNIQUE NOT NULL
        )
        """
    )

    cur.execute("DELETE FROM tickers")

    rows = [(s, f"{s}.BA") for s in simbolos]
    cur.executemany(
        "INSERT OR IGNORE INTO tickers (symbol, yahoo_symbol) VALUES (?, ?)",
        rows,
    )

    conn.commit()
    conn.close()
    print(f"[OK] SQLite inicializada en {DB_PATH} con {len(rows)} filas")


def get_symbols() -> list[str]:
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT symbol FROM tickers ORDER BY symbol")
    rows = [r[0] for r in cur.fetchall()]
    conn.close()
    return rows


def get_yahoo_symbols() -> list[str]:
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT yahoo_symbol FROM tickers ORDER BY yahoo_symbol")
    rows = [r[0] for r in cur.fetchall()]
    conn.close()
    return rows


# --------- FASTAPI APP ---------

app = FastAPI(
    title="API Tickers Rava",
    description="Tickers de Rava y sus símbolos Yahoo (.BA), con vista en vanilla JS.",
    version="1.0.0",
)


@app.get("/tickers")
def read_tickers():
    """
    Devuelve lista de símbolos normales (ej: ALUA, CEPU, GGAL).
    """
    data = get_symbols()
    return JSONResponse(content=data)


@app.get("/yahoo")
def read_yahoo_tickers():
    """
    Devuelve lista de símbolos para Yahoo Finance (ej: ALUA.BA, CEPU.BA).
    """
    data = get_yahoo_symbols()
    return JSONResponse(content=data)


@app.get("/", response_class=HTMLResponse)
def index():
    """
    Página simple con vanilla JS que muestra los tickers leídos desde SQLite.
    """
    symbols = get_symbols()
    tickers_js = json.dumps(symbols)

    html_page = f"""
<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="utf-8" />
  <title>Tickers Rava</title>
  <style>
    body {{ font-family: system-ui, sans-serif; margin: 20px; }}
    h1 {{ margin-bottom: 5px; }}
    small {{ color: #666; }}
    ul {{ list-style: none; padding: 0; max-width: 320px; }}
    li {{ padding: 4px 0; border-bottom: 1px solid #eee; }}
    code {{ background:#f5f5f5; padding:2px 4px; border-radius:3px; }}
  </style>
</head>
<body>
  <h1>Tickers Rava</h1>
  <small>Servidos desde SQLite, renderizados con JavaScript vanilla.</small>
  <p>Total: <span id="count"></span></p>
  <ul id="lista"></ul>

  <script>
    const TICKERS = {tickers_js};

    const ul = document.getElementById("lista");
    const countSpan = document.getElementById("count");
    countSpan.textContent = TICKERS.length;

    TICKERS.forEach(t => {{
      const li = document.createElement("li");
      li.innerHTML = "<code>" + t + "</code>";
      ul.appendChild(li);
    }});
  </script>
</body>
</html>
"""
    return HTMLResponse(content=html_page)


# --------- MAIN ---------

def main():
    # 1) Scraping + extracción
    descargar_html()
    simbolos = extraer_simbolos_desde_html()

    # 2) Inicializar SQLite
    init_db(simbolos)

    # 3) Levantar API
    print("[OK] API en http://127.0.0.1:8000")
    print("  - /tickers -> símbolos 'comunes'")
    print("  - /yahoo   -> símbolos Yahoo (.BA)")
    print("  - /        -> HTML con JS vanilla")
    print("  - /docs    -> Swagger UI")
    uvicorn.run(app, host="0.0.0.0", port=8000)


if __name__ == "__main__":
    main()

