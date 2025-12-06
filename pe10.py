#!/usr/bin/env python3
import argparse
from pathlib import Path

import requests
from bs4 import BeautifulSoup


def obtener_pe_ttm(symbol: str) -> float | None:
    """
    Devuelve el P/E Ratio (TTM) de Yahoo Finance para 'symbol'.
    Si el valor es '--' o no existe, devuelve None.
    """
    symbol = symbol.upper()
    url = f"https://finance.yahoo.com/quote/{symbol}/"
    headers = {
        "User-Agent": "Mozilla/5.0",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.8",
    }

    resp = requests.get(url, headers=headers, timeout=15)
    resp.raise_for_status()

    soup = BeautifulSoup(resp.text, "html.parser")

    tag = soup.find("fin-streamer", attrs={"data-field": "trailingPE"})
    if not tag:
        return None

    valor_str = (tag.get("data-value") or tag.get_text(strip=True) or "").strip()

    # Yahoo muestra -- u otros marcadores cuando no hay PER válido (pérdidas, etc.)
    if valor_str in ("", "--", "N/A"):
        return None

    return float(valor_str)


def procesar_ticker(symbol: str) -> str | None:
    """
    Procesa un ticker: imprime por pantalla y devuelve la línea para guardar.
    Si no hay TTM, devuelve una línea de SKIP.
    """
    symbol = symbol.strip().upper()
    if not symbol:
        return None

    try:
        pe = obtener_pe_ttm(symbol)
        if pe is None:
            linea = f"{symbol},SKIP,NO_TTM"
        else:
            linea = f"{symbol},{pe}"
        print(linea)
        return linea
    except Exception as e:
        linea = f"{symbol},ERROR,{e}"
        print(linea)
        return linea


def main():
    parser = argparse.ArgumentParser(
        description="Obtiene el P/E Ratio (TTM) desde Yahoo Finance."
    )
    parser.add_argument(
        "-i", "--instrument",
        help="Ticker único, por ejemplo RACE"
    )
    parser.add_argument(
        "-f", "--file",
        help="Fichero de texto con tickers, uno por línea (por ejemplo cedears.txt)"
    )
    parser.add_argument(
        "-o", "--output",
        default="tmtm_resultados.txt",
        help="Fichero de salida (por defecto tmtm_resultados.txt)"
    )
    args = parser.parse_args()

    if not args.instrument and not args.file:
        parser.error("Debes especificar -i TICKER o -f fichero.txt")

    salidas: list[str] = []

    # Ticker individual
    if args.instrument:
        linea = procesar_ticker(args.instrument)
        if linea:
            salidas.append(linea)

    # Fichero de tickers
    if args.file:
        path = Path(args.file)
        if not path.is_file():
            raise FileNotFoundError(f"No existe el fichero: {path}")
        with path.open() as fh:
            for line in fh:
                linea = procesar_ticker(line)
                if linea:
                    salidas.append(linea)

    # Guardar resultados
    if salidas:
        out_path = Path(args.output)
        out_path.write_text("\n".join(salidas), encoding="utf-8")
        print(f"\nGuardado en {out_path}")


if __name__ == "__main__":
    main()
