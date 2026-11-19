"""Genera la propuesta UML; no implementa ni modifica el videojuego."""
from pathlib import Path
from html import escape
import json
import math
import textwrap
import subprocess
import xml.etree.ElementTree as ET

from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.pagesizes import A3, landscape

ROOT = Path(__file__).resolve().parents[1]
ROOT.mkdir(parents=True, exist_ok=True)
for folder in ("svg", "imagenes"):
    (ROOT / folder).mkdir(exist_ok=True)
FONT_DIR = Path("/usr/share/fonts/truetype/dejavu")
for name, file in [("UML", "DejaVuSans.ttf"), ("UML-Bold", "DejaVuSans-Bold.ttf"), ("UML-Italic", "DejaVuSans-Oblique.ttf")]:
    pdfmetrics.registerFont(TTFont(name, str(FONT_DIR / file)))
W, H = landscape(A3)

# Un único catálogo mantiene coherentes las clases repetidas en distintas vistas.
MODEL = {}
def cls(name, attrs=(), methods=(), abstract=False):
    MODEL[name] = {"atributos": list(attrs), "metodos": list(methods), "abstracta": abstract}

cls("Juego", ["- nivel_actual: Nivel", "- estado_actual: EstadoJuego", "- puntaje: Puntaje", "- puntos_inicio_nivel: int", "- vista: Vista"], [
    "+ iniciar(): None", "+ cargar_nivel(numero: int): None", "+ cambiar_estado(estado: EstadoJuego): None",
    "+ procesar_evento(evento: Event): None", "+ update(dt: float): None", "+ actualizar_nivel(dt: float): None",
    "+ dibujar(): None", "+ siguiente_nivel(): None", "+ reiniciar_nivel(): None", "+ reiniciar_partida(): None",
    "+ get_nivel(): Nivel", "+ get_puntaje(): Puntaje", "+ get_estado(): EstadoJuego"])
cls("Nivel", ["- numero: int", "- mapa: Mapa", "- colisiones: SistemaColisiones", "- personajes: list<Personaje>",
    "- camaras: list<Camara>", "- llave: Llave", "- puerta: Puerta", "- panel: PanelSeguridad [0..1]"], [
    "+ agregar_guardia(guardia: Guardia): None", "+ get_numero(): int", "+ get_mapa(): Mapa",
    "+ get_colisiones(): SistemaColisiones", "+ get_personajes(): list<Personaje>", "+ get_prisionero(): Prisionero",
    "+ get_guardias(): list<Guardia>", "+ get_camaras(): list<Camara>", "+ get_llave(): Llave",
    "+ get_puerta(): Puerta", "+ get_panel(): PanelSeguridad | None"])
cls("Mapa", ["- plano: list<str>", "- muros: list<Rect>"], ["+ get_muros(): list<Rect>", "+ get_dimensiones(): tuple"])
cls("SistemaColisiones", ["- mapa: Mapa"], [
    "+ puede_mover(rect: Rect, dx: float, dy: float): bool",
    "+ mover(rect: Rect, dx: float, dy: float): Rect", "+ toca(a: Rect, b: Rect): bool"])
cls("Vista", ["- pantalla: Surface"], ["+ dibujar(juego: Juego): None", "+ dibujar_pausa(): None", "+ dibujar_resultado(victoria: bool): None"])
cls("Puntaje", ["- valor: int"], ["+ get_valor(): int", "+ sumar(cantidad: int): None", "+ restaurar(valor: int): None", "+ reiniciar(): None"])
cls("Personaje", ["- rect: Rect", "- velocidad: float", "- colisiones: SistemaColisiones"], [
    "+ get_rect(): Rect", "+ mover(dx: float, dy: float, dt: float): None", "+ update(dt: float): None"], True)
cls("Prisionero", ["- llave_obtenida: bool", "- direccion: tuple"], [
    "+ set_direccion(dx: int, dy: int): None", "+ recoger_llave(): None", "+ tiene_llave(): bool", "+ update(dt: float): None"])
cls("Guardia", ["- alerta: bool", "- objetivo: tuple"], [
    "+ alertar(posicion: tuple): None", "+ dejar_alerta(): None", "# perseguir(dt: float): None", "+ update(dt: float): None"], True)
