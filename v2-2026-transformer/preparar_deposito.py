"""Prepara el depósito de datos de Complexhibit (catálogos anotados).

Genera dos capas:
  abierto/      sin el texto íntegro de los catálogos (se puede publicar)
                - inventario_catalogos.csv  (identificador, nombre original, datos a completar)
                - anotaciones/<id>.json     anotaciones standoff: posiciones, etiqueta, rasgos y,
                                            solo para entidades cortas, el texto anotado
                - particion.json            entrenamiento / validación / prueba con los nuevos ids
                - estadisticas.csv          anotaciones por etiqueta y catálogo
                - README.md                 plantilla de descripción
  restringido/  con el texto íntegro (acceso restringido por derechos de autor)
                - gate/<id>.xml             ficheros GATE originales renombrados
                - bio/nivel1.jsonl, nivel2.jsonl   versión para aprendizaje automático

Uso: python preparar_deposito.py CARPETA_XML CARPETA_SALIDA [particion.json]
"""
import csv
import hashlib
import json
import re
import shutil
import sys
import unicodedata
import xml.etree.ElementTree as ET
from collections import Counter
from pathlib import Path

import complexhibit_ie as ie

# Entidades cuyo texto se incluye en la capa abierta (fragmentos cortos y factuales).
# Los bloques (catalogueItem, exhibition) se dan solo por posición.
CON_TEXTO = set(ie.NIVEL2) | {"height", "width", "depth", "weight", "diameter",
                              "person", "institution", "work", "technique"}
MAX_TEXTO = 200

_ES = {"de", "la", "el", "en", "y", "los", "las", "del", "por", "con", "una", "que", "obra", "sobre"}
_EN = {"the", "of", "and", "in", "on", "with", "by", "a", "is", "was", "work", "his", "her"}


def slug(nombre, maximo=40):
    s = unicodedata.normalize("NFKD", nombre).encode("ascii", "ignore").decode()
    s = re.sub(r"[^a-zA-Z0-9]+", "_", s).strip("_").lower()
    return s[:maximo].rstrip("_") or "catalogo"


def idioma(texto):
    pal = re.findall(r"[a-záéíóúñ]+", texto.lower()[:20000])
    es = sum(p in _ES for p in pal)
    en = sum(p in _EN for p in pal)
    if es + en < 20:
        return ""
    if es > 2 * en:
        return "es"
    if en > 2 * es:
        return "en"
    return "es/en"


def primera_linea(texto):
    for l in texto.splitlines():
        l = " ".join(l.split())
        if len(l) > 3:
            return l[:120]
    return ""


def arreglar(t):
    for pat, rep in ie.TOKEN_FIXES:
        t = pat.sub(rep, t)
    return t


