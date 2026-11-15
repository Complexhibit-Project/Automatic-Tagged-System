"""Complexhibit: extracción de información de catálogos de exposiciones (línea de órdenes).

Dos modos:

  modelos  Procesa catálogos en texto plano (.txt) con los modelos entrenados
           (nivel 1: bloques; nivel 2: entidades; nivel 3: reglas + clasificador de atributos)
           y escribe, por cada catálogo, la salida anidada en JSON y, si se pide, en RDF (Turtle).

  gate     Convierte catálogos anotados a mano en GATE (.xml) a la misma salida JSON / RDF,
           sin modelos. Sirve para exportar el gold standard al grafo de conocimiento.

Ejemplos:
  python extraer.py modelos --entrada textos/ --salida resultados/ --modelos modelos/ --rdf
  python extraer.py gate    --entrada xml_gate/ --salida resultados/ --rdf
"""
import argparse
import json
import sys
from pathlib import Path

import complexhibit_ie as ie
import complexhibit_rdf as rdf

# Atributos que se piden al clasificador para cada tipo de entidad o bloque
PEDIR = {"PER": ["person.role"], "ORG": ["institution.type", "institution.role"],
         "TECH": ["technique.type"], "ITEM": ["work.type"]}


class Extractor:
    def __init__(self, carpeta_modelos, dispositivo=None):
        import torch
        from transformers import (AutoModelForSequenceClassification,
                                  AutoModelForTokenClassification, AutoTokenizer)
        self.torch = torch
        self.dev = dispositivo or ("cuda" if torch.cuda.is_available() else "cpu")
        # Los modelos pueden estar en una carpeta local (nivel1/, nivel2/, atributos/)
        # o publicados en Hugging Face: --modelos hf:USUARIO/complexhibit  ->  USUARIO/complexhibit-nivel1, ...
        if str(carpeta_modelos).startswith("hf:"):
            prefijo = str(carpeta_modelos)[3:]
            ruta = lambda n: f"{prefijo}-{n}"
            existe = lambda n: True
        else:
            base = Path(carpeta_modelos)
            ruta = lambda n: base / n
            existe = lambda n: (base / n / "config.json").exists()
            faltan = [n for n in ("nivel1", "nivel2") if not existe(n)]
            if faltan:
                sys.exit(f"Faltan modelos en {base}: {', '.join(faltan)} (cada uno es una carpeta con config.json)")

        def cargar(nombre, clase):
            m = clase.from_pretrained(ruta(nombre))
            if self.dev == "cpu":
                m = m.float()   # los modelos se publican en media precisión; en CPU se pasan a 32 bits
            return AutoTokenizer.from_pretrained(ruta(nombre)), m.to(self.dev).eval()

        self.t1, self.m1 = cargar("nivel1", AutoModelForTokenClassification)
        self.t2, self.m2 = cargar("nivel2", AutoModelForTokenClassification)
        self.m3 = None
        if existe("atributos"):
            self.t3, self.m3 = cargar("atributos", AutoModelForSequenceClassification)
            self.clases3 = [self.m3.config.id2label[i] for i in range(len(self.m3.config.id2label))]
        else:
            print("Aviso: no hay modelo de atributos; se omiten roles y tipos.", file=sys.stderr)

    def _bio(self, tok, modelo, texto, max_tokens=200, bloques=False):
        tokens = ie.tokenize(texto)
        tags = ["O"] * len(tokens)
        id2label = modelo.config.id2label
        trozos = (ie.segment_bounds_inferencia(tokens, texto, max_tokens) if bloques
                  else ie.segment_bounds(tokens, texto, None, max_tokens))
        for a, b in trozos:
            palabras = [ie.fix_token(t[0]) for t in tokens[a:b]]
            enc = tok(palabras, is_split_into_words=True, truncation=True, max_length=512,
                      return_tensors="pt").to(self.dev)
            with self.torch.no_grad():
                pred = modelo(**enc).logits.argmax(-1)[0].tolist()
            prev = None
            for j, w in enumerate(enc.word_ids(0)):
                if w is not None and w != prev:
                    tags[a + w] = id2label[pred[j]]
                prev = w
        return ie.bio_a_spans(tokens, tags)

    def _atributo(self, texto, s, e, atributo):
        entrada = f"{atributo}: " + ie.con_marcas(texto, s, e)
        enc = self.t3(entrada, truncation=True, max_length=256, return_tensors="pt").to(self.dev)
        with self.torch.no_grad():
            lg = self.m3(**enc).logits[0].tolist()
        validos = [i for i, c in enumerate(self.clases3) if c.startswith(atributo + "=")]
        if not validos:
            return None
        return self.clases3[max(validos, key=lambda i: lg[i])].split("=", 1)[1]

    def procesar(self, texto):
        sp1 = self._bio(self.t1, self.m1, texto, bloques=True)   # nivel 1: sin cortar las fichas (v1.1)
        sp2 = self._bio(self.t2, self.m2, texto)
        atributos = {}
        if self.m3 is not None:
            for s, e, lab in sp1 + sp2:
                for at in PEDIR.get(lab, []):
                    v = self._atributo(texto, s, e, at)
                    if v:
                        atributos.setdefault((s, e), {})[at] = v
        return ie.montar_salida(texto, sp1, sp2, atributos)


def ficheros(entrada, extension):
    p = Path(entrada)
    if p.is_file():
        return [p]
    return sorted(x for x in p.rglob(f"*{extension}") if not x.name.startswith("._"))


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("modo", choices=["modelos", "gate"])
    ap.add_argument("--entrada", required=True, help="fichero o carpeta (.txt en modo modelos, .xml en modo gate)")
    ap.add_argument("--salida", required=True, help="carpeta de resultados")
    ap.add_argument("--modelos", default="/modelos", help="carpeta con nivel1/, nivel2/ y atributos/, o hf:USUARIO/complexhibit para usar los modelos publicados en Hugging Face")
    ap.add_argument("--rdf", action="store_true", help="genera también RDF (Turtle) según OntoExhibit + CIDOC-CRM")
    a = ap.parse_args(argv)

    salida = Path(a.salida)
    (salida / "json").mkdir(parents=True, exist_ok=True)
    grafo = rdf.Grafo() if a.rdf else None
    lista = ficheros(a.entrada, ".txt" if a.modo == "modelos" else ".xml")
    if not lista:
        sys.exit(f"No hay ficheros que procesar en {a.entrada}")
    extractor = Extractor(a.modelos) if a.modo == "modelos" else None

    n = 0
    for f in lista:
        try:
            if extractor:
                res = extractor.procesar(f.read_text(encoding="utf-8", errors="ignore"))
            else:
                _, res = rdf.gold_a_salida(f)
        except Exception as err:  # noqa: BLE001
            print(f"AVISO {f.name}: {err}", file=sys.stderr)
            continue
        (salida / "json" / f"{f.stem}.json").write_text(json.dumps(res, indent=1, ensure_ascii=False), encoding="utf-8")
        if grafo is not None:
            rdf.salida_a_turtle(res, ("pred-" if extractor else "") + f.stem, grafo)
        n += 1
        print(f"{f.name}: {len(res['bloques'])} bloques, {len(res['entidades_fuera_de_bloques'])} entidades sueltas")
    if grafo is not None:
        (salida / "grafo.ttl").write_text(grafo.turtle(), encoding="utf-8")
        print(f"RDF: {salida / 'grafo.ttl'} ({len(set(grafo.lineas))} tripletas)")
    print(f"{n} de {len(lista)} catálogos procesados -> {salida}")


if __name__ == "__main__":
    main()
