#!/usr/bin/env python3
"""
ift_sns.py
IFT Plan Nacional de Numeración — builds SQLite from local CSV.
Auto-detects pnn_Publico_*.csv in ~/mexicosint/data/
"""

import os
import csv
import sqlite3
import glob

MODULE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.dirname(MODULE_DIR)
DATA_DIR = os.path.join(PROJECT_DIR, "data")
DB_PATH = os.path.join(DATA_DIR, "ift_pnn.db")


def _find_csv():
    """Find the IFT CSV file in data dir."""
    pattern = os.path.join(DATA_DIR, "pnn_Publico_*.csv")
    files = glob.glob(pattern)
    if not files:
        raise FileNotFoundError(f"No pnn_Publico_*.csv found in {DATA_DIR}")
    return files[0]  # Use first match


def _build_db():
    """Parse CSV and build indexed SQLite database."""
    csv_path = _find_csv()
    print(f"[*] Building IFT database from {os.path.basename(csv_path)}...")

    # Remove old DB
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)

    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    c.execute("""
        CREATE TABLE pnn (
            zona INTEGER,
            numeracion_inicial TEXT,
            numeracion_final TEXT,
            ocupacion INTEGER,
            modalidad TEXT,
            razon_social TEXT,
            fecha_asignacion TEXT
        )
    """)
    c.execute("CREATE INDEX idx_range ON pnn(numeracion_inicial, numeracion_final)")

    with open(csv_path, "r", encoding="utf-8", errors="ignore") as f:
        reader = csv.reader(f)
        raw_headers = next(reader)
        headers = [h.strip() for h in raw_headers]

        # Map columns
        idx_zona = headers.index("ZONA")
        idx_ini = headers.index("NUMERACION_INICIAL")
        idx_fin = headers.index("NUMERACION_FINAL")
        idx_ocu = headers.index("OCUPACION")
        idx_mod = headers.index("MODALIDAD")
        idx_raz = headers.index("RAZON_SOCIAL")
        idx_fec = headers.index("FECHA_ASIGNACION")

        rows = []
        total = 0
        for row in reader:
            if len(row) < 7:
                continue
            rows.append((
                row[idx_zona].strip(),
                row[idx_ini].strip(),
                row[idx_fin].strip(),
                row[idx_ocu].strip(),
                row[idx_mod].strip(),
                row[idx_raz].strip(),
                row[idx_fec].strip()
            ))
            if len(rows) >= 5000:
                c.executemany("INSERT INTO pnn VALUES (?, ?, ?, ?, ?, ?, ?)", rows)
                total += len(rows)
                rows = []
        if rows:
            c.executemany("INSERT INTO pnn VALUES (?, ?, ?, ?, ?, ?, ?)", rows)
            total += len(rows)

    conn.commit()
    conn.close()
    print(f"[+] Database built: {DB_PATH} ({total} rows)")


def init_db(force_rebuild=False):
    """Build DB if missing or forced."""
    if os.path.exists(DB_PATH) and not force_rebuild:
        return
    _build_db()


def consultar(numero_10: str) -> dict:
    """
    Query the local IFT database for a 10-digit number.
    """
    result = {
        "source": "IFT PNN (local DB)",
        "numero": numero_10,
        "found": False,
        "zona": None,
        "modalidad": "Unknown",
        "carrier": "Unknown",
        "razon_social": "Unknown",
        "fecha_asignacion": None,
        "error": None,
    }

    if not numero_10.isdigit() or len(numero_10) != 10:
        result["error"] = "Invalid 10-digit number"
        return result

    try:
        init_db()
    except Exception as e:
        result["error"] = f"DB init failed: {e}"
        return result

    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    c.execute("""
        SELECT zona, modalidad, razon_social, fecha_asignacion
        FROM pnn
        WHERE numeracion_inicial <= ? AND numeracion_final >= ?
        LIMIT 1
    """, (numero_10, numero_10))

    row = c.fetchone()
    conn.close()

    if row:
        result["found"] = True
        result["zona"] = row[0]
        result["modalidad"] = row[1]
        result["razon_social"] = row[2]
        result["carrier"] = row[2]
        result["fecha_asignacion"] = row[3]

    return result


if __name__ == "__main__":
    import sys
    import json
    test = sys.argv[1] if len(sys.argv) > 1 else "6636334933"
    print(json.dumps(consultar(test), indent=2, ensure_ascii=False))