def main(carpeta_xml, salida, particion_json=None):
    salida = Path(salida)
    if salida.exists():
        shutil.rmtree(salida)
    ab, rs = salida / "abierto", salida / "restringido"
    for d in (ab / "anotaciones", rs / "gate", rs / "bio"):
        d.mkdir(parents=True)

    part = {}
    if particion_json and Path(particion_json).exists():
        p = json.load(open(particion_json, encoding="utf-8"))
        part = {d: "prueba" for d in p.get("test", [])}
        part.update({d: "validacion" for d in p.get("validation", [])})

    ficheros = sorted(Path(carpeta_xml).rglob("*.xml"), key=lambda p: p.stem.lower())
    filas, stats, mapa, excluidos = [], [], {}, []
    n = 0
    for f in ficheros:
        try:
            texto, anns = ie.load_gate(f)
        except ET.ParseError as err:
            excluidos.append((f.name, f"XML no válido: {err}"))
            continue
        if not anns:
            excluidos.append((f.name, "sin anotaciones"))
            continue
        n += 1
        ident = f"cat_{n:03d}_{slug(f.stem)}"
        mapa[f.stem] = ident
        shutil.copy(f, rs / "gate" / f"{ident}.xml")
        anot = []
        for t, s, e, rasgos in sorted(anns, key=lambda a: (a[1], -a[2])):
            a = {"tipo": t, "ini": s, "fin": e}
            if rasgos:
                a["rasgos"] = rasgos
            if t in CON_TEXTO and e - s <= MAX_TEXTO:
                a["texto"] = arreglar(texto[s:e])
            anot.append(a)
        json.dump({
            "id": ident,
            "nombre_original": f.stem,
            "longitud_texto": len(texto),
            "sha256_texto": hashlib.sha256(texto.encode("utf-8")).hexdigest(),
            "nota": "Posiciones en caracteres sobre el texto del documento GATE original. "
                    "El texto íntegro no se incluye por derechos de autor; el resumen sha256 "
                    "permite comprobar que se dispone del mismo texto.",
            "anotaciones": anot,
        }, open(ab / "anotaciones" / f"{ident}.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
        cuenta = Counter(t for t, *_ in anns)
        for t, c in sorted(cuenta.items()):
            stats.append({"id": ident, "etiqueta": t, "n": c})
        filas.append({
            "id": ident,
            "nombre_original": f.stem,
            "particion": part.get(f.stem, "entrenamiento") if part else "",
            "idioma_estimado": idioma(texto),
            "primera_linea_del_texto": primera_linea(texto),
            "n_anotaciones": len(anns),
            "n_obras": cuenta.get("catalogueItem", 0),
            "referencia_bibliografica": "",
            "editor_o_institucion": "",
            "anio": "",
            "url_origen": "",
            "anotador": "",
        })

    with open(ab / "inventario_catalogos.csv", "w", encoding="utf-8-sig", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(filas[0]), delimiter=";")
        w.writeheader()
        w.writerows(filas)
    with open(ab / "estadisticas.csv", "w", encoding="utf-8-sig", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=["id", "etiqueta", "n"], delimiter=";")
        w.writeheader()
        w.writerows(stats)
    if part:
        json.dump({k: sorted(mapa[d] for d, v in part.items() if v == k and d in mapa)
                   for k in ("prueba", "validacion")},
                  open(ab / "particion.json", "w", encoding="utf-8"), indent=1)

    # Versión BIO (contiene el texto: capa restringida), con los nuevos identificadores
    for nivel, m in (("nivel1", ie.NIVEL1), ("nivel2", ie.NIVEL2)):
        with open(rs / "bio" / f"{nivel}.jsonl", "w", encoding="utf-8") as fh:
            for f in ficheros:
                if f.stem not in mapa:
                    continue
                for fila in ie.documento_bio(f, m):
                    fila["doc"] = mapa[f.stem]
                    fh.write(json.dumps(fila, ensure_ascii=False) + "\n")

    totales = Counter()
    for s in stats:
        totales[s["etiqueta"]] += s["n"]
    tabla = "\n".join(f"| {t} | {c} |" for t, c in totales.most_common())
    excl = "\n".join(f"- {a}: {b}" for a, b in excluidos) or "- Ninguno"
    readme = f"""# Complexhibit: catálogos de exposiciones anotados

[Completar: autores, año, DOI, cómo citar]

Corpus de {len(filas)} catálogos de exposiciones anotados manualmente con GATE según el
Manual de etiquetado v1, en tres niveles: bloques del catálogo (fichas de obra y
exposiciones), entidades (personas, títulos, instituciones, lugares, fechas, técnicas,
dimensiones…) y detalle (dimensiones desglosadas, fechas normalizadas, roles y tipos).

Proyecto Complexhibit (PID2021-125037NB-I00), financiado por [completar].

## Contenido

- `inventario_catalogos.csv`: un catálogo por fila; relaciona el identificador con el
  nombre original del fichero y con su referencia bibliográfica.
- `anotaciones/<id>.json`: anotaciones en formato standoff (posición inicial y final en
  caracteres, etiqueta y rasgos). Para las entidades se incluye el texto anotado; para los
  bloques, solo la posición.
- `particion.json`: catálogos de validación y prueba (el resto, entrenamiento).
- `estadisticas.csv`: número de anotaciones por etiqueta y catálogo.

## Anotaciones por etiqueta

| Etiqueta | N.º |
| --- | --- |
{tabla}

## Texto íntegro y acceso restringido

Los textos íntegros de los catálogos están sujetos a derechos de autor de sus editores y no
se publican en abierto. Los ficheros GATE originales y la versión BIO se conservan en
[acceso restringido, a petición justificada para investigación / completar]. El campo
`sha256_texto` permite comprobar que una copia del texto coincide con la anotada.

## Correcciones aplicadas

Al normalizar los valores de algunos atributos en GATE (`city` → `poblation`, `material` →
`technique`), la sustitución afectó también a palabras del texto que contenían esas cadenas
(por ejemplo, «materiality» aparecía como «techniqueity»). La conversión restituye esas palabras
a su forma original; las posiciones de las anotaciones no cambian. El texto incluido en
`anotaciones/` está restituido y los ficheros GATE se conservan tal como se anotaron.

## Ficheros excluidos

{excl}

## Licencia

[CC BY 4.0, completar]
"""
    (ab / "README.md").write_text(readme, encoding="utf-8")
    print(f"{len(filas)} catálogos -> {salida}")
    print("Excluidos:", excluidos or "ninguno")
    return filas, excluidos


if __name__ == "__main__":
    main(*sys.argv[1:])
