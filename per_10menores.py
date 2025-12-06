#!/usr/bin/env python3
import sys
import argparse

def encontrar_top_10_menores_per(archivo, top_n=10):
    pers = []
    
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
                    pers.append((per, ticker))
                except ValueError:
                    print(f"Línea {linea_num}: No se pudo convertir '{second}' a float", file=sys.stderr)
                    continue
        
        if not pers:
            print("No se encontraron valores PER válidos", file=sys.stderr)
            return 1
        
        # Ordenar por PER ascendente y tomar top N
        pers.sort(key=lambda x: x[0])
        top_pers = pers[:top_n]
        
        print(f"\nTop {top_n} menores PERs:")
        print("-" * 30)
        for i, (per, ticker) in enumerate(top_pers, 1):
            print(f"{i:2d}. {ticker:8s} {per:6.2f}")
        
        return 0
        
    except FileNotFoundError:
        print(f"Error: Archivo '{archivo}' no encontrado", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"Error leyendo archivo: {e}", file=sys.stderr)
        return 1

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Encuentra los N menores PER válidos en un archivo")
    parser.add_argument("-f", "--file", required=True, help="Archivo con la lista de tickers y PER")
    parser.add_argument("-n", "--top", type=int, default=10, help="Cantidad de menores PERs a mostrar (default: 10)")
    args = parser.parse_args()
    
    sys.exit(encontrar_top_10_menores_per(args.file, args.top))

