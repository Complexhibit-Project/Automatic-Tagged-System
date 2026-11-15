"""Exportación a RDF (Turtle) según OntoExhibit, completada con CIDOC-CRM.

Convierte en RDF:
  * la salida anidada de los tres niveles (JSON de complexhibit_ie.montar_salida);
  * el gold standard anotado en GATE (mismo formato, construido desde las anotaciones).

Correspondencias principales
  exhibition            -> ox:Exhibition  (hasTitle, hasTimeSpan, hasVenue, takesPlaceAt,
                                           hasOrganizer, hasLender, hasCuratorInvolved,
                                           hasExhibitingActant, displays)
  catalogueItem / work  -> ox:Artwork     (hasTitle, hasCreation -> E65_Creation)
  persName + role       -> ox:E21_Person  + ox:hasRole -> rol (ox:Creator, ox:Lender...)
  institution + type    -> ox:Institution / ox:Gallery / ox:Company ... + rol
  placeName             -> ox:Territorial_Entity
  address               -> ox:Physical_Site con ox:address
  date                  -> ox:Exact_Date / ox:Time_Range (hasStartingDate, hasEndingDate)
  técnica               -> crm:P32_used_general_technique -> crm:E55_Type
  material              -> crm:P45_consists_of -> crm:E57_Material
  dimensiones           -> crm:P43_has_dimension -> crm:E54_Dimension (P2, P90, P91)
  tipo de obra          -> crm:P2_has_type -> crm:E55_Type
  nº de inventario      -> crm:P1_is_identified_by -> crm:E42_Identifier
  catálogo              -> ox:Catalog, que crm:P67_refers_to cada entidad mencionada
"""
import collections
import re
import unicodedata
from pathlib import Path

import complexhibit_ie as ie

OX = "https://w3id.org/OntoExhibit#"
CRM = "http://www.cidoc-crm.org/cidoc-crm/"
BASE_DATOS = "https://w3id.org/OntoExhibit/datos/"   # cambiar si se publica en otro espacio

PREFIJOS = f"""@prefix ox: <{OX}> .
@prefix crm: <{CRM}> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .
@prefix d: <{BASE_DATOS}> .

"""

# valores de role de <person> del manual de etiquetado -> clases de rol de OntoExhibit
ROL_PERSONA = {
    "creator": "Creator", "lender": "Lender", "owner": "Owner", "funder": "Funder",
    "exhibitioncurator": "Curator", "museumcurator": "Curator", "curator": "Curator",
    "assistant": "Assistant", "editor": "Editor", "designer": "Designer",
    "photographer": "Creator", "trustee": "Member", "author": "Author",
}
# valores de role de <institution> del manual de etiquetado -> clases de rol de OntoExhibit
# ('host', la institución que acoge la exposición, se representa como sede: ox:hasVenue)
ROL_INSTITUCION = {
    "organiser": "Organizer", "organizer": "Organizer", "lender": "Lender", "owner": "Owner",
    "funder": "Funder", "client": "Commissioner", "depository": "Owner",
}
# valores de type de <institution> del manual de etiquetado -> clases de OntoExhibit
TIPO_INSTITUCION = {
    "gallery": "Gallery", "artgallery": "Gallery", "company": "Company",
}


# ----------------------------------------------------------------------------
def slug(texto, maximo=60):
    t = unicodedata.normalize("NFKD", texto.lower()).encode("ascii", "ignore").decode()
    t = re.sub(r"[^a-z0-9]+", "-", t).strip("-")
    return t[:maximo] or "x"


def lit(texto, tipo=None):
    t = str(texto).replace("\\", "\\\\").replace('"', '\\"').replace("\n", " ").replace("\r", " ")
    t = re.sub(r"\s+", " ", t).strip()
    return f'"{t}"^^xsd:{tipo}' if tipo else f'"{t}"'


def valores_lista(v):
    return [x.strip().lstrip("_").lower() for x in re.split(r"[,+]", v or "") if x.strip()]


