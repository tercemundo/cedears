import argparse
import requests
from bs4 import BeautifulSoup
from pathlib import Path

def obtener_pe_ttm(symbol: str) -> float:
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
        raise RuntimeError(f"No encontré trailingPE para {symbol}")

    valor_str = tag.get("data-value") or tag.get_text(strip=True)
    return float(valor_str)

def procesar_ticker(symbol: str) -> str:
    symbol = symbol.strip().upper()
    if not symbol:
        return ""
    try:
        pe = obtener_pe_ttm(symbol)
        linea = f"{symbol},{pe}"
        print(linea)
        return linea
    except Exception as e:
        linea = f"{symbol},ERROR,{e}"
        print(linea)
        return linea

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--instrument", help="Ticker único, ej. RACE")
    parser.add_argument("-f", "--file", help="Fichero con tickers (uno por línea)")
    args = parser.parse_args()

    if not args.instrument and not args.file:
        parser.error("Debes especificar -i TICKER o -f fichero.txt")

    salidas = []

    if args.instrument:
        linea = procesar_ticker(args.instrument)
        if linea:
            salidas.append(linea)

    if args.file:
        path = Path(args.file)
        with path.open() as fh:
            for line in fh:
                linea = procesar_ticker(line)
                if linea:
                    salidas.append(linea)

    # Guardar todo en un CSV/TXT
    with open("tmtm_resultados.txt", "w", encoding="utf-8") as out:
        out.write("\n".join(salidas))

if __name__ == "__main__":
    main()
