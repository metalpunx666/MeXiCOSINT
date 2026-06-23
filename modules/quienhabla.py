#!/usr/bin/env python3
"""
quienhabla.py
Scraper for quienhabla.mx — crowdsourced phone intel.

INPUT FORMAT: Accepts ANY format — auto-normalizes to 10 digits:
  • +52 1 66 3633 4933  → 6636334933
  • 5216636334933       → 6636334933
  • 66-3633-4933        → 6636334933
  • 6636334933          → 6636334933 (already clean)

WHEN TO USE +52 (COUNTRY CODE):
  • phonenumbers library (E164 standard) → needs +52
  • International APIs / SIP / VoIP     → needs +52
  • Mexican web scrapers (quienhabla, SNS IFT) → NO +52, just 10 digits
  • Mexican SMS gateways                → usually 10 digits or 52XXXXXXXXXX

No auth needed for quienhabla. Rate limited to 1 req/sec.
"""

import requests
import time
import re
from bs4 import BeautifulSoup

BASE_URL = "https://www.quienhabla.mx"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "es-MX,es;q=0.9",
}

JUNK_PATTERNS = [
    "aviso de privacidad",
    "quienhabla",
    "no hay comentarios",
    "cookies",
    "politica",
    "terminos",
    "condiciones",
    "contacto",
    "publicidad",
    "registrar",
    "iniciar sesion",
    "login",
    "registro",
    "buscar",
    "numeros",
    "telefono",
    "compartir",
    "reportar",
    "bloquear",
    "desbloquear",
]

# City to state mapping for Mexican cities commonly found on quienhabla.mx
CIUDAD_TO_ESTADO = {
    "tijuana": "Baja California",
    "mexicali": "Baja California",
    "ensenada": "Baja California",
    "tecate": "Baja California",
    "rosarito": "Baja California",
    "ciudad de mexico": "Ciudad de México",
    "cdmx": "Ciudad de México",
    "guadalajara": "Jalisco",
    "monterrey": "Nuevo León",
    "puebla": "Puebla",
    "leon": "Guanajuato",
    "queretaro": "Querétaro",
    "san luis potosi": "San Luis Potosí",
    "merida": "Yucatán",
    "cancun": "Quintana Roo",
    "playa del carmen": "Quintana Roo",
    "culiacan": "Sinaloa",
    "mazatlan": "Sinaloa",
    "los mochis": "Sinaloa",
    "hermosillo": "Sonora",
    "nogales": "Sonora",
    "ciudad juarez": "Chihuahua",
    "chihuahua": "Chihuahua",
    "saltillo": "Coahuila",
    "torreon": "Coahuila",
    "monclova": "Coahuila",
    "acapulco": "Guerrero",
    "chilpancingo": "Guerrero",
    "oaxaca": "Oaxaca",
    "veracruz": "Veracruz",
    "cordoba": "Veracruz",
    "coatzacoalcos": "Veracruz",
    "poza rica": "Veracruz",
    "tuxtla gutierrez": "Chiapas",
    "tapachula": "Chiapas",
    "villahermosa": "Tabasco",
    "campeche": "Campeche",
    "ciudad del carmen": "Campeche",
    "chetumal": "Quintana Roo",
    "colima": "Colima",
    "manzanillo": "Colima",
    "tepic": "Nayarit",
    "puerto vallarta": "Jalisco",
    "aguascalientes": "Aguascalientes",
    "durango": "Durango",
    "morelia": "Michoacán",
    "uruapan": "Michoacán",
    "zamora": "Michoacán",
    "apatzingan": "Michoacán",
    "lazaro cardenas": "Michoacán",
    "irapuato": "Guanajuato",
    "celaya": "Guanajuato",
    "salamanca": "Guanajuato",
    "san miguel de allende": "Guanajuato",
    "pachuca": "Hidalgo",
    "tulancingo": "Hidalgo",
    "tula": "Hidalgo",
    "cuernavaca": "Morelos",
    "cuautla": "Morelos",
    "jojutla": "Morelos",
    "tampico": "Tamaulipas",
    "ciudad victoria": "Tamaulipas",
    "nuevo laredo": "Tamaulipas",
    "reynosa": "Tamaulipas",
   "matamoros": "Tamaulipas",
    "zacatecas": "Zacatecas",
    "fresnillo": "Zacatecas",
    "jerez": "Zacatecas",
    "tlaxcala": "Tlaxcala",
    "la paz": "Baja California Sur",
    "los cabos": "Baja California Sur",
    "loreto": "Baja California Sur",
    "santiago de queretaro": "Querétaro",
    "toluca": "Estado de México",
    "ecatepec": "Estado de México",
    "neza": "Estado de México",
    "neza": "Estado de México",
    "ciudad nezahualcoyotl": "Estado de México",
}
def _normalize_mx_10(raw: str) -> str:
    cleaned = raw.strip().replace("-", "").replace(" ", "").replace("(", "").replace(")", "")
    if cleaned.startswith("+52"):
        cleaned = cleaned[3:]
    elif cleaned.startswith("52"):
        cleaned = cleaned[2:]
    if len(cleaned) == 11 and cleaned.startswith("1"):
        cleaned = cleaned[1:]
    if not cleaned.isdigit() or len(cleaned) != 10:
        raise ValueError(f"Cannot normalize to 10 digits: got '{cleaned}' ({len(cleaned)} chars)")
    return cleaned