cls("GuardiaPatrulla", ["- ruta: list<tuple>", "- indice: int"], ["+ update(dt: float): None"])
cls("GuardiaCentinela", ["- origen: tuple"], ["+ update(dt: float): None"])
cls("Camara", ["- zona: Rect", "- activa: bool"], [
    "+ detectar(rect: Rect): bool", "+ activar(): None", "+ desactivar(): None", "+ get_zona(): Rect"])
cls("Llave", ["- rect: Rect", "- recogida: bool"], ["+ get_rect(): Rect", "+ recoger(): bool", "+ esta_recogida(): bool"])
cls("Puerta", ["- rect: Rect", "- abierta: bool"], ["+ get_rect(): Rect", "+ abrir(): None", "+ esta_abierta(): bool"])
cls("PanelSeguridad", ["- rect: Rect", "- utilizado: bool", "- tiempo_restante: float", "- camaras: list<Camara>"], [
    "+ get_rect(): Rect", "+ activar(): bool", "+ update(dt: float): None", "+ esta_activo(): bool"])
cls("CreadorGuardia", [], [
    "+ crear(datos: dict, colisiones: SistemaColisiones): Guardia",
    "+ incorporar(nivel: Nivel, datos: dict): None"], True)
cls("CreadorPatrulla", [], ["+ crear(datos: dict, colisiones: SistemaColisiones): Guardia"])
cls("CreadorCentinela", [], ["+ crear(datos: dict, colisiones: SistemaColisiones): Guardia"])
cls("EstadoJuego", ["# juego: Juego"], ["+ manejar_evento(evento: Event): None", "+ update(dt: float): None"], True)
for name in ("Jugando", "Pausa", "Derrota", "Victoria"):
    cls(name, [], ["+ manejar_evento(evento: Event): None", "+ update(dt: float): None"])

ABSTRACT_METHODS = {
    "Personaje": ("+ update(",), "Guardia": ("+ update(",),
    "CreadorGuardia": ("+ crear(",),
    "EstadoJuego": ("+ manejar_evento(", "+ update("),
}

def wrap_line(value, width, size=9.4):
    if pdfmetrics.stringWidth(value, "UML", size) <= width:
        return [value]
    words = value.split(" ")
    lines, current = [], ""
    for word in words:
        proposed = (current + " " + word).strip()
        if current and pdfmetrics.stringWidth(proposed, "UML", size) > width:
            lines.append(current)
            current = "    " + word
        else:
            current = proposed
    if current:
        lines.append(current)
    return lines

PDF = canvas.Canvas(str(ROOT / "UML_Fuga_Prision_v1.pdf"), pagesize=(W, H))
PDF.setTitle("Fuga de la Prision - Propuesta UML v1")
PDF.setAuthor("Equipo del proyecto")
PAGES = []

