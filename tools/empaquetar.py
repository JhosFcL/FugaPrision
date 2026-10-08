"""Empaqueta el parcial sin entornos, cachés ni archivos temporales."""
import hashlib
import json
from pathlib import Path
import zipfile

raiz = Path(__file__).resolve().parents[1]
destino = raiz.parent / "Entregable_Parcial_Fuga_Prision.zip"
excluidos = {".git", ".venv", "venv", "__pycache__", ".pytest_cache", "tmp"}
archivos = []
for archivo in raiz.rglob("*"):
    relativo = archivo.relative_to(raiz)
    if archivo.is_file() and not any(parte in excluidos for parte in relativo.parts):
        if not archivo.name.startswith("~$") and archivo.suffix not in (".pyc", ".pyo"):
            archivos.append(archivo)
manifest = {}
with zipfile.ZipFile(destino, "w", zipfile.ZIP_DEFLATED) as paquete:
    for archivo in sorted(archivos):
        nombre = "Proyecto_Fuga_Prision/" + archivo.relative_to(raiz).as_posix()
        datos = archivo.read_bytes()
        paquete.writestr(nombre, datos)
        manifest[nombre] = hashlib.sha256(datos).hexdigest()
    paquete.writestr("MANIFIESTO_SHA256.json", json.dumps(manifest, indent=2, ensure_ascii=False))
with zipfile.ZipFile(destino) as paquete:
    assert paquete.testzip() is None
    for nombre, esperado in manifest.items():
        assert hashlib.sha256(paquete.read(nombre)).hexdigest() == esperado
    for obligatorio in ("main.py", "requirements.txt", "entrega/Informe_Parcial_Fuga_Prision.docx",
                        "entrega/Informe_Parcial_Fuga_Prision.pdf", "entrega/historial_git.bundle",
                        "tests/test_juego.py", "docs/03_guion_exposicion.md"):
        assert "Proyecto_Fuga_Prision/" + obligatorio in paquete.namelist()
print(json.dumps({"zip": str(destino), "archivos": len(archivos), "bytes": destino.stat().st_size,
                  "integridad": "testzip y SHA256 de todos los archivos correctos"}, ensure_ascii=False, indent=2))
