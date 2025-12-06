#!/usr/bin/env python3
from pathlib import Path

INPUT = "paneles.txt"
OUTPUT = "rava_simbolos_yahoo.txt"


def main():
    src = Path(INPUT)
    if not src.exists():
        raise SystemExit(f"No encontré {INPUT}, generá primero los símbolos desde Rava")

    tickers = [
        line.strip()
        for line in src.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]

    yahoo_tickers = [f"{t}.BA" for t in tickers]

    Path(OUTPUT).write_text("\n".join(yahoo_tickers) + "\n", encoding="utf-8")
    print(f"Guardados {len(yahoo_tickers)} tickers en {OUTPUT}")


if __name__ == "__main__":
    main()

