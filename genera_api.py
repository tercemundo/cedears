#!/usr/bin/env python3
import requests
import certifi
import json
import html
import re
import sqlite3
from pathlib import Path
from fastapi import FastAPI
from fastapi.responses import JSONResponse
import uvicorn

# -------- SCRAPING / EXTRACCIÓN RAVA --------

URL_HTML = "https://www.rava.com/cotizaciones/acciones-argentinas"
HTML_FILE = Path("rava_acciones.html")
DB_PATH = Path("tickers.db")


def descargar_html():
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


def extraer_simbolos_desde_html():
    raw = HTML_FILE.read_text(encoding="utf-8")

    m = re.search(r'datos="({.*})"', raw)
    if not m:
        raise SystemExit("No encontré el bloque datos=\"{...}\" en el HTML")

    datos_escapados = m.group(1)
    datos_json_text = html.unescape(datos_escapados)
    data = json.loads(datos_json_text)

    simbolos = set()
    for panel_items in data.values():
        for item in panel_items:
            simb = item.get("simbolo")
            if simb:
                simbolos.add(simb)

    simbolos_ordenados = sorted(simbolos)
    print(f"[OK] Extraídos {len(simbolos_ordenados)} símbolos de Rava")
    return simbolos_ordenados


# -------- SQLITE --------

def init_db(simbolos):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    # Crear tabla simple
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS tickers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            symbol TEXT UNIQUE NOT NULL,
            yahoo_symbol TEXT UNIQUE NOT NULL
        )
        """
    )

    # Limpiar tabla para recargar
    cur.execute("DELETE FROM tickers")

    rows = [(s, f"{s}.BA") for s in simbolos]
    cur.executemany(
        "INSERT OR IGNORE INTO tickers (symbol, yahoo_symbol) VALUES (?, ?)",
        rows,
    )

    conn.commit()
    conn.close()
    print(f"[OK] Base SQLite inicializada en {DB_PATH} con {len(rows)} filas")


def get_all_tickers_from_db():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT symbol, yahoo_symbol FROM tickers ORDER BY symbol")
    rows = cur.fetchall()
    conn.close()
    return [{"symbol": s, "yahoo_symbol": y} for (s, y) in rows]


# -------- FASTAPI --------

app = FastAPI(
    title="API Tickers Rava",
    description="Devuelve tickers de Rava y su símbolo Yahoo (.BA).",
    version="1.0.0",
)


@app.get("/tickers")
def read_tickers():
    """
    Devuelve todos los tickers almacenados en SQLite.
    """
    data = get_all_tickers_from_db()
    return JSONResponse(content=data)


# -------- MAIN (script) --------

def main():
    # 1) Scraping + extracción
    descargar_html()
    simbolos = extraer_simbolos_desde_html()

    # 2) Crear / poblar SQLite
    init_db(simbolos)

    # 3) Levantar API
    print("[OK] Iniciando API en http://127.0.0.1:8000 ...")
    print("    - Endpoint datos:  http://127.0.0.1:8000/tickers")
    print("    - Swagger /docs:   http://127.0.0.1:8000/docs")
    uvicorn.run(app, host="0.0.0.0", port=8000)


if __name__ == "__main__":
    main()