class Grafo:
    def __init__(self):
        self.lineas = []
        self.n = 0
        self.doc = "doc"

    def t(self, s, p, o):
        self.lineas.append(f"{s} {p} {o} .")

    def nuevo(self, prefijo):
        self.n += 1
        return f"d:{prefijo}-{self.doc}-{self.n}"

    def turtle(self):
        return PREFIJOS + "\n".join(dict.fromkeys(self.lineas)) + "\n"


# ----------------------------------------------------------------------------
def _fecha(g, valores, texto):
    """Devuelve el nodo de tiempo (Exact_Date o Time_Range) o None."""
    if not valores:
        return None
    if "when" in valores:
        n = g.nuevo("fecha")
        tipo = "gYear" if len(valores["when"]) == 4 else "date"
        g.t(n, "a", "ox:Exact_Date")
        g.t(n, "rdfs:label", lit(valores["when"], tipo))
        g.t(n, "crm:P3_has_note", lit(texto))
        return n
    if "from" in valores or "to" in valores:
        r = g.nuevo("intervalo")
        g.t(r, "a", "ox:Time_Range")
        g.t(r, "crm:P3_has_note", lit(texto))
        for clave, prop in (("from", "ox:hasStartingDate"), ("to", "ox:hasEndingDate")):
            if clave in valores:
                n = g.nuevo("fecha")
                g.t(n, "a", "ox:Exact_Date")
                g.t(n, "rdfs:label", lit(valores[clave], "date" if len(valores[clave]) == 10 else "gYear"))
                g.t(r, prop, n)
        return r
    return None


def _persona(g, ent):
    p = f"d:persona-{slug(ent['texto'])}"
    g.t(p, "a", "ox:E21_Person")
    g.t(p, "ox:person_name", lit(ent["texto"]))
    g.t(p, "rdfs:label", lit(ent["texto"]))
    return p


def _institucion(g, ent):
    i = f"d:institucion-{slug(ent['texto'])}"
    tipos = valores_lista(ent.get("atributos", {}).get("institution.type"))
    clase = next((TIPO_INSTITUCION[t] for t in tipos if t in TIPO_INSTITUCION), "Institution")
    g.t(i, "a", f"ox:{clase}")
    g.t(i, "ox:name", lit(ent["texto"]))
    g.t(i, "rdfs:label", lit(ent["texto"]))
    for t in tipos:
        if t not in TIPO_INSTITUCION:
            g.t(i, "crm:P2_has_type", f"d:tipo-institucion-{slug(t)}")
            g.t(f"d:tipo-institucion-{slug(t)}", "a", "crm:E55_Type")
            g.t(f"d:tipo-institucion-{slug(t)}", "rdfs:label", lit(t))
    return i


def _rol(g, actante, clase):
    r = g.nuevo("rol")
    g.t(r, "a", f"ox:{clase}")
    g.t(actante, "ox:hasRole", r)
    g.t(r, "ox:isRoleOf", actante)
    return r


def _lugar(g, ent):
    l = f"d:lugar-{slug(ent['texto'])}"
    g.t(l, "a", "ox:Territorial_Entity")
    g.t(l, "rdfs:label", lit(ent["texto"]))
    return l


def _tipo(g, espacio, valor):
    u = f"d:{espacio}-{slug(valor)}"
    g.t(u, "a", "crm:E55_Type")
    g.t(u, "rdfs:label", lit(valor))
    return u


