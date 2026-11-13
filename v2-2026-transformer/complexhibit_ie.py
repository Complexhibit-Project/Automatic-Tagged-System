"""Complexhibit: extracción de información de catálogos en tres niveles.

Nivel 1  bloques:   catalogueItem (ITEM) y exhibition (EXHIB)        -> modelo BIO
Nivel 2  entidades: persName, title, institution, placeName, date...  -> modelo BIO
Nivel 3  detalle:   dimensiones y fechas                              -> reglas
                    roles y tipos (person.role, institution.type...)  -> clasificador

Este módulo contiene todo lo que no depende del modelo: lectura de GATE,
conversión a BIO, reglas, ejemplos para el clasificador de atributos,
decodificación de predicciones y montaje de la salida anidada.
"""
import json
import re
import xml.etree.ElementTree as ET
from fractions import Fraction
from pathlib import Path

# ----------------------------------------------------------------------------
# Esquema (según el Manual de etiquetado v1)
# ----------------------------------------------------------------------------
# El orden de cada diccionario fija la prioridad si dos anotaciones se solapan.
NIVEL2 = {
    "persName": "PER",
    "title": "TITLE",
    "institution": "ORG",
    "venue": "ORG",
    "placeName": "LOC",
    "date": "DATE",
    "technique": "TECH",
    "material": "TECH",
    "dimensions": "DIM",
    "address": "ADDR",
    "idno": "IDNO",
}
NIVEL1 = {
    "catalogueItem": "ITEM",
    "exhibition": "EXHIB",
}
# Atributos que aprende el clasificador del nivel 3: (tipo GATE, rasgo)
ATRIBUTOS = [
    ("person", "role"),
    ("institution", "type"),
    ("institution", "role"),
    ("work", "type"),
    ("technique", "type"),
]

# Reemplazo global erróneo detectado en el corpus: al renombrar valores de
# atributos (city -> poblation, material -> technique) se modificó también
# el texto. Se corrige solo el texto de cada palabra; las posiciones no cambian.
TOKEN_FIXES = [
    (re.compile(r"poblation"), "city"),
    (re.compile(r"techniqueity"), "materiality"),
    (re.compile(r"techniquely"), "materially"),
    (re.compile(r"detechniqueiz"), "dematerializ"),
]

TOKEN_RE = re.compile(r"\w+(?:[-'’]\w+)*|[^\w\s]", re.UNICODE)


# ----------------------------------------------------------------------------
# Lectura de textos etiquetados con GATE
# ----------------------------------------------------------------------------
def load_gate(path):
    """Devuelve (texto, anotaciones) con anotaciones = [(tipo, ini, fin, rasgos)]."""
    root = ET.parse(path).getroot()
    tw = root.find("TextWithNodes")
    text = tw.text or ""
    offsets = {}
    for node in tw:
        offsets[int(node.get("id"))] = len(text)
        text += node.tail or ""
    anns = []
    for aset in root.findall("AnnotationSet"):
        for a in aset.findall("Annotation"):
            s = offsets.get(int(a.get("StartNode")), int(a.get("StartNode")))
            e = offsets.get(int(a.get("EndNode")), int(a.get("EndNode")))
            feats = {f.find("Name").text: (f.find("Value").text or "") for f in a.findall("Feature")}
            if e > s:
                anns.append((a.get("Type"), s, e, feats))
    return text, anns


def fix_token(tok):
    for pat, rep in TOKEN_FIXES:
        tok = pat.sub(rep, tok)
    return tok


def tokenize(text):
    return [(m.group(), m.start(), m.end()) for m in TOKEN_RE.finditer(text)]


# ----------------------------------------------------------------------------
# Conversión a BIO
# ----------------------------------------------------------------------------
def resolve_overlaps(spans, prioridad):
    spans = sorted(spans, key=lambda x: (prioridad.index(x[2]), -(x[1] - x[0])))
    kept = []
    for s, e, t in spans:
        if all(e <= ks or s >= ke for ks, ke, _ in kept):
            kept.append((s, e, t))
    return sorted(kept)


def to_bio(tokens, spans, mapa):
    tags = ["O"] * len(tokens)
    for s, e, t in spans:
        inside = [i for i, (_, ts, te) in enumerate(tokens) if ts < e and te > s]
        for k, i in enumerate(inside):
            tags[i] = ("B-" if k == 0 else "I-") + mapa[t]
    return tags