class Sheet:
    def __init__(self, filename, title, subtitle):
        self.filename, self.title, self.subtitle = filename, title, subtitle
        self.svg = []
        self.nodes, self.edges, self.states, self.notes, self.initials = {}, [], [], [], []
        self.rect(0, 0, W, H, fill="#ffffff", stroke="none")
        self.text(32, 32, title, 19, bold=True)
        self.text(32, 53, subtitle, 10.2)
        self.line([(32, 66), (W-32, 66)], width=.7)

    def line(self, points, width=.9, dashed=False, color="#333333"):
        PDF.setStrokeColor(color)
        PDF.setLineWidth(width)
        PDF.setDash([5, 3] if dashed else [])
        p = PDF.beginPath()
        p.moveTo(points[0][0], H-points[0][1])
        for x, y in points[1:]: p.lineTo(x, H-y)
        PDF.drawPath(p)
        dash = ' stroke-dasharray="5 3"' if dashed else ''
        self.svg.append(f'<polyline points="{" ".join(f"{x:.2f},{y:.2f}" for x,y in points)}" fill="none" stroke="{color}" stroke-width="{width}"{dash}/>')

    def rect(self, x, y, w, h, fill="#ffffff", stroke="#333333", radius=0):
        PDF.setFillColor(fill)
        PDF.setStrokeColor("#ffffff" if stroke == "none" else stroke)
        PDF.setLineWidth(.8)
        PDF.setDash([])
        PDF.roundRect(x, H-y-h, w, h, radius, fill=1, stroke=int(stroke != "none"))
        self.svg.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{radius}" fill="{fill}" stroke="{stroke}" stroke-width=".8"/>')

    def polygon(self, points, fill="#ffffff"):
        PDF.setFillColor(fill)
        PDF.setStrokeColor("#333333")
        PDF.setDash([])
        p = PDF.beginPath()
        p.moveTo(points[0][0], H-points[0][1])
        for x,y in points[1:]: p.lineTo(x,H-y)
        p.close()
        PDF.drawPath(p,fill=1,stroke=1)
        self.svg.append(f'<polygon points="{" ".join(f"{x},{y}" for x,y in points)}" fill="{fill}" stroke="#333333" stroke-width=".9"/>')

    def circle(self,x,y,r):
        PDF.setFillColor("#333333")
        PDF.circle(x,H-y,r,fill=1,stroke=0)
        self.svg.append(f'<circle cx="{x}" cy="{y}" r="{r}" fill="#333333"/>')
        self.initials.append((x,y,r))

    def note(self,x,y,value,size=9.4,bold=False):
        self.notes.append((x,y,value,size,bold))
        self.text(x,y,value,size,bold=bold)

    def text(self, x, y, value, size=9.4, bold=False, align="left", color="#222222", italic=False):
        font = "UML-Bold" if bold else ("UML-Italic" if italic else "UML")
        PDF.setFont(font,size)
        PDF.setFillColor(color)
        fn = PDF.drawCentredString if align == "center" else PDF.drawString
        fn(x,H-y,value)
        anchor = ' text-anchor="middle"' if align == "center" else ''
        weight = ' font-weight="bold"' if bold else ''
        slant = ' font-style="italic"' if italic else ''
        self.svg.append(f'<text x="{x}" y="{y}" font-family="DejaVu Sans, sans-serif" font-size="{size}" fill="{color}"{anchor}{weight}{slant}>{escape(value)}</text>')

    def label(self,x,y,value,size=8.8):
        width=pdfmetrics.stringWidth(value,"UML",size)
        self.rect(x-3,y-size-2,width+6,size+5,stroke="none")
        self.text(x,y,value,size)

    def box(self,name,x,y,w, attrs=None, methods=None, note=""):
        model=MODEL[name]
        attrs=model["atributos"] if attrs is None else attrs
        methods=model["metodos"] if methods is None else methods
        assert set(attrs).issubset(model["atributos"])
        assert set(methods).issubset(model["metodos"])
        a=[s for line in attrs for s in wrap_line(line,w-18)]
        m=[s for line in (methods or [" "]) for s in wrap_line(line,w-18)]
        title_h=37 if model["abstracta"] else 26
        ah=max(23,len(a)*12+10) if a else 0
        mh=max(23,len(m)*12+10)
        h=title_h+ah+mh
        assert x>=25 and x+w<=W-25 and y>=75 and y+h<=H-58,(name,x,y,w,h)
        self.nodes[name]={"x":x,"y":y,"w":w,"h":h,"title_h":title_h,"ah":ah,
                          "a":a,"m":m,"attrs":attrs,"methods":methods,"note":note}
        return name

    def port(self,name,side,f=.5):
        n=self.nodes[name]
        if side=="L": return n["x"],n["y"]+n["h"]*f
        if side=="R": return n["x"]+n["w"],n["y"]+n["h"]*f
        if side=="T": return n["x"]+n["w"]*f,n["y"]
        return n["x"]+n["w"]*f,n["y"]+n["h"]

    def edge(self,source,target,points,kind="assoc",label="",label_at=None,mults=None):
        assert source in self.nodes and target in self.nodes
        self.edges.append(dict(source=source,target=target,points=points,kind=kind,label=label,label_at=label_at,mults=mults))

    def draw_edge(self,e):
        pts=e["points"]
        self.line(pts,dashed=e["kind"]=="dep")
        def direction(a,b):
            dx,dy=b[0]-a[0],b[1]-a[1]
            length=math.hypot(dx,dy)
            return dx/length,dy/length
        if e["kind"] in ("comp","agg"):
            x,y=pts[0];ux,uy=direction(pts[0],pts[1]);px,py=-uy,ux
            self.polygon([(x,y),(x+ux*8+px*4,y+uy*8+py*4),(x+ux*16,y+uy*16),(x+ux*8-px*4,y+uy*8-py*4)],
                         "#333333" if e["kind"]=="comp" else "#ffffff")
        if e["kind"] in ("inherit","assoc","dep"):
            x,y=pts[-1];ux,uy=direction(pts[-2],pts[-1]);px,py=-uy,ux
            ends=[(x-ux*11+px*5,y-uy*11+py*5),(x,y),(x-ux*11-px*5,y-uy*11-py*5)]
            if e["kind"]=="inherit": self.polygon(ends)
            else:self.line(ends)
        if e.get("label_at"): self.label(*e["label_at"],e["label"])
        for label,x,y in e.get("mults") or []: self.label(x,y,label,8.5)

    def finish(self,footer):
        for e in self.edges:self.draw_edge(e)
        for name,n in self.nodes.items():
            x,y,w,h=n["x"],n["y"],n["w"],n["h"]
            self.rect(x,y,w,h)
            self.rect(x,y,w,n["title_h"],fill="#f1f1f1")
            if MODEL[name]["abstracta"]:
                self.text(x+w/2,y+13,"«abstract»",8.8,align="center")
                self.text(x+w/2,y+29,name,11.5,bold=True,align="center")
            else:self.text(x+w/2,y+18,name,11.5,bold=True,align="center")
            split=y+n["title_h"]+n["ah"]
            self.line([(x,split),(x+w,split)],width=.7)
            for i,line in enumerate(n["a"]): self.text(x+9,y+n["title_h"]+16+i*12,line)
            for i,line in enumerate(n["m"]):
                abstract=any(line.startswith(p) for p in ABSTRACT_METHODS.get(name,()))
                self.text(x+9,split+16+i*12,line,italic=abstract)
            if n["note"]:self.text(x,y-6,n["note"],8.3)
        self.line([(32,H-44),(W-32,H-44)],width=.6)
        self.text(32,H-28,footer,8.5)
        self.text(32,H-13,"Propuesta v1 - 19/11/2026 | Diseño objetivo; no representa todavía una refactorización del código.",8.2)
        self.save()

    def save(self):
        (ROOT/"svg"/(self.filename+".svg")).write_text(f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}pt" height="{H}pt" viewBox="0 0 {W} {H}">'+"\n".join(self.svg)+"</svg>",encoding="utf-8")
        PAGES.append(self)
        PDF.showPage()

