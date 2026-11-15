# Versión 2 (2026): sistema final en tres niveles

| Nivel | Qué extrae | Método |
| --- | --- | --- |
| 1. Bloques | Fichas de obra (`catalogueItem`) y exposiciones (`exhibition`) | Modelo *transformer* (BIO) |
| 2. Entidades | Persona, título, institución/sede, lugar, fecha, técnica/material, dimensiones, dirección, n.º de inventario | Modelo *transformer* (BIO) |
| 3. Detalle | Alto, ancho, fondo, peso, diámetro y unidad; fechas ISO | Reglas |
| 3. Detalle | Rol de persona, tipo y rol de institución, tipo de obra, tipo de técnica | Clasificador *transformer* con contexto |

Sistema final: XLM-RoBERTa large (`FacebookAI/xlm-roberta-large`) para los tres componentes
entrenados; los modelos se publican en Hugging Face (`Complexhibit-Project/complexhibit-nivel1`,
`-nivel2` y `-atributos`, licencia MIT). Partición por catálogo completo
(80/10/10, semilla 42). Evaluación por entidad completa con seqeval.

## Ficheros

- `complexhibit_ie.py`: lectura de GATE, conversión a BIO, reglas del nivel 3 y montaje de la salida anidada.
- `complexhibit_rdf.py`: exportación a RDF (Turtle) según OntoExhibit + CIDOC-CRM.
- `preparar_deposito.py`: prepara el depósito de datos (anotaciones standoff, inventario, partición).

## Cuadernos (Google Colab)

| Cuaderno | Uso | GPU |
| --- | --- | --- |
| `01_entrenamiento_etiquetador.ipynb` | Entrena los tres componentes con XLM-RoBERTa large y los guarda en Hugging Face | Sí (L4 o A100) |
| `02_aplicar_etiquetador.ipynb` | Aplica el etiquetador a catálogos nuevos (texto o PDF) y genera JSON, RDF y una muestra para revisión | Sí |
| `03_nivel3_reglas.ipynb` | Evaluación de las reglas de dimensiones y fechas | No |
| `04_exportacion_rdf.ipynb` | Exportación del gold standard a RDF | No |
| `05_preparar_deposito.ipynb` | Preparación del depósito de datos | No |
| `06_comparacion_modelo_base.ipynb` | Modelo base (XLM-RoBERTa base) y comparación con el sistema final | Sí |
| `07_comparacion_bilstm.ipynb` | Reconstrucción de la arquitectura BiLSTM de 2023 para compararla con el sistema final | Sí |
| `08_nivel1_v11_reentrenamiento.ipynb` | Nivel 1, versión 1.1: reentrenamiento con el texto dividido sin usar la anotación y evaluación en condiciones de uso real (sustituye al nivel 1 del cuaderno 01) | Sí (L4 o A100) |
| `09_predicciones_gold_standard.ipynb` | Aplica los modelos publicados a los 100 catálogos y guarda sus predicciones para compararlas con la anotación manual | Sí |

Todos salvo el 02 piden al empezar un ZIP con los ficheros XML de GATE.

## Resultados (10 catálogos de prueba)

| Componente | Resultado (sistema final, XLM-RoBERTa large) |
| --- | --- |
| Nivel 1, fichas de obra y exposiciones (v1.1) | Fichas de obra: F1 0,61 por bloque exacto y 0,71 por solapamiento, sobre el texto completo de cada catálogo |
| Nivel 2, entidades | F1 0,73 por entidad (precisión 0,70; exhaustividad 0,75) |
| Nivel 3, reglas | 91,5 % de las dimensiones y 77,5 % de las fechas |
| Nivel 3, clasificador | Exactitud de 0,49 a 0,94 según el atributo (rol de persona 0,94) |
| Exportación RDF (100 catálogos) | 108.996 tripletas; 2.754 obras, 1.757 personas, 376 exposiciones |

Como referencia, con el mismo protocolo el modelo base obtiene 0,69 en el nivel 2, y la arquitectura BiLSTM de 2023 reconstruida, 0,62 en el nivel 2.

## Desarrollo y autoría

La herramienta se fundamenta en una metodología de anotación textual concebida específicamente en el marco del proyecto, que comprende una guía de anotación y un esquema de categorías propio. El corpus de entrenamiento fue anotado manualmente por el equipo investigador, lo que hace posible el etiquetado automático de nuevos textos conforme a los criterios definidos. La implementación del código se llevó a cabo con asistencia de inteligencia artificial generativa (Claude, de Anthropic), a partir de las especificaciones y directrices establecidas por el equipo investigador, que asumió el diseño metodológico, la supervisión del desarrollo y la validación de los resultados.

- **Diseño del sistema y de su evaluación, y dirección del desarrollo:** M.ª Luisa Díez Platas (Universidad Internacional de La Rioja, UNIR).
- **Guía de anotación y esquema de categorías:** María Ortiz Tello y M.ª Luisa Díez Platas ([manual de etiquetado](../docs/)).
- **Validación:** el funcionamiento de la herramienta se ha comprobado con las métricas descritas en este documento, calculadas sobre catálogos que no se usaron en el entrenamiento.