def segment_bounds(tokens, text, tags=None, max_tokens=200):
    """Índices [ini, fin) de fragmentos: se corta en líneas en blanco o al llegar
    a max_tokens, sin partir nunca una entidad."""
    bounds, start = [], 0
    for i, (_, s, e) in enumerate(tokens):
        nxt = tokens[i + 1] if i + 1 < len(tokens) else None
        if nxt is None:
            bounds.append((start, i + 1))
            break
        inside_next = tags is not None and tags[i + 1].startswith("I-")
        gap = text[e:nxt[1]]
        if not inside_next and ("\n\n" in gap or i + 1 - start >= max_tokens):
            bounds.append((start, i + 1))
            start = i + 1
    return bounds


def documento_bio(path, mapa, max_tokens=200):
    text, anns = load_gate(path)
    spans = [(s, e, t) for t, s, e, _ in anns if t in mapa]
    tokens = tokenize(text)
    tags = to_bio(tokens, resolve_overlaps(spans, list(mapa)), mapa)
    filas = []
    for k, (a, b) in enumerate(segment_bounds(tokens, text, tags, max_tokens)):
        filas.append({
            "doc": Path(path).stem, "seg": k,
            "tokens": [fix_token(t[0]) for t in tokens[a:b]],
            "tags": tags[a:b],
        })
    return filas


def construir_bio(carpeta, mapa, salida, max_tokens=200):
    n, stats = 0, {}
    with open(salida, "w", encoding="utf-8") as fh:
        for p in sorted(Path(carpeta).rglob("*.xml")):
            try:
                filas = documento_bio(p, mapa, max_tokens)
            except ET.ParseError as err:
                print(f"AVISO: no se pudo leer {p.name}: {err}")
                continue
            for f in filas:
                fh.write(json.dumps(f, ensure_ascii=False) + "\n")
                for t in f["tags"]:
                    if t.startswith("B-"):
                        stats[t[2:]] = stats.get(t[2:], 0) + 1
            n += 1
    print(f"{n} documentos -> {salida}")
    print("Entidades por etiqueta:", dict(sorted(stats.items(), key=lambda x: -x[1])))
    return stats


# ----------------------------------------------------------------------------
# Nivel 3a: reglas de dimensiones
# ----------------------------------------------------------------------------
_NUM = r"\d+(?:[.,]\d+)?(?:\s+\d+/\d+)?|\d+/\d+"


def _valor(s):
    s = s.strip().replace(",", ".")
    try:
        return float(sum(Fraction(p) for p in s.split()))
    except (ValueError, ZeroDivisionError):
        return None


def parse_dimensions(texto, unidad_defecto=None):
    """'93 x 19 x 16' -> {'height': 93.0, 'width': 19.0, 'depth': 16.0, 'unit': ...}
    Convención de los catálogos: alto x ancho x fondo."""
    t = texto.lower()
    out = {}
    if re.search(r"\b(lbs?|pounds?)\b", t):
        out["unit"] = "libra"
    elif re.search(r"(?<![a-záéíóú])kg\b|kilo", t):
        out["unit"] = "kg"
    elif re.search(r"\bfeet\b|(?<![a-záéíóú])ft\b|\bpies\b", t):
        out["unit"] = "feet"
    elif re.search(r"(?<![a-záéíóú])cm\b", t):
        out["unit"] = "cm"
    elif re.search(r"(?<![a-záéíóú])mm\b", t):
        out["unit"] = "mm"
    elif re.search(r"(?<![a-záéíóú])m\b|metros", t):
        out["unit"] = "m"
    elif '"' in t or "inch" in t or "pulgada" in t or "in." in t:
        out["unit"] = "inches"
    if "unit" not in out and unidad_defecto:
        out["unit"] = unidad_defecto
    nums = re.findall(_NUM, t)
    if out.get("unit") in ("libra", "kg"):
        if nums:
            out["weight"] = _valor(nums[0])
        return out
    if re.search(r"\bdi[aá]m|ø|⌀", t) and nums:
        out["diameter"] = _valor(nums[0])
        return out
    rango = re.search(rf"({_NUM})\s+(?:to|a|-)\s+({_NUM})\s+(?:feet|ft|pies|cm|m)?\s*(?:in height|de alto|alto)", t)
    if rango:
        out["height"] = (_valor(rango.group(1)), _valor(rango.group(2)))
        return out
    if re.search(r"in height|de alto|\balto\b", t) and nums:
        out["height"] = _valor(nums[0])
        return out
    partes = re.split(r"\s*[x×]\s*", t)
    vals = [_valor(m.group()) for p in partes for m in [re.search(_NUM, p)] if m]
    for clave, v in zip(("height", "width", "depth"), vals):
        out[clave] = v
    return out