def join(s,a,sidea,b,sideb,kind="assoc",via=(),label="",label_at=None,mults=None,fa=.5,fb=.5):
    p,q=s.port(a,sidea,fa),s.port(b,sideb,fb)
    if not via and p[0]!=q[0] and p[1]!=q[1]:
        if sidea in ("L","R"):
            mid=(p[0]+q[0])/2
            via=[(mid,p[1]),(mid,q[1])]
        else:
            mid=(p[1]+q[1])/2
            via=[(p[0],mid),(q[0],mid)]
    elif via:
        via=list(via)
        first=via[0]
        if p[0]!=first[0] and p[1]!=first[1]:
            via.insert(0,(first[0],p[1]) if sidea in ("L","R") else (p[0],first[1]))
        last=via[-1]
        if q[0]!=last[0] and q[1]!=last[1]:
            via.append((last[0],q[1]) if sideb in ("L","R") else (q[0],last[1]))
    points=[p,*via,q]
    points=[v for i,v in enumerate(points) if i==0 or v!=points[i-1]]
    clean=[]
    for v in points:
        while len(clean)>1 and ((clean[-2][0]==clean[-1][0]==v[0]) or (clean[-2][1]==clean[-1][1]==v[1])):
            clean.pop()
        clean.append(v)
    points=clean
    s.edge(a,b,points,kind,label,label_at,mults)

