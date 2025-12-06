#!/usr/bin/env python3
import sys
import argparse

def encontrar_menor_per(archivo):
    min_ticker = None
    min_per = None
    
    try:
        with open(archivo, "r", encoding="utf-8") as f:
            for linea_num, line in enumerate(f, 1):
                line = line.strip()
                if not line:
                    continue
                    
                parts = line.split(',')
                if len(parts) < 2:
                    continue
                
                ticker = parts[0].strip()
                second = parts[1].strip()
                
                # Saltar SKIP o ERROR
                if second in ("SKIP", "ERROR"):
                    continue
                
                try:
                    per = float(second)
                except ValueError:
                    print(f"Línea {linea_num}: No se pudo convertir '{second}' a float", file=sys.stderr)
                    continue
                
                if min_per is None or per < min_per:
                    min_per = per
                    min_ticker = ticker
        
        if min_ticker is None:
            print("No se encontraron valores PER válidos", file=sys.stderr)
            return 1
        
        print(f"Menor PER: {min_ticker} {min_per}")
        return 0
        
    except FileNotFoundError:
        print(f"Error: Archivo '{archivo}' no encontrado", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"Error leyendo archivo: {e}", file=sys.stderr)
        return 1

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Encuentra el menor PER válido en un archivo")
    parser.add_argument("-f", "--file", required=True, help="Archivo con la lista de tickers y PER")
    args = parser.parse_args()
    
    sys.exit(encontrar_menor_per(args.file))