def unidad_documento(text):
    """Unidad declarada para todo el catálogo, p. ej. 'All dimensions are given
    in inches' o 'Medidas en centímetros'."""
    t = text.lower()
    m = re.search(r"\b(dimensions?|measurements?|medidas|dimensiones)\b[^.\n;]{0,30}?\b(?:in|en)\s+(inches|inch|cent[ií]met\w*|cm|metros|feet)\b", t)
    if not m:
        return None
    u = m.group(2)
    return "inches" if u.startswith("inch") else "feet" if u == "feet" else "m" if u == "metros" else "cm"


def unidad_mayoritaria(frases):
    """Unidad explícita más frecuente entre las dimensiones de un catálogo: se usa
    para las medidas que no indican unidad (p. ej. '19 5/8 x 29 13/16')."""
    cuenta = {}
    for f in frases:
        u = parse_dimensions(f).get("unit")
        if u and u not in ("libra", "kg"):   # solo unidades de longitud
            cuenta[u] = cuenta.get(u, 0) + 1
    return max(cuenta, key=cuenta.get) if cuenta else None


def unidad_por_defecto(text, frases):
    """Primero la unidad declarada en el catálogo ('dimensions are given in inches');
    si no la hay, la más frecuente entre sus medidas."""
    return unidad_documento(text) or unidad_mayoritaria(frases)


def dimensiones_oro(text, anns):
    """Pares (texto de la dimensión, valores anotados) para evaluar las reglas."""
    res = []
    for t, s, e, f in anns:
        if t != "dimensions":
            continue
        oro = {"unit": f.get("unit")} if f.get("unit") else {}
        for t2, s2, e2, _ in anns:
            if t2 in ("height", "width", "depth", "weight", "diameter") and s <= s2 and e2 <= e:
                v = text[s2:e2]
                m = re.match(rf"\s*({_NUM})\s+(?:to|a|-)\s+({_NUM})\s*$", v)
                oro[t2] = (_valor(m.group(1)), _valor(m.group(2))) if m else _valor(v)
        res.append((text[s:e], oro))
    return res


# ----------------------------------------------------------------------------
# Nivel 3b: reglas de fechas (formato ISO del manual: when / from-to)
# ----------------------------------------------------------------------------
MESES = {
    "jan": 1, "january": 1, "enero": 1, "ene": 1,
    "feb": 2, "february": 2, "febrero": 2,
    "mar": 3, "march": 3, "marzo": 3,
    "apr": 4, "april": 4, "abril": 4, "abr": 4,
    "may": 5, "mayo": 5,
    "jun": 6, "june": 6, "junio": 6,
    "jul": 7, "july": 7, "julio": 7,
    "aug": 8, "august": 8, "agosto": 8, "ago": 8,
    "sep": 9, "sept": 9, "september": 9, "septiembre": 9, "setiembre": 9,
    "oct": 10, "october": 10, "octubre": 10,
    "nov": 11, "november": 11, "noviembre": 11,
    "dec": 12, "december": 12, "diciembre": 12, "dic": 12,
}
_DIAS_MES = [31, 29, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]


def _ultimo_dia(y, m):
    if m == 2:
        return 29 if (y % 4 == 0 and (y % 100 != 0 or y % 400 == 0)) else 28
    return _DIAS_MES[m - 1]


_RANGO_INCIERTO = re.compile(r"^\W*(\d{4})\s*[-–—]\s*(\d{2}|\d{4})\s*/\s*(\d{4})\W*$")
_ANIO_ABREV = re.compile(r"\b(\d{2})(\d{2})\s*[-–—]\s*(\d{2})(?![\d/])")