def _dimensiones(g, obra, valores, texto):
    unidad = valores.get("unit")
    for clave in ("height", "width", "depth", "weight", "diameter"):
        if clave not in valores or valores[clave] is None:
            continue
        dmn = g.nuevo("dimension")
        g.t(obra, "crm:P43_has_dimension", dmn)
        g.t(dmn, "a", "crm:E54_Dimension")
        g.t(dmn, "crm:P2_has_type", _tipo(g, "tipo-dimension", clave))
        v = valores[clave]
        if isinstance(v, (tuple, list)):
            g.t(dmn, "crm:P90a_has_lower_value_limit", lit(v[0], "decimal"))
            g.t(dmn, "crm:P90b_has_upper_value_limit", lit(v[1], "decimal"))
        else:
            g.t(dmn, "crm:P90_has_value", lit(v, "decimal"))
        if unidad:
            u = f"d:unidad-{slug(unidad)}"
            g.t(u, "a", "crm:E58_Measurement_Unit")
            g.t(u, "rdfs:label", lit(unidad))
            g.t(dmn, "crm:P91_has_unit", u)
        g.t(dmn, "crm:P3_has_note", lit(texto))


def _titulo(g, entidad_uri, texto):
    t = g.nuevo("titulo")
    g.t(t, "a", "ox:Title")
    g.t(t, "rdfs:label", lit(texto))
    g.t(entidad_uri, "ox:hasTitle", t)
    g.t(t, "ox:isTitleOf", entidad_uri)


# ----------------------------------------------------------------------------
def _exposicion(g, b, cat):
    e = g.nuevo("exposicion")
    g.t(e, "a", "ox:Exhibition")
    g.t(cat, "crm:P67_refers_to", e)
    titulo_hecho = fecha_hecha = False
    for ent in b["contenido"]:
        lab, at = ent["tipo"], ent.get("atributos", {})
        if lab == "TITLE" and not titulo_hecho:
            _titulo(g, e, ent["texto"]); g.t(e, "rdfs:label", lit(ent["texto"])); titulo_hecho = True
        elif lab == "DATE" and not fecha_hecha:
            n = _fecha(g, ent.get("valores"), ent["texto"])
            if n:
                g.t(e, "ox:hasTimeSpan", n); fecha_hecha = True
        elif lab == "LOC":
            g.t(e, "ox:takesPlaceAt", _lugar(g, ent))
        elif lab == "ADDR":
            s = g.nuevo("sitio"); g.t(s, "a", "ox:Physical_Site"); g.t(s, "ox:address", lit(ent["texto"]))
            g.t(e, "ox:hasVenue", s)
        elif lab == "ORG":
            _vincular_institucion(g, e, _institucion(g, ent), ent)
        elif lab == "PER":
            _vincular_persona(g, e, _persona(g, ent), ent)
    return e


def _vincular_institucion(g, expo, inst, ent):
    roles = valores_lista(ent.get("atributos", {}).get("institution.role"))
    if expo is None:
        return
    for r in roles:
        if r == "host":
            g.t(expo, "ox:hasVenue", inst)
        elif r in ROL_INSTITUCION:
            rol = _rol(g, inst, ROL_INSTITUCION[r])
            prop = {"Organizer": "ox:hasOrganizer", "Lender": "ox:hasLender"}.get(ROL_INSTITUCION[r])
            if prop:
                g.t(expo, prop, rol)


def _vincular_persona(g, expo, per, ent):
    rol_txt = ent.get("atributos", {}).get("person.role", "").strip().lower()
    clase = ROL_PERSONA.get(rol_txt.replace("_", ""))
    if not clase:
        return None
    rol = _rol(g, per, clase)
    if expo is not None:
        if clase == "Curator":
            g.t(expo, "ox:hasCuratorInvolved", rol)
        elif clase == "Lender":
            g.t(expo, "ox:hasLender", rol)
        elif clase == "Creator":
            g.t(expo, "ox:hasExhibitingActant", per)
    return rol