def _is_junk(text: str) -> bool:
    if not text or len(text) < 3:
        return True
    t = text.lower().strip()
    for junk in JUNK_PATTERNS:
        if junk in t:
            return True
    if len(t) < 5 and t.replace(".", "").replace(",", "").isdigit():
        return True
    return False


def _extract_label_value(soup: BeautifulSoup, label_text: str) -> str | None:
    label_text_lower = label_text.lower()
    for dt in soup.find_all("dt"):
        dt_text = dt.get_text(strip=True).lower()
        if label_text_lower in dt_text:
            dd = dt.find_next_sibling("dd")
            if dd:
                val = dd.get_text(strip=True)
                if val and not _is_junk(val):
                    return val
    for elem in soup.find_all(["div", "span", "p", "li", "td"]):
        elem_text = elem.get_text(strip=True).lower()
        if label_text_lower in elem_text and len(elem_text) < len(label_text) + 20:
            nxt = elem.find_next_sibling()
            if nxt:
                val = nxt.get_text(strip=True)
                if val and not _is_junk(val):
                    return val
            for child in elem.children:
                if hasattr(child, 'get_text'):
                    child_text = child.get_text(strip=True)
                    if child_text and label_text_lower not in child_text.lower():
                        if not _is_junk(child_text):
                            return child_text
    for cls_keyword in ["compania", "carrier", "telefono", "tipo", "ciudad", "estado", "municipio", "modo", "busqueda"]:
        elems = soup.find_all(class_=lambda x: x and cls_keyword in str(x).lower())
        for elem in elems:
            val = elem.get_text(strip=True)
            if val and not _is_junk(val) and len(val) < 100:
                if label_text_lower not in val.lower():
                    return val
    texto = soup.get_text(separator="\n")
    patterns = [
        rf'{re.escape(label_text)}\s*[:\-]?\s*\n?\s*([^\n]+?)(?=\n|$)',
        rf'{re.escape(label_text)}\s*[:\-]?\s*([^\n]+?)(?=\n|$)',
        rf'{re.escape(label_text)}\s*[:\-]?\s*([A-Za-zÁÉÍÓÚáéíóúÑñ0-9\s\-\.]+?)(?=\n|$)',
    ]
    for pattern in patterns:
        match = re.search(pattern, texto, re.IGNORECASE)
        if match:
            val = match.group(1).strip()
            if val and not _is_junk(val) and len(val) < 100:
                return val
    return None


def _extract_comments(soup: BeautifulSoup) -> list[str]:
    comments = []
    for cls in ["comment", "comentario", "review", "opinion", "reporte", "feedback", "testimonial", "entry", "post", "message", "mensaje", "report"]:
        elems = soup.find_all(class_=lambda x: x and cls in str(x).lower())
        for elem in elems:
            txt = elem.get_text(strip=True)
            if txt and len(txt) > 10 and not _is_junk(txt):
                comments.append(txt)
    for elem in soup.find_all(["article", "div", "li"]):
        has_meta = elem.find(class_=lambda x: x and any(k in str(x).lower() for k in ["time", "fecha", "date", "user", "usuario", "author", "autor"]))
        if has_meta:
            txt = elem.get_text(strip=True)
            if txt and len(txt) > 15 and not _is_junk(txt):
                for meta in elem.find_all(["time", "span", "div"], class_=lambda x: x and any(k in str(x).lower() for k in ["time", "fecha", "date", "user", "usuario"])):
                    txt = txt.replace(meta.get_text(strip=True), "", 1)
                txt = txt.strip()
                if txt and len(txt) > 10 and txt not in comments:
                    comments.append(txt)
    for p in soup.find_all("p"):
        parent_names = [ancestor.name for ancestor in p.parents if ancestor.name]
        if any(name in ["nav", "footer", "header", "aside"] for name in parent_names):
            continue
        txt = p.get_text(strip=True)
        if txt and len(txt) > 15 and not _is_junk(txt):
            link_text = "".join(a.get_text(strip=True) for a in p.find_all("a"))
            if len(link_text) < len(txt) * 0.5 and txt not in comments:
                comments.append(txt)
    full = soup.get_text(separator=" ")
    if ("no hay comentarios" in full.lower() or "sin comentarios" in full.lower()) and not comments:
        return ["No hay comentarios para este número."]
    seen = set()
    unique = []
    for c in comments:
        cc = re.sub(r'\s+', ' ', c).strip()
        if cc.lower() not in seen and len(cc) > 5:
            seen.add(cc.lower())
            unique.append(cc)
    return unique[:10]