def parse_date(texto):
    t = texto.lower().replace("’", "'")
    # '1920-21/1987': fecha de creación incierta (1920 o 1921) y fecha posterior (p. ej., estampación)
    m = _RANGO_INCIERTO.match(t)
    if m:
        a, b, c = m.groups()
        b = a[:2] + b if len(b) == 2 else b
        return {"notBefore": a, "notAfter": b, "to": c}
    # '1969-71' -> '1969 - 1971'
    t = _ANIO_ABREV.sub(lambda m: f"{m.group(1)}{m.group(2)} - {m.group(1)}{m.group(3)}", t)
    toks = re.findall(r"[a-záéíóúñ]+|\d+", t)
    fechas = []  # lista de [dia, mes, año] en orden de aparición
    cur = [None, None, None]
    for tok in toks:
        if tok.isdigit():
            n = int(tok)
            if len(tok) == 4 and 1000 <= n <= 2100:
                cur[2] = n
                fechas.append(cur)
                cur = [None, None, None]
            elif n <= 31:
                if cur[0] is not None:  # nuevo día sin año: cerrar el anterior
                    fechas.append(cur)
                    cur = [None, None, None]
                cur[0] = n
        elif tok in MESES:
            if cur[1] is not None:
                fechas.append(cur)
                cur = [None, None, None]
            cur[1] = MESES[tok]
    if cur != [None, None, None]:
        fechas.append(cur)
    # formatos numéricos dd/mm/aaaa
    num = [x for x in re.findall(r"(\d{1,2})[/.-](\d{1,2})[/.-](\d{4})", t) if 1 <= int(x[1]) <= 12]
    if num:
        fechas = [[int(d), int(m), int(y)] for d, m, y in num]
    fechas = [f for f in fechas if any(x is not None for x in f)]
    if not fechas:
        return {}
    # el año (y el mes) se propagan hacia atrás: "9 January-6 March, 1998"
    for i in range(len(fechas) - 2, -1, -1):
        if fechas[i][2] is None:
            fechas[i][2] = fechas[i + 1][2]
            if fechas[i][1] is None:
                fechas[i][1] = fechas[i + 1][1]
    if any(f[2] is None for f in fechas):
        return {}
    # el mes se propaga hacia delante en rangos de días: 'June 20-26, 1963'
    for i in range(1, len(fechas)):
        if fechas[i][1] is None and fechas[i][0] is not None and fechas[i - 1][1] is not None:
            fechas[i][1] = fechas[i - 1][1]

    def iso(f, fin=False):
        d, m, y = f
        if m is None:
            return f"{y:04d}" if not fin else f"{y:04d}"
        if d is None:
            d = _ultimo_dia(y, m) if fin else 1
        return f"{y:04d}-{m:02d}-{d:02d}"

    if len(fechas) == 1:
        f = fechas[0]
        if f[1] is None:
            return {"when": f"{f[2]:04d}"}
        if f[0] is None:  # mes y año: intervalo del mes
            return {"from": iso(f), "to": iso(f, fin=True)}
        return {"when": iso(f)}
    return {"from": iso(fechas[0]), "to": iso(fechas[-1], fin=True)}


def fechas_oro(text, anns):
    res = []
    for t, s, e, f in anns:
        if t == "date":
            oro = {k: v for k, v in f.items() if k in ("when", "from", "to", "notBefore", "notAfter")}
            if oro:
                res.append((text[s:e], oro))
    return res


def evaluar_reglas(carpeta, docs=None):
    """Exactitud de las reglas frente a los valores anotados a mano."""
    dim_ok = dim_n = fec_ok = fec_n = 0
    errores = {"dimensiones": [], "fechas": []}
    for p in sorted(Path(carpeta).rglob("*.xml")):
        if docs is not None and p.stem not in docs:
            continue
        try:
            text, anns = load_gate(p)
        except ET.ParseError:
            continue
        pares = dimensiones_oro(text, anns)
        udoc = unidad_por_defecto(text, [f for f, _ in pares])
        for frase, oro in pares:
            pred = parse_dimensions(frase, udoc)
            campos = [k for k in oro if k != "unit"]
            ok = all(pred.get(k) == oro[k] for k in campos) and (not oro.get("unit") or pred.get("unit") == oro["unit"])
            dim_n += 1
            dim_ok += ok
            if not ok and len(errores["dimensiones"]) < 30:
                errores["dimensiones"].append({"texto": frase, "oro": oro, "regla": pred, "doc": p.stem})
        for frase, oro in fechas_oro(text, anns):
            pred = parse_date(frase)
            ok = pred == oro
            fec_n += 1
            fec_ok += ok
            if not ok and len(errores["fechas"]) < 30:
                errores["fechas"].append({"texto": frase, "oro": oro, "regla": pred, "doc": p.stem})
    return {
        "dimensiones": {"n": dim_n, "exactitud": dim_ok / dim_n if dim_n else None},
        "fechas": {"n": fec_n, "exactitud": fec_ok / fec_n if fec_n else None},
        "errores": errores,
    }