def _obra(g, b, cat, expo, creadores_doc):
    o = g.nuevo("obra")
    g.t(o, "a", "ox:Artwork")
    g.t(cat, "crm:P67_refers_to", o)
    if expo is not None:
        g.t(expo, "ox:displays", o)
        g.t(o, "ox:isDisplayedAt", expo)
    tipo_obra = b.get("atributos", {}).get("work.type")
    if tipo_obra:
        g.t(o, "crm:P2_has_type", _tipo(g, "tipo-obra", tipo_obra))
    creacion = None
    titulo_hecho = False
    hay_creador = False
    for ent in b["contenido"]:
        lab = ent["tipo"]
        if lab == "TITLE" and not titulo_hecho:
            _titulo(g, o, ent["texto"]); g.t(o, "rdfs:label", lit(ent["texto"])); titulo_hecho = True
        elif lab == "DATE":
            n = _fecha(g, ent.get("valores"), ent["texto"])
            if n:
                creacion = creacion or _creacion(g, o)
                g.t(creacion, "ox:hasTimeSpan", n)
        elif lab == "TECH":
            tt = ent.get("atributos", {}).get("technique.type")
            for v in (valores_lista(tt) if tt else [ent["texto"]]):
                g.t(o, "crm:P32_used_general_technique", _tipo(g, "tecnica", v))
            g.t(o, "crm:P3_has_note", lit("Técnica: " + ent["texto"]))
        elif lab == "MAT":
            m = f"d:material-{slug(ent['texto'])}"
            g.t(m, "a", "crm:E57_Material"); g.t(m, "rdfs:label", lit(ent["texto"]))
            g.t(o, "crm:P45_consists_of", m)
        elif lab == "DIM":
            _dimensiones(g, o, ent.get("valores") or {}, ent["texto"])
        elif lab == "IDNO":
            i = g.nuevo("identificador"); g.t(i, "a", "crm:E42_Identifier"); g.t(i, "rdfs:label", lit(ent["texto"]))
            g.t(o, "crm:P1_is_identified_by", i)
        elif lab == "PER":
            per = _persona(g, ent)
            rol = _vincular_persona(g, None, per, ent)
            if rol and ent.get("atributos", {}).get("person.role", "").lower() == "creator":
                creacion = creacion or _creacion(g, o)
                g.t(creacion, "ox:hasCreator", rol); hay_creador = True
            elif rol and ent.get("atributos", {}).get("person.role", "").lower() == "owner":
                g.t(o, "ox:hasOwner", rol)
        elif lab == "ORG":
            inst = _institucion(g, ent)
            if "owner" in valores_lista(ent.get("atributos", {}).get("institution.role")):
                g.t(o, "ox:hasOwner", _rol(g, inst, "Owner"))
        elif lab == "LOC":
            creacion = creacion or _creacion(g, o)
            g.t(creacion, "ox:hasPlaceOfCreation", _lugar(g, ent))
    # en catálogos monográficos el autor suele aparecer solo fuera de la ficha
    if not hay_creador and len(creadores_doc) == 1:
        creacion = creacion or _creacion(g, o)
        g.t(creacion, "ox:hasCreator", creadores_doc[0])
    return o


def _creacion(g, obra):
    c = g.nuevo("creacion")
    g.t(c, "a", "ox:E65_Creation")
    g.t(obra, "ox:hasCreation", c)
    g.t(c, "ox:isCreationOf", obra)
    return c


