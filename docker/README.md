# Extractor Complexhibit (contenedor Docker)

Extrae información de catálogos de exposiciones en tres niveles (bloques, entidades y detalle)
y la exporta como JSON anidado y como RDF según OntoExhibit + CIDOC-CRM.

## Construir la imagen

```bash
docker build -t complexhibit-extractor .
```

## Usar

Catálogos en texto plano, con los modelos entrenados (carpetas `nivel1/`, `nivel2/` y,
opcionalmente, `atributos/`, tal como las guarda el cuaderno de entrenamiento):

```bash
docker run --rm -v /ruta/modelos:/modelos -v /ruta/datos:/datos complexhibit-extractor \
  modelos --entrada /datos/textos --salida /datos/resultados --rdf
```

Con los modelos publicados en Hugging Face (no hace falta descargarlos a mano). Son los tres
modelos del sistema final, basados en XLM-RoBERTa large: `Complexhibit-Project/complexhibit-nivel1`,
`-nivel2` y `-atributos`:

```bash
docker run --rm -v /ruta/datos:/datos complexhibit-extractor \
  modelos --modelos hf:Complexhibit-Project/complexhibit --entrada /datos/textos --salida /datos/resultados --rdf
```

Catálogos anotados en GATE, sin modelos (exportación del gold standard al grafo):

```bash
docker run --rm -v /ruta/datos:/datos complexhibit-extractor \
  gate --entrada /datos/xml_gate --salida /datos/resultados --rdf
```

Resultados: `resultados/json/<catálogo>.json` (salida anidada) y `resultados/grafo.ttl` (RDF),
que puede cargarse en el almacén de tripletas de la plataforma Complexhibit (Virtuoso).

Sin Docker: `pip install torch transformers sentencepiece` y `python extraer.py ...` con los mismos argumentos.