# ----------------------------------------------------------------------------
# Nivel 3c: ejemplos para el clasificador de roles y tipos
# ----------------------------------------------------------------------------
VENTANA = 250  # caracteres de contexto a cada lado


def con_marcas(text, s, e, ventana=VENTANA):
    a, b = max(0, s - ventana), min(len(text), e + ventana)
    frag = text[a:s] + " [E] " + text[s:e] + " [/E] " + text[e:b]
    frag = " ".join(fix_token(w) for w in frag.split())
    return frag


def ejemplos_atributos(carpeta):
    filas = []
    for p in sorted(Path(carpeta).rglob("*.xml")):
        try:
            text, anns = load_gate(p)
        except ET.ParseError:
            continue
        for t, s, e, f in anns:
            for tipo, rasgo in ATRIBUTOS:
                if t == tipo and f.get(rasgo, "").strip():
                    valor = re.sub(r"\s*,\s*", ", ", f[rasgo].strip().lstrip("_"))
                    filas.append({
                        "doc": p.stem, "atributo": f"{tipo}.{rasgo}",
                        "texto": f"{tipo}.{rasgo}: " + con_marcas(text, s, e),
                        "valor": valor,
                    })
    return filas


# ----------------------------------------------------------------------------
# Inferencia de etiquetas por palabra a fragmentos y a una salida anidada
# ----------------------------------------------------------------------------
def bio_a_spans(tokens, tags):
    """tokens = [(palabra, ini, fin)], tags = ['B-PER', ...] -> [(ini, fin, 'PER')]"""
    spans, cur = [], None
    for (w, s, e), tag in zip(tokens, tags):
        if tag.startswith("B-") or (tag.startswith("I-") and (cur is None or cur[2] != tag[2:])):
            if cur:
                spans.append(tuple(cur))
            cur = [s, e, tag[2:]]
        elif tag.startswith("I-") and cur:
            cur[1] = e
        else:
            if cur:
                spans.append(tuple(cur))
            cur = None
    if cur:
        spans.append(tuple(cur))
    return spans


def montar_salida(text, spans_n1, spans_n2, atributos=None):
    """Combina niveles 1, 2 y 3 en una estructura anidada (al estilo del manual).
    atributos: dict {(ini, fin): {'person.role': 'creator', ...}}"""
    atributos = atributos or {}
    udoc = unidad_por_defecto(text, [text[s:e] for s, e, lab in spans_n2 if lab == "DIM"])

    def entidad(s, e, lab):
        d = {"tipo": lab, "texto": text[s:e].strip(), "ini": s, "fin": e}
        if lab == "DIM":
            d["valores"] = parse_dimensions(text[s:e], udoc)
        if lab == "DATE":
            d["valores"] = parse_date(text[s:e])
        if (s, e) in atributos:
            d["atributos"] = atributos[(s, e)]
        return d

    bloques = []
    for s, e, lab in spans_n1:
        hijos = [entidad(s2, e2, l2) for s2, e2, l2 in spans_n2 if s <= s2 and e2 <= e]
        b = {"tipo": {"ITEM": "catalogueItem", "EXHIB": "exhibition"}.get(lab, lab),
             "texto": text[s:e].strip()[:300], "ini": s, "fin": e, "contenido": hijos}
        if (s, e) in atributos:
            b["atributos"] = atributos[(s, e)]
        bloques.append(b)
    dentro = {(s2, e2) for s, e, _ in spans_n1 for s2, e2, _ in spans_n2 if s <= s2 and e2 <= e}
    sueltas = [entidad(s, e, l) for s, e, l in spans_n2 if (s, e) not in dentro]
    return {"bloques": bloques, "entidades_fuera_de_bloques": sueltas}