# 01: coordinación y colaboradores.
s=Sheet("01_estructura_principal","01. Estructura principal","Coordinación, datos del nivel, dibujo y colisiones. Las entidades se detallan en 02; los patrones, en 03 y 04.")
s.box("Juego",45,210,335)
s.box("Nivel",490,155,345)
s.box("Vista",45,83,335)
s.box("EstadoJuego",45,620,335)
s.box("CreadorGuardia",885,90,270)
s.box("Mapa",885,360,270)
s.box("SistemaColisiones",885,565,270)
s.box("Puntaje",490,640,345)
join(s,"Juego","R","Nivel","L","comp",label="nivel actual",label_at=(390,285),mults=[("1",385,370),("1",475,315)])
join(s,"Juego","T","Vista","B","comp",mults=[("1",225,199),("1",225,190)])
join(s,"Juego","B","EstadoJuego","T","comp",label="estado actual",label_at=(225,580),mults=[("1",225,548),("1",225,610)])
join(s,"Juego","R","Puntaje","L","comp",via=[(430,440),(430,680)],fa=.85,label="puntaje de campaña",label_at=(440,625))
join(s,"Juego","R","CreadorGuardia","L","dep",via=[(425,245),(425,117)],fa=.12,label="usa al cargar el nivel",label_at=(510,110))
join(s,"Nivel","R","Mapa","L","comp",fa=.68,label="mapa propio",label_at=(846,330))
join(s,"Nivel","R","SistemaColisiones","L","comp",via=[(855,455),(855,620)],fa=.90,label="colisiones del nivel",label_at=(860,543))
join(s,"SistemaColisiones","T","Mapa","B","assoc",label="consulta",label_at=(1030,522),mults=[("1",1002,554),("1",1002,473)])
join(s,"Vista","L","Juego","L","dep",via=[(28,136),(28,310)],label="dibuja",label_at=(33,195))
s.finish("- privado | # protegido | + público | rombo negro: composición | rombo blanco: agregación | triángulo vacío: herencia")

# 02: entidades y relaciones de pertenencia.
s=Sheet("02_personajes_y_seguridad","02. Personajes y seguridad","El nivel posee sus entidades. PanelSeguridad comparte referencias a cámaras que pertenecen al nivel.")
s.box("Personaje",40,110,275)
s.box("Nivel",400,100,350,attrs=["- personajes: list<Personaje>","- camaras: list<Camara>","- llave: Llave","- puerta: Puerta","- panel: PanelSeguridad [0..1]"],methods=["+ agregar_guardia(guardia: Guardia): None"],note="Nivel resumido; definición completa en 01.")
s.box("PanelSeguridad",850,95,300)
s.box("Prisionero",40,405,275)
s.box("Guardia",400,405,350)
s.box("Camara",850,405,300)
s.box("Llave",40,655,275)
s.box("GuardiaPatrulla",400,675,170)
s.box("GuardiaCentinela",600,675,170)
s.box("Puerta",850,655,300)
join(s,"Prisionero","T","Personaje","B","inherit")
join(s,"Guardia","T","Personaje","B","inherit",via=[(575,350),(177.5,350)])
join(s,"GuardiaPatrulla","T","Guardia","B","inherit",via=[(485,630),(575,630)])
join(s,"GuardiaCentinela","T","Guardia","B","inherit",via=[(685,630),(575,630)])
join(s,"Nivel","L","Personaje","R","comp",label="personajes",label_at=(325,145),mults=[("1",383,185),("1..*",318,163)])
join(s,"Nivel","R","PanelSeguridad","L","comp",label="panel",label_at=(765,140),mults=[("1",760,185),("0..1",823,185)])
join(s,"Nivel","R","Camara","L","comp",via=[(818,240),(818,470)],fa=.72,label="cámaras",label_at=(759,335),mults=[("0..*",823,490)])
join(s,"Nivel","L","Llave","R","comp",via=[(335,255),(335,707)],fa=.85,mults=[("1",318,728)])
join(s,"Nivel","R","Puerta","L","comp",via=[(795,270),(795,707)],fa=.9,mults=[("1",830,728)])
join(s,"PanelSeguridad","B","Camara","T","agg",label="controla",label_at=(1010,351),mults=[("0..1",1010,331),("0..*",1010,393)])
s.finish("Personaje.update(dt) es abstracto; Guardia lo mantiene abstracto. Prisionero y los dos guardias concretos lo implementan.")

