"""Exportación con celdas nativas de diagrams.net y conectores anclados."""
from copy import deepcopy
from pathlib import Path
import xml.etree.ElementTree as ET


def exportar_drawio(destino, paginas, modelo, abstractos, ancho, alto):
    destino = Path(destino)
    individuales = destino / "drawio"
    individuales.mkdir(exist_ok=True)
    combinado = ET.Element("mxfile", host="app.diagrams.net", type="device", compressed="false")

    for numero, pagina in enumerate(paginas, 1):
        diagram = ET.Element("diagram", id=f"lamina-{numero}", name=pagina.title)
        graph = ET.SubElement(diagram, "mxGraphModel", dx="1191", dy="842", grid="0",
            gridSize="10", guides="1", tooltips="1", connect="1", arrows="1", fold="1",
            page="1", pageScale="1", pageWidth=str(round(ancho)), pageHeight=str(round(alto)), math="0", shadow="0")
        root = ET.SubElement(graph, "root")
        ET.SubElement(root, "mxCell", id="0")
        ET.SubElement(root, "mxCell", id="1", parent="0")

        def vertex(id, value, x, y, w, h, style, parent="1", connectable=True):
            attrs = dict(id=id, value=value, style=style, vertex="1", parent=parent)
            if not connectable:
                attrs["connectable"] = "0"
            cell = ET.SubElement(root, "mxCell", attrs)
            ET.SubElement(cell, "mxGeometry", x=f"{x:g}", y=f"{y:g}", width=f"{w:g}",
                          height=f"{h:g}", attrib={"as": "geometry"})
            return cell

        def text(id, value, x, y, w, h=16, size=9.4, bold=False, italic=False,
                 align="left", parent="1", background=False):
            font_style = (1 if bold else 0) + (2 if italic else 0)
            style = (f"text;html=0;whiteSpace=wrap;align={align};verticalAlign=middle;"
                     f"fontFamily=Arial;fontSize={size};fontStyle={font_style};"
                     "strokeColor=none;fillColor=none;fontColor=#222222;spacing=0;"
                     "autosize=0;resizable=1;rotatable=0;")
            if background:
                style += "fillColor=#ffffff;"
            return vertex(id, value, x, y, w, h, style, parent, connectable=False)

        def rule(id, x1, y1, x2, y2, parent="1"):
            cell = ET.SubElement(root, "mxCell", id=id, edge="1", parent=parent,
                style="edgeStyle=none;endArrow=none;startArrow=none;strokeColor=#333333;strokeWidth=0.8;")
            geo = ET.SubElement(cell, "mxGeometry", relative="1", attrib={"as": "geometry"})
            for name, x, y in [("sourcePoint", x1, y1), ("targetPoint", x2, y2)]:
                ET.SubElement(geo, "mxPoint", x=f"{x:g}", y=f"{y:g}", attrib={"as": name})

        # Las aristas se guardan antes de los cuadros para que no tapen sus textos.
        for i, edge in enumerate(pagina.edges):
            style = ("edgeStyle=none;rounded=0;html=0;strokeColor=#333333;strokeWidth=0.9;"
                     "startArrow=none;endArrow=none;jettySize=0;orthogonalLoop=1;")
            if edge["kind"] == "comp":
                style += "startArrow=diamond;startFill=1;startSize=12;"
            elif edge["kind"] == "agg":
                style += "startArrow=diamond;startFill=0;startSize=12;"
            elif edge["kind"] == "inherit":
                style += "endArrow=block;endFill=0;endSize=10;"
            elif edge["kind"] in {"assoc", "dep", "transition"}:
                style += "endArrow=open;endFill=0;endSize=9;"
            if edge["kind"] == "dep":
                style += "dashed=1;dashPattern=5 3;"
            attrs = dict(id=f"conexion-{i}", value="", edge="1", parent="1")
            for field, prefix, p in [("source", "exit", edge["points"][0]),
                                     ("target", "entry", edge["points"][-1])]:
                name = edge[field]
                if name:
                    attrs[field] = name
                    node = pagina.nodes[name]
                    nx = (p[0] - node["x"]) / node["w"]
                    ny = (p[1] - node["y"]) / node["h"]
                    style += f"{prefix}X={nx:.8f};{prefix}Y={ny:.8f};{prefix}Dx=0;{prefix}Dy=0;{prefix}Perimeter=0;"
            attrs["style"] = style
            cell = ET.SubElement(root, "mxCell", attrs)
            geo = ET.SubElement(cell, "mxGeometry", relative="1", attrib={"as": "geometry"})
            for name, p in [("sourcePoint", edge["points"][0]), ("targetPoint", edge["points"][-1])]:
                ET.SubElement(geo, "mxPoint", x=f"{p[0]:g}", y=f"{p[1]:g}", attrib={"as": name})
            waypoints = ET.SubElement(geo, "Array", attrib={"as": "points"})
            for x, y in edge["points"][1:-1]:
                ET.SubElement(waypoints, "mxPoint", x=f"{x:g}", y=f"{y:g}")

        text("titulo", pagina.title, 32, 12, 1120, 27, size=19, bold=True)
        text("subtitulo", pagina.subtitle, 32, 39, 1120, 21, size=10.2)
        rule("separador-cabecera", 32, 66, ancho - 32, 66)

        for name, node in pagina.nodes.items():
            w, h, th = node["w"], node["h"], node["title_h"]
            vertex(name, "", node["x"], node["y"], w, h,
                   "group;html=0;connectable=1;recursiveResize=0;rotatable=0;")
            vertex(name + "-caja", "", 0, 0, w, h,
                   "shape=rectangle;fillColor=#ffffff;strokeColor=#333333;strokeWidth=0.8;",
                   parent=name, connectable=False)
            vertex(name + "-cabecera", "", 0, 0, w, th,
                   "shape=rectangle;fillColor=#f1f1f1;strokeColor=#333333;strokeWidth=0.8;",
                   parent=name, connectable=False)
            if modelo[name]["abstracta"]:
                text(name + "-abstracta", "«abstract»", 0, 3, w, 13, 8.8, align="center", parent=name)
                text(name + "-nombre", name, 0, 16, w, 20, 11.5, bold=True, align="center", parent=name)
            else:
                text(name + "-nombre", name, 0, 2, w, 23, 11.5, bold=True, align="center", parent=name)
            if node["ah"]:
                rule(name + "-separador", 0, th + node["ah"], w, th + node["ah"], parent=name)
            for j, line in enumerate(node["a"]):
                text(f"{name}-atributo-{j}", line, 9, th + 6 + j * 12, w - 18, 12, parent=name)
            italic = False
            for j, line in enumerate(node["m"]):
                if line.startswith(("+ ", "# ", "- ")):
                    italic = any(line.startswith(prefix) for prefix in abstractos.get(name, ()))
                text(f"{name}-metodo-{j}", line, 9, th + node["ah"] + 6 + j * 12, w - 18, 12,
                     italic=italic, parent=name)
            if node["note"]:
                text(name + "-nota", node["note"], node["x"], node["y"] - 19, node["w"] + 100, 16, 8.3)

        for node in pagina.states:
            name, w, h = node["name"], node["w"], node["h"]
            vertex(name, "", node["x"], node["y"], w, h,
                   "group;html=0;recursiveResize=0;rotatable=0;")
            vertex(name + "-caja", "", 0, 0, w, h,
                   "rounded=1;arcSize=12;absoluteArcSize=1;fillColor=#ffffff;strokeColor=#333333;strokeWidth=0.8;",
                   parent=name, connectable=False)
            text(name + "-nombre", name, 0, 8, w, 30, 14, bold=True, align="center", parent=name)
            rule(name + "-separador", 0, 42, w, 42, parent=name)
            for j, line in enumerate(node["lines"]):
                text(f"{name}-accion-{j}", line, 14, 51 + j * 17, w - 28, 18, 10, parent=name)

        for i, (x, y, r) in enumerate(pagina.initials):
            vertex(f"inicio-{i}", "", x - r, y - r, 2*r, 2*r,
                   "shape=ellipse;fillColor=#333333;strokeColor=#333333;")
        for i, (x, y, value, size, bold) in enumerate(pagina.notes):
            text(f"nota-{i}", value, x, y - size - 2, ancho - x - 25, size + 8, size, bold)
        for i, edge in enumerate(pagina.edges):
            if edge.get("label_at"):
                x, y = edge["label_at"]
                # Ancho ajustado al texto para conservar el espacio de las flechas.
                width = min(ancho - x - 20, max(50, len(edge["label"]) * 5.1))
                text(f"etiqueta-{i}", edge["label"], x - 2, y - 11, width + 4, 15, 8.8, background=True)
            for j, (value, x, y) in enumerate(edge.get("mults") or []):
                text(f"multiplicidad-{i}-{j}", value, x, y - 11, max(14, len(value) * 5.4), 15, 8.5, background=True)
        rule("separador-pie", 32, alto - 44, ancho - 32, alto - 44)
        text("pie", "Propuesta v1 | - privado; # protegido; + público | Ver explicación en LEEME.md",
             32, alto - 40, 1120, 15, 8.5)
        text("estado-del-modelo", "Diseño propuesto para implementar - 19/11/2026", 32, alto - 24, 1120, 15, 8.2)

        individual = ET.Element("mxfile", host="app.diagrams.net", type="device", compressed="false")
        individual.append(deepcopy(diagram))
        ET.indent(individual)
        path = individuales / (pagina.filename + ".drawio")
        ET.ElementTree(individual).write(path, encoding="utf-8", xml_declaration=True)
        combinado.append(diagram)
    ET.indent(combinado)
    ET.ElementTree(combinado).write(destino / "UML_Fuga_Prision_v1.drawio", encoding="utf-8", xml_declaration=True)
