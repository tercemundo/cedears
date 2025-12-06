#!/usr/bin/env python3
import json
import html
import re
from pathlib import Path

INPUT = "rava_acciones.html"      # o el archivo donde guardes el source
OUTPUT = "paneles.txt"


def main():
    raw = Path(INPUT).read_text(encoding="utf-8")

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

    # 5) guardar uno por línea
    ordenados = sorted(simbolos)
    Path(OUTPUT).write_text("\n".join(ordenados) + "\n", encoding="utf-8")
    print(f"Guardados {len(ordenados)} símbolos en {OUTPUT}")


if __name__ == "__main__":
    main()