# 03: Factory Method auténtico, con una operación común que usa el método fábrica.
s=Sheet("03_factory_method","03. Factory Method","incorporar() reutiliza el procedimiento común; crear() es el método fábrica que cada creador concreto redefine.")
s.box("CreadorGuardia",55,135,475)
s.box("Guardia",765,135,380)
s.box("CreadorPatrulla",55,445,325)
s.box("CreadorCentinela",55,650,325)
s.box("GuardiaPatrulla",820,445,325)
s.box("GuardiaCentinela",820,650,325)
s.box("Nivel",455,350,300,attrs=[],methods=["+ agregar_guardia(guardia: Guardia): None"],note="Nivel resumido; definición completa en 01.")
join(s,"CreadorPatrulla","L","CreadorGuardia","L","inherit",via=[(30,490),(30,185)])
join(s,"CreadorCentinela","L","CreadorGuardia","L","inherit",via=[(27,695),(27,185)])
join(s,"GuardiaPatrulla","T","Guardia","B","inherit")
join(s,"GuardiaCentinela","R","Guardia","R","inherit",via=[(1164,697),(1164,210)])
join(s,"CreadorGuardia","R","Guardia","L","dep",label="crear() devuelve",label_at=(570,160))
join(s,"CreadorGuardia","B","Nivel","L","dep",via=[(292.5,300),(420,300),(420,389)],label="incorpora al nivel",label_at=(440,315))
join(s,"CreadorPatrulla","R","GuardiaPatrulla","L","dep",label="crea",label_at=(575,455))
join(s,"CreadorCentinela","R","GuardiaCentinela","L","dep",label="crea",label_at=(575,660))
s.note(455,565,"Procedimiento común de incorporar():",10.5,bold=True)
s.note(455,588,"1. guardia = self.crear(datos, colisiones)",9.7)
s.note(455,610,"2. nivel.agregar_guardia(guardia)",9.7)
s.note(455,636,"El creador concreto decide la clase del guardia.",9.1)
s.finish("Producto: Guardia | Productos concretos: GuardiaPatrulla y GuardiaCentinela | Método fábrica: crear()")

# 04: clases del patrón State.
s=Sheet("04_state_clases","04. State: diagrama de clases","Juego conserva un EstadoJuego y delega en él el manejo de eventos y la actualización.")
s.box("Juego",435,95,320,attrs=["- nivel_actual: Nivel","- estado_actual: EstadoJuego"],methods=[
    "+ cambiar_estado(estado: EstadoJuego): None", "+ procesar_evento(evento: Event): None", "+ update(dt: float): None",
    "+ actualizar_nivel(dt: float): None", "+ siguiente_nivel(): None", "+ reiniciar_nivel(): None", "+ reiniciar_partida(): None"],note="Juego resumido; definición completa en 01.")
s.box("EstadoJuego",435,420,320)
for name,x in [("Jugando",35),("Pausa",330),("Derrota",625),("Victoria",920)]:s.box(name,x,650,235)
join(s,"Juego","B","EstadoJuego","T","comp",label="estado actual",label_at=(605,385),mults=[("1",605,360),("1",605,411)])
join(s,"EstadoJuego","R","Juego","R","assoc",via=[(805,465),(805,215)],label="contexto recibido",label_at=(820,355))
for name in ["Jugando","Pausa","Derrota","Victoria"]:
    p=s.port(name,"T")
    join(s,name,"T","EstadoJuego","B","inherit",via=[(p[0],605),(595,605)])
s.note(35,575,"Jugando.update(dt) llama a Juego.actualizar_nivel(dt). Pausa.update(dt) mantiene detenido el nivel.",10)
s.finish("# juego es protegido para que los estados concretos consulten el contexto. Los atributos de dominio siguen siendo privados.")

# 05: máquina de estados UML, complementaria al diagrama de clases.
s=Sheet("05_state_transiciones","05. State: transiciones de la partida","Cuatro estados concretos. El avance entre niveles se realiza durante Jugando, sin añadir otra clase de estado.")
def state(name,x,y,w,h,lines):
    s.rect(x,y,w,h,radius=12)
    s.text(x+w/2,y+29,name,14,bold=True,align="center")
    s.line([(x,y+42),(x+w,y+42)],width=.6)
    for i,line in enumerate(lines):s.text(x+14,y+64+i*17,line,10)
    s.states.append(dict(name=name,x=x,y=y,w=w,h=h,lines=lines))
