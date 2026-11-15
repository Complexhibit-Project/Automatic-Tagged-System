# Versión 1 (2023-2024): BiLSTM + ELMo

Código de la primera fase del sistema, tal como se desarrolló entre 2023 y 2024: preparación de los datos a
partir de las anotaciones de GATE y entrenamiento de una red de dos capas BiLSTM con
representaciones ELMo (Keras / TensorFlow). Sus resultados preliminares se presentaron en el
congreso de Humanidades Digitales Hispánicas de 2023.

Se conserva como **registro histórico** del proyecto, sin modificaciones (incluye copias de trabajo
como `back1.py`…`back4.py` o `procesartextobak.py`).

## Organización de los ficheros

Los ficheros corresponden a las etapas de una cadena de procesamiento que se ejecutaba paso a paso
desde el entorno de desarrollo (Spyder), no a un programa único:

| Etapa | Ficheros | Función |
| --- | --- | --- |
| 1. Lectura de las anotaciones | `procesartexto.py`, `buscar.py`, `texto.py` | Leen los XML de GATE y recuperan, para cada anotación, su posición en el texto y sus rasgos |
| 2. Construcción del conjunto de entrenamiento | `contruirlistas.py`, `sentences.py`, `codigosentencias.py` | Dividen el texto en frases y asignan a cada palabra su etiqueta |
| 3. Preparación de datos y entrenamiento | `prepararDatos.py`, `preparacionDatos.py` | Codifican las frases y las etiquetas, y definen y entrenan la red BiLSTM con ELMo |
| Copias de trabajo | `back1.py`…`back4.py`, `procesartextobackup.py`, `procesartextobak.py` | Versiones intermedias de las etapas anteriores, conservadas como registro del desarrollo |

## Reproducción y evaluación (2026)

La arquitectura de esta versión **se ha vuelto a ejecutar y evaluar** en 2026 para compararla con el
sistema final en igualdad de condiciones. El código original no puede ejecutarse tal cual: el módulo
de ELMo de TensorFlow Hub requiere TensorFlow 1, que no funciona con las versiones vigentes de
Python. Por eso se ha reconstruido la misma red (dos capas BiLSTM de 512 unidades con conexión
residual y salida *softmax* por palabra) sustituyendo ELMo por las representaciones congeladas de un
codificador multilingüe actual (XLM-RoBERTa), que cumplen la misma función.

Cuaderno: [`../v2-2026-transformer/cuadernos/07_comparacion_bilstm.ipynb`](../v2-2026-transformer/cuadernos/07_comparacion_bilstm.ipynb)

Resultados sobre los mismos 10 catálogos de prueba que el sistema final (entidades del nivel 2):

| Medida | BiLSTM reconstruido | Sistema final (XLM-RoBERTa large) |
| --- | --- | --- |
| F1 por entidad completa | 0,62 | 0,73 |
| Exactitud por palabra | 0,965 | — |

La exactitud por palabra es muy alta porque la mayoría de las palabras de un catálogo no son
entidades; por eso la comparación se hace por entidad completa. El sistema final supera a esta
arquitectura en 11 puntos de F1.

Las rutas de los ficheros originales (`/Users/...`) corresponden al equipo en que se desarrollaron.