def _extract_reportes(soup: BeautifulSoup) -> int:
    full = soup.get_text(separator=" ")
    patterns = [
        r'(\d+)\s+(comentarios?|reportes?|veces|b[uú]squedas?)',
        r'(\d+)\s+(personas?\s+han?\s+(buscado|reportado|comentado))',
        r'(\d+)\s+(resultados?|entradas?|registros?)',
        r'(\d+)\s+(veces\s+buscado)',
    ]
    for pattern in patterns:
        match = re.search(pattern, full, re.IGNORECASE)
        if match:
            try:
                return int(match.group(1))
            except ValueError:
                pass
    return 0


def consultar(raw_numero: str) -> dict:
    result = {
        "source": "quienhabla.mx",
        "input": raw_numero,
        "numero_10": None,
        "url": None,
        "found": False,
        "carrier": "Unknown",
        "tipo": "Unknown",
        "ciudad": "Unknown",
        "estado": "Unknown",
        "reportes": 0,
        "comentarios": [],
        "error": None,
    }
    try:
        numero_10 = _normalize_mx_10(raw_numero)
    except ValueError as e:
        result["error"] = str(e)
        return result
    result["numero_10"] = numero_10
    formatted = f"{numero_10[:2]}-{numero_10[2:6]}-{numero_10[6:]}"
    url = f"{BASE_URL}/{formatted}/"
    result["url"] = url
    try:
        time.sleep(1.0)
        r = requests.get(url, headers=HEADERS, timeout=15)
        r.raise_for_status()
    except requests.RequestException as e:
        result["error"] = f"Request failed: {e}"
        return result
    if r.status_code != 200:
        result["error"] = f"HTTP {r.status_code}"
        return result
    soup = BeautifulSoup(r.text, "html.parser")
    carrier = _extract_label_value(soup, "Compañía de teléfono") or _extract_label_value(soup, "Compañía") or _extract_label_value(soup, "Operadora")
    tipo = _extract_label_value(soup, "Tipo") or _extract_label_value(soup, "Modo")
    ciudad = _extract_label_value(soup, "Ciudad") or _extract_label_value(soup, "Municipio")
    estado = _extract_label_value(soup, "Estado")
    # Fallback: derive estado from ciudad if not found on page
    if (not estado or estado == "Unknown") and ciudad and ciudad != "Unknown":
        ciudad_key = ciudad.lower().strip()
        if ciudad_key in CIUDAD_TO_ESTADO:
            estado = CIUDAD_TO_ESTADO[ciudad_key]
            result["found"] = True
    if carrier and carrier != "Unknown":
        result["found"] = True
        result["carrier"] = carrier
    if tipo and tipo != "Unknown":
        result["tipo"] = tipo
    if ciudad and ciudad != "Unknown":
        result["ciudad"] = ciudad
    if estado and estado != "Unknown":
        result["estado"] = estado
    if any(v not in ("Unknown", None, "") for v in [carrier, tipo, ciudad, estado]):
        result["found"] = True
    result["reportes"] = _extract_reportes(soup)
    result["comentarios"] = _extract_comments(soup)
    if not result["found"] and not result["comentarios"]:
        full_text = soup.get_text(separator=" ").lower()
        if any(k in full_text for k in ["no encontrado", "not found", "error"]):
            result["error"] = "Page returned 'not found' or error content"
        elif any(k in full_text for k in ["no hay información", "sin información"]):
            result["error"] = "No information available for this number"
    return result


if __name__ == "__main__":
    import sys
    import json
    test = sys.argv[1] if len(sys.argv) > 1 else "5512345678"
    print(json.dumps(consultar(test), indent=2, ensure_ascii=False))
