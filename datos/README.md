# Gold standard de catálogos de exposiciones anotados (Complexhibit)

Corpus de **100 catálogos de exposiciones** anotados manualmente con GATE según el
[manual de etiquetado](../docs/manual_etiquetado_v1.1.pdf) (depositado en Zenodo: https://doi.org/10.5281/zenodo.24242023), en tres niveles: bloques del catálogo
(fichas de obra y exposiciones), entidades (personas, títulos, instituciones, lugares, fechas,
técnicas, dimensiones…) y detalle (dimensiones desglosadas, fechas normalizadas, roles y tipos).
Es el conjunto con el que se han entrenado y evaluado los modelos de este repositorio.

Depósito en Zenodo: https://doi.org/10.5281/zenodo.24199594

## Contenido

| Fichero | Contenido |
| --- | --- |
| `inventario_catalogos.csv` | Un catálogo por fila: identificador, nombre original del fichero, partición, idioma, número de anotaciones y de obras |
| `anotaciones/<id>.json` | Anotaciones externas al texto (formato *standoff*): posición inicial y final en caracteres, etiqueta y rasgos. Para las entidades se incluye el texto anotado (fragmentos breves); para los bloques, solo la posición |
| `particion.json` | Catálogos de validación (10) y de prueba (10); el resto (80) son de entrenamiento |
| `estadisticas.csv` | Número de anotaciones por etiqueta y catálogo |
| `rdf/gold_standard_ontoexhibit.ttl` | El gold standard como grafo de conocimiento (RDF/Turtle) según OntoExhibit y CIDOC-CRM: 108.996 tripletas |
| `rdf/resumen_rdf.csv` | Número de instancias por clase en el grafo |

## Anotaciones por etiqueta

| Etiqueta | N.º |
| --- | --- |
| persName | 4925 |
| person | 4697 |
| title | 3304 |
| work | 2798 |
| catalogueItem | 2754 |
| date | 2521 |
| img | 2472 |
| dimensions | 2384 |
| height | 2268 |
| width | 2250 |
| technique | 1922 |
| institution | 991 |
| placeName | 847 |
| exhibition | 376 |
| itemDesc | 353 |
| material | 338 |
| depth | 304 |
| person  | 276 |
| birth | 234 |
| text | 152 |
| catalogueSection | 136 |
| workCollection | 118 |
| catalogue | 101 |
| idno | 82 |
| address | 70 |
| venue | 66 |
| price | 65 |
| workPlace | 64 |
| caption | 60 |
| nationality | 49 |
| diameter | 46 |
| paragraph | 39 |
| origPlace | 30 |
| death | 28 |
| reference | 28 |
| translatedTitle | 22 |
| weight | 21 |
| duration | 10 |
| worklist | 4 |
| checklist | 4 |
| minute | 3 |
| second | 3 |
| index | 1 |

## Texto íntegro

Los textos íntegros de los catálogos están sujetos a derechos de autor de sus editores y no se
publican. Los ficheros GATE originales se conservan en almacenamiento institucional, con acceso
restringido al equipo investigador. El campo `sha256_texto` de cada fichero de anotaciones permite
comprobar que una copia del texto coincide exactamente con la anotada.

## Correcciones aplicadas

Al normalizar los valores de algunos atributos en GATE (`city` → `poblation`, `material` →
`technique`), la sustitución afectó también a palabras del texto que contenían esas cadenas
(por ejemplo, «materiality» aparecía como «techniqueity»). La conversión restituye esas palabras
a su forma original; las posiciones de las anotaciones no cambian. El texto incluido en
`anotaciones/` está restituido y los ficheros GATE se conservan tal como se anotaron.

## Cómo citar

Díez Platas, M. L. y Ortiz Tello, M. (2026). *Gold standard de catálogos de exposiciones de arte anotados (Complexhibit)* [Conjunto de datos]. Zenodo. https://doi.org/10.5281/zenodo.24199594

## Licencia

CC BY 4.0.

## Financiación

Proyecto PID2021-125037NB-I00, «Estudio e interpretación del dominio de las exposiciones artísticas como sistema cultural complejo mediante analítica de datos y procesamiento del lenguaje natural» (Complexhibit), financiado por MCIN/AEI/10.13039/501100011033.
