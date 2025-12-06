#!/usr/bin/env python3
import requests
import certifi
from bs4 import BeautifulSoup
from pathlib import Path

URL = "https://www.rava.com/cotizaciones/acciones-argentinas"
HTML_FILE = Path("rava_acciones.html")
OUTPUT = Path("paneles.txt")


def descargar_html():
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
    }
    resp = requests.get(URL, headers=headers, verify=certifi.where(), timeout=30)
    resp.raise_for_status()
    HTML_FILE.write_text(resp.text, encoding="utf-8")
    print(f"HTML guardado en {HTML_FILE}")


def extraer_tickers_desde_html():
    html = HTML_FILE.read_text(encoding="utf-8")
    soup = BeautifulSoup(html, "lxml")

    # Mostrar qué tablas ve BeautifulSoup
    print("Tablas encontradas y sus cabeceras:")
    for i, table in enumerate(soup.find_all("table"), 1):
        ths = [th.get_text(strip=True) for th in table.find_all("th")]
        print(f"Tabla #{i}: {ths}")

    # Elegir la PRIMER tabla que tenga al menos una columna llamada 'Especie'
    tabla_objetivo = None
    for table in soup.find_all("table"):
        ths = [th.get_text(strip=True).upper() for th in table.find_all("th")]
        if any("ESPECIE" in t for t in ths):
            tabla_objetivo = table
            break

    if tabla_objetivo is None:
        raise SystemExit("No encontré ninguna tabla con columna 'Especie'")

    tickers = []
    rows = tabla_objetivo.find_all("tr")[1:]  # saltar encabezado
    for row in rows:
        cols = row.find_all("td")
        if not cols:
            continue
        especie = cols[0].get_text(strip=True)
        if especie:
            tickers.append(especie)

    OUTPUT.write_text("\n".join(tickers) + "\n", encoding="utf-8")
    print(f"Guardados {len(tickers)} tickers en {OUTPUT}")


def main():
    descargar_html()
    extraer_tickers_desde_html()


if __name__ == "__main__":
    main()