state("Jugando",420,185,350,145,["Actualiza personajes, cámaras y panel.","Resuelve contactos y suma puntos."])
state("Pausa",50,440,290,115,["Conserva la partida detenida."])
state("Derrota",450,570,290,115,["Espera el reinicio del nivel."])
state("Victoria",850,440,290,115,["La última salida fue alcanzada."])
def transition(points,label,x,y):
    s.draw_edge(dict(points=points,kind="assoc",label=label,label_at=(x,y),mults=None))
    s.edges.append(dict(source="",target="",points=points,kind="transition",label=label,label_at=(x,y),mults=None))
s.circle(576,108,6)
transition([(576,114),(576,185)],"iniciar partida",590,153)
transition([(420,255),(195,255),(195,440)],"P / Esc",235,245)
transition([(340,480),(385,480),(385,300),(420,300)],"P / Esc",305,367)
transition([(595,330),(595,570)],"contacto con un guardia",610,475)
transition([(450,625),(380,625),(380,360),(455,360),(455,330)],"R / reiniciar nivel",225,600)
transition([(770,255),(995,255),(995,440)],"salida [último nivel]",820,245)
transition([(1140,490),(1164,490),(1164,125),(695,125),(695,185)],"R / nueva partida",900,115)
transition([(770,300),(805,300),(805,365),(735,365),(735,330)],"salida [quedan niveles] / siguiente nivel",795,392)
s.note(50,735,"Cerrar la ventana finaliza la aplicación desde cualquier estado.",10)
s.line([(32,H-44),(W-32,H-44)],width=.6)
s.text(32,H-28,"Las etiquetas expresan evento [condición] / acción. P y Esc cambian entre Jugando y Pausa.",8.5)
s.text(32,H-13,"Propuesta v1 - 19/11/2026 | Diagrama de comportamiento; no constituye código implementado.",8.2)
s.save()
PDF.save()

# Archivos nativos de diagrams.net, uno por lámina y un combinado.
from exportar_drawio import exportar_drawio
exportar_drawio(ROOT, PAGES, MODEL, ABSTRACT_METHODS, W, H)
(ROOT/"fuentes"/"modelo.json").write_text(json.dumps(MODEL,ensure_ascii=False,indent=2),encoding="utf-8")

coverage={name:[i+1 for i,s in enumerate(PAGES) if name in s.nodes] for name in MODEL}
assert len(MODEL)==23
assert all(coverage.values()),coverage
for s in PAGES:
    nodes=list(s.nodes.items())
    for i,(name,a) in enumerate(nodes):
        for other,b in nodes[i+1:]:
            overlap=min(a['x']+a['w'],b['x']+b['w'])-max(a['x'],b['x'])>0 and min(a['y']+a['h'],b['y']+b['h'])-max(a['y'],b['y'])>0
            assert not overlap,(s.filename,name,other)
    for e in s.edges:
        if e['kind']=='transition':continue
        for p,q in zip(e['points'],e['points'][1:]):
            for name,b in s.nodes.items():
                if name in (e['source'],e['target']):continue
                # Intersección de segmentos con el interior de otras cajas.
                if p[0]==q[0] and b['x']+1<p[0]<b['x']+b['w']-1:
                    assert min(max(p[1],q[1]),b['y']+b['h']-1)<=max(min(p[1],q[1]),b['y']+1),(s.filename,e['source'],e['target'],name)
                if p[1]==q[1] and b['y']+1<p[1]<b['y']+b['h']-1:
                    assert min(max(p[0],q[0]),b['x']+b['w']-1)<=max(min(p[0],q[0]),b['x']+1),(s.filename,e['source'],e['target'],name)
(ROOT/"fuentes"/"cobertura.json").write_text(json.dumps(coverage,indent=2),encoding="utf-8")
subprocess.run(["pdftoppm","-scale-to","2300","-png",str(ROOT/"UML_Fuga_Prision_v1.pdf"),str(ROOT/"imagenes"/"lamina")],check=True)
for i,s in enumerate(PAGES,1):
    (ROOT/"imagenes"/f"lamina-{i}.png").replace(ROOT/"imagenes"/(s.filename+".png"))
print(f'{len(MODEL)} clases, {len(PAGES)} láminas. PDF, SVG y archivo editable generados en {ROOT}')