def salida_a_turtle(salida, doc_id, g=None):
    """salida = dict de complexhibit_ie.montar_salida. Devuelve el objeto Grafo."""
    g = g or Grafo()
    g.doc = slug(doc_id, 40)
    cat = f"d:catalogo-{slug(doc_id)}"
    g.t(cat, "a", "ox:Catalog")
    g.t(cat, "rdfs:label", lit(doc_id))
    expos = [b for b in salida["bloques"] if b["tipo"] == "exhibition"]
    obras = [b for b in salida["bloques"] if b["tipo"] == "catalogueItem"]
    expo_uris = [_exposicion(g, b, cat) for b in expos]
    principal = expo_uris[0] if expo_uris else None
    # entidades fuera de bloques: se vinculan a la exposición principal del catálogo
    for ent in salida["entidades_fuera_de_bloques"]:
        lab = ent["tipo"]
        if lab == "PER":
            per = _persona(g, ent); g.t(cat, "crm:P67_refers_to", per)
            _vincular_persona(g, principal, per, ent)
        elif lab == "ORG":
            inst = _institucion(g, ent); g.t(cat, "crm:P67_refers_to", inst)
            _vincular_institucion(g, principal, inst, ent)
        elif lab == "LOC":
            g.t(cat, "crm:P67_refers_to", _lugar(g, ent))
    # autor principal del catálogo: el creador que concentra la mayoría de las menciones
    # (fuera de las fichas); se asigna a las obras cuya ficha no indica autor
    creadores = collections.Counter(
        slug(ent["texto"])
        for ent in salida["entidades_fuera_de_bloques"] + [x for b in expos for x in b["contenido"]]
        if ent["tipo"] == "PER" and ent.get("atributos", {}).get("person.role", "").lower() == "creator")
    creadores_rol = []
    if creadores:
        nombre, n = creadores.most_common(1)[0]
        if n / sum(creadores.values()) >= 0.5:
            creadores_rol = [_rol(g, f"d:persona-{nombre}", "Creator")]
    for b in obras:
        _obra(g, b, cat, principal, creadores_rol)
    return g


# ----------------------------------------------------------------------------
# Gold standard -> misma estructura que la salida del sistema
# ----------------------------------------------------------------------------
NIVEL2_GOLD = dict(ie.NIVEL2)
NIVEL2_GOLD["material"] = "MAT"   # en el gold se distingue material de técnica


def gold_a_salida(path):
    text, anns = ie.load_gate(path)
    # En el gold standard se conservan todas las anotaciones, también las que se
    # superponen (p. ej., título y material sobre el mismo texto). Para entrenar, la
    # conversión a BIO deja una sola etiqueta por palabra; aquí no es necesario.
    sp1 = sorted({(s, e, ie.NIVEL1[t]) for t, s, e, _ in anns if t in ie.NIVEL1})
    sp2 = sorted({(s, e, NIVEL2_GOLD[t]) for t, s, e, _ in anns if t in NIVEL2_GOLD})
    atributos = {}

    def buscar(tipo, s, e, rasgo, contenido=False):
        for t, a, b, f in anns:
            if t != tipo or not f.get(rasgo):
                continue
            if (a <= s and e <= b) if not contenido else (s <= a and b <= e):
                return f[rasgo].strip().lstrip("_")
        return None

    for s, e, lab in sp2:
        d = {}
        if lab == "PER":
            v = buscar("person", s, e, "role"); d.update({"person.role": v} if v else {})
        if lab == "ORG":
            for r in ("type", "role"):
                v = buscar("institution", s, e, r); d.update({f"institution.{r}": v} if v else {})
        if lab == "TECH":
            v = buscar("technique", s, e, "type"); d.update({"technique.type": v} if v else {})
        if d:
            atributos[(s, e)] = d
    for s, e, lab in sp1:
        if lab == "ITEM":
            v = buscar("work", s, e, "type", contenido=True)
            if v:
                atributos[(s, e)] = {"work.type": v}
    return text, ie.montar_salida(text, sp1, sp2, atributos)


def exportar_gold(carpeta, salida_ttl, por_documento=None):
    g = Grafo()
    n = 0
    for p in sorted(Path(carpeta).rglob("*.xml")):
        try:
            _, sal = gold_a_salida(p)
        except Exception as err:  # noqa: BLE001
            print(f"AVISO {p.name}: {err}")
            continue
        salida_a_turtle(sal, p.stem, g)
        if por_documento:
            Path(por_documento).mkdir(parents=True, exist_ok=True)
            Path(por_documento, p.stem + ".ttl").write_text(salida_a_turtle(sal, p.stem).turtle(), encoding="utf-8")
        n += 1
    Path(salida_ttl).write_text(g.turtle(), encoding="utf-8")
    print(f"{n} catálogos -> {salida_ttl} ({len(set(g.lineas))} tripletas)")
    return g
