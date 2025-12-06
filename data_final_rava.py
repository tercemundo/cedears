#!/usr/bin/env python3
import requests
import certifi
import json
import html
import re
from pathlib import Path

URL_HTML = "https://www.rava.com/cotizaciones/acciones-argentinas"
HTML_FILE = Path("rava_acciones.html")
PANELES_FILE = Path("paneles.txt")
YAHOO_FILE = Path("rava_simbolos_yahoo.txt")


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

    # 1) buscar el bloque datos="{...}" dentro del HTML
    m = re.search(r'datos="({.*})"', raw)
    if not m:
        raise SystemExit("No encontré el bloque datos=\"{...}\" en el HTML")

    datos_escapados = m.group(1)

    # 2) convertir entidades HTML (&quot; -> ")
    datos_json_text = html.unescape(datos_escapados)

    # 3) cargar como JSON
    data = json.loads(datos_json_text)

    # 4) recorrer todos los paneles (GEN, LID, etc.) y extraer 'simbolo'
    simbolos = set()
    for panel_items in data.values():
        for item in panel_items:
            simb = item.get("simbolo")
            if simb:
                simbolos.add(simb)

    simbolos_ordenados = sorted(simbolos)
    PANELES_FILE.write_text("\n".join(simbolos_ordenados) + "\n", encoding="utf-8")
    print(f"[OK] Guardados {len(simbolos_ordenados)} símbolos en {PANELES_FILE}")

    return simbolos_ordenados


def generar_simbolos_yahoo(simbolos):
    yahoo = [f"{s}.BA" for s in simbolos]
    YAHOO_FILE.write_text("\n".join(yahoo) + "\n", encoding="utf-8")
    print(f"[OK] Guardados {len(yahoo)} símbolos Yahoo en {YAHOO_FILE}")


def main():
    descargar_html()
    simbolos = extraer_simbolos_desde_html()
    generar_simbolos_yahoo(simbolos)


if __name__ == "__main__":
    main()

