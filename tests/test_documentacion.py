"""Evita que el UML y la guía vuelvan a omitir clases o mostrar código antiguo."""
import ast
from pathlib import Path
import re
import unittest

RAIZ = Path(__file__).resolve().parents[1]


def clases_del_juego():
    clases = {}
    for archivo in (RAIZ / "src").glob("*.py"):
        for nodo in ast.parse(archivo.read_text(encoding="utf-8")).body:
            if isinstance(nodo, ast.ClassDef):
                clases[nodo.name] = nodo
    return clases


class PruebasDocumentacion(unittest.TestCase):
    def test_uml_incluye_clases_atributos_metodos_y_relaciones_reales(self):
        clases = clases_del_juego()
        uml = (RAIZ / "docs/diagramas/modelo_parcial.mmd").read_text(encoding="utf-8")
        cajas = dict(re.findall(r"class (\w+) \{(.*?)\n\}", uml, re.S))
        self.assertEqual(set(cajas), set(clases))
        for nombre, nodo in clases.items():
            atributos = set()
            for parte in ast.walk(nodo):
                if (isinstance(parte, ast.Attribute) and isinstance(parte.ctx, ast.Store)
                        and isinstance(parte.value, ast.Name) and parte.value.id == "self"):
                    atributos.add(parte.attr)
            for parte in nodo.body:
                if isinstance(parte, ast.AnnAssign) and isinstance(parte.target, ast.Name):
                    atributos.add(parte.target.id)
                elif isinstance(parte, ast.Assign):
                    atributos.update(t.id for t in parte.targets if isinstance(t, ast.Name))
                elif isinstance(parte, ast.FunctionDef):
                    if any(isinstance(d, ast.Name) and d.id == "property" for d in parte.decorator_list):
                        atributos.add(parte.name)
                    elif parte.name != "__init__":
                        parametros = ", ".join(a.arg for a in parte.args.args if a.arg != "self")
                        self.assertIn(f"{parte.name}({parametros})", cajas[nombre])
            atributos_uml = set(re.findall(r"^\s*[+#-](\w+):", cajas[nombre], re.M))
            self.assertEqual(atributos_uml, atributos, nombre)
            for base in nodo.bases:
                if isinstance(base, ast.Name) and base.id in clases:
                    self.assertIn(f"{base.id} <|-- {nombre}", uml)
        for propietario, tipo, parte, atributo in re.findall(
                r'(\w+) "[\d.*]+" ([*o])-- "[\d.*]+" (\w+) : (\w+)', uml):
            self.assertRegex(cajas[propietario], rf"{atributo}: [^\n]*\b{parte}\b")

    def test_guia_contiene_el_codigo_actual_completo_de_cada_clase(self):
        clases = clases_del_juego()
        guia = (RAIZ / "docs/Explicacion_de_clases.md").read_text(encoding="utf-8")
        documentadas = {}
        for bloque in re.findall(r"```python\n(.*?)\n```", guia, re.S):
            nodo = ast.parse(bloque).body[0]
            self.assertIsInstance(nodo, ast.ClassDef)
            self.assertNotIn(nodo.name, documentadas)
            documentadas[nodo.name] = nodo
        self.assertEqual(set(documentadas), set(clases))
        for nombre in clases:
            self.assertEqual(ast.dump(clases[nombre]), ast.dump(documentadas[nombre]), nombre)
