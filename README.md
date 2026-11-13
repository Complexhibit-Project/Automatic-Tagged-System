# Automatic-Tagged-System

Sistema de extracción automática de información de catálogos de exposiciones del proyecto
**Complexhibit** (PID2021-125037NB-I00). A partir del texto de un catálogo, identifica las fichas
de obra y las exposiciones, las entidades (personas, títulos, instituciones, lugares, fechas,
técnicas, dimensiones…) y su detalle (dimensiones desglosadas, fechas normalizadas, roles y tipos),
y exporta el resultado como grafo RDF según la ontología [OntoExhibit](https://github.com/Complexhibit-Project/OntoExhibit),
ampliada con CIDOC-CRM.

Web del proyecto: https://complexhibit.eu · Plataforma: https://complexhibit.uma.es

## Contenido

| Carpeta | Qué contiene |
| --- | --- |
| [`v1-2023-bilstm-elmo/`](v1-2023-bilstm-elmo/) | Primera versión (2023): red BiLSTM con representaciones ELMo. Se conserva como registro histórico; ya no es ejecutable en los entornos actuales. |
| [`v2-2026-transformer/`](v2-2026-transformer/) | Sistema final: modelo *transformer* multilingüe (XLM-RoBERTa) en tres niveles, reglas de normalización, exportación a RDF y cuadernos de entrenamiento y evaluación. |
| [`datos/`](datos/) | Gold standard abierto: anotaciones externas al texto de los 100 catálogos, inventario, partición, estadísticas y grafo RDF. |
| [`docs/`](docs/) | Manual de etiquetado (v1.1), con la correspondencia entre el esquema de anotación y las etiquetas de los modelos. |
| [`docker/`](docker/) | Contenedor Docker del sistema final para ejecutarlo en cualquier entorno. |

## Modelos entrenados

Los tres modelos del sistema final (XLM-RoBERTa large) no se guardan en este repositorio por su
tamaño (más de 1 GB cada uno). Están publicados en Hugging Face, con licencia MIT:

- [`Complexhibit-Project/complexhibit-nivel1`](https://huggingface.co/Complexhibit-Project/complexhibit-nivel1): fichas de obra y exposiciones
- [`Complexhibit-Project/complexhibit-nivel2`](https://huggingface.co/Complexhibit-Project/complexhibit-nivel2): entidades
- [`Complexhibit-Project/complexhibit-atributos`](https://huggingface.co/Complexhibit-Project/complexhibit-atributos): roles y tipos

El contenedor Docker los descarga de allí (`--modelos hf:Complexhibit-Project/complexhibit`).

## Datos

El gold standard de 100 catálogos (anotaciones externas al texto, inventario, partición,
estadísticas y grafo RDF) está en la carpeta [`datos/`](datos/) y, con el manual de etiquetado, en
Zenodo: https://doi.org/10.5281/zenodo.24199594. Los textos íntegros de los
catálogos no se distribuyen por derechos de autor.

## Desarrollo y autoría

La herramienta se fundamenta en una metodología de anotación textual concebida específicamente en el marco del proyecto, que comprende una guía de anotación y un esquema de categorías propio. El corpus de entrenamiento fue anotado manualmente por el equipo investigador, lo que hace posible el etiquetado automático de nuevos textos conforme a los criterios definidos. La implementación del código se llevó a cabo con asistencia de inteligencia artificial generativa (Claude, de Anthropic), a partir de las especificaciones y directrices establecidas por el equipo investigador, que asumió el diseño metodológico, la supervisión del desarrollo y la validación de los resultados.

- **Diseño del sistema y de su evaluación, y dirección del desarrollo:** M.ª Luisa Díez Platas (Universidad Internacional de La Rioja, UNIR).
- **Guía de anotación y esquema de categorías:** María Ortiz Tello y M.ª Luisa Díez Platas ([manual de etiquetado](docs/)).
- **Validación:** el funcionamiento de la herramienta se ha comprobado con las métricas descritas en la carpeta `v2-2026-transformer/`, calculadas sobre catálogos que no se usaron en el entrenamiento.

## Licencia

Código: MIT. Datos y documentación: CC BY 4.0.

## Cómo citar

Díez Platas, M. L. y Ortiz Tello, M. (2026). *Automatic-Tagged-System: extracción de información de catálogos de exposiciones*. Proyecto Complexhibit. https://github.com/Complexhibit-Project/Automatic-Tagged-System
