"""
ui/mapa.py
Pantalla con mapa interactivo de Tuluá usando tkintermapview.
Muestra marcadores por restaurante; al hacer clic abre el popup de info.
"""

import tkinter as tk
import json
import os
import webbrowser

try:
    import tkintermapview
    MAPA_DISPONIBLE = True
except ImportError:
    MAPA_DISPONIBLE = False

# ── Paleta ────────────────────────────────────────────────────────────────────
BG_PRINCIPAL  = "#0F1923"
BG_HEADER     = "#111D2B"
BG_CARD       = "#1A2535"
BG_CARD_HOVER = "#1F2E42"
COLOR_ACENTO  = "#FF6B35"
COLOR_TEXTO   = "#F0EDE8"
COLOR_GRIS    = "#8A9BB0"
COLOR_BORDE   = "#2A3D55"
COLOR_VERDE   = "#2ECC71"

COLORES_CAT = {
    "Almuerzos":     "#E8593C",
    "Comida Rápida": "#F0A500",
    "Bebidas":       "#2196A6",
}

# ── Coordenadas reales de restaurantes en Tuluá ───────────────────────────────
# Si un restaurante no tiene coordenadas definidas aquí, se ubica en el centro
COORDENADAS = {
    "r011": (4.08370, -76.19800),   # El Rancho – Calle 41a #2-41
    "r001": (4.08700, -76.19500),
    "r002": (4.08500, -76.19600),
    "r003": (4.08200, -76.19700),
    "r004": (4.08900, -76.19300),
    "r005": (4.08100, -76.19900),
    "r006": (4.08600, -76.20100),
    "r007": (4.08300, -76.20000),
    "r008": (4.08800, -76.19700),
    "r009": (4.08400, -76.19400),
    "r010": (4.08000, -76.19600),
}

# Centro de Tuluá
TULUA_LAT = 4.08377
TULUA_LON = -76.19649


def _leer_restaurantes() -> list:
    ruta = os.path.join(
        os.path.dirname(os.path.dirname(__file__)), "datos", "restaurantes.json"
    )
    try:
        with open(ruta, encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return []


# ── Popup (reutilizado del módulo restaurantes) ───────────────────────────────
class PopupRestaurante(tk.Toplevel):
    def __init__(self, parent, restaurante: dict):
        super().__init__(parent)
        self.title(restaurante.get("nombre", "Restaurante"))
        self.configure(bg=BG_PRINCIPAL)
        self.resizable(False, False)
        self.transient(parent)
        self.grab_set()

        parent.update_idletasks()
        px = parent.winfo_rootx()
        py = parent.winfo_rooty()
        pw = parent.winfo_width()
        ph = parent.winfo_height()
        w, h = 420, 460
        self.geometry(f"{w}x{h}+{px + (pw-w)//2}+{py + (ph-h)//2}")

        self._r = restaurante
        self._construir()

    def _construir(self):
        r = self._r
        categoria = r.get("categoria", "")
        color_cat = COLORES_CAT.get(categoria, COLOR_ACENTO)

        tk.Frame(self, bg=color_cat, height=5).pack(fill="x")

        cab = tk.Frame(self, bg=BG_HEADER, pady=16)
        cab.pack(fill="x")
        tk.Label(cab, text=r.get("imagen_emoji", "🍽️"),
                 font=("Helvetica", 34), bg=BG_HEADER).pack()
        tk.Label(cab, text=r.get("nombre", "—"),
                 font=("Georgia", 15, "bold"),
                 bg=BG_HEADER, fg=COLOR_TEXTO, wraplength=360).pack(pady=(4, 0))
        if categoria:
            tk.Label(cab, text=categoria,
                     font=("Helvetica", 9, "bold"),
                     bg=color_cat, fg="#FFFFFF", padx=8, pady=3).pack(pady=(6, 0))

        tk.Frame(self, bg=COLOR_BORDE, height=1).pack(fill="x")

        cuerpo = tk.Frame(self, bg=BG_PRINCIPAL, padx=26, pady=16)
        cuerpo.pack(fill="both", expand=True)

        desc = r.get("descripcion", "")
        if desc:
            tk.Label(cuerpo, text=desc, font=("Helvetica", 10),
                     bg=BG_PRINCIPAL, fg=COLOR_TEXTO,
                     wraplength=360, justify="center").pack(pady=(0, 12))

        self._fila(cuerpo, "📍", r.get("direccion", ""))
        self._fila(cuerpo, "📞", r.get("telefono", ""))
        self._fila(cuerpo, "🕐", r.get("horario", ""))

        n = len(r.get("productos", []))
        if n:
            self._fila(cuerpo, "🍴", f"{n} productos en carta")

        btns = tk.Frame(cuerpo, bg=BG_PRINCIPAL)
        btns.pack(pady=(16, 0))

        direccion = r.get("direccion", "")
        if direccion:
            q = direccion.replace(" ", "+")
            tk.Button(
                btns, text="📍 Ver en mapa",
                font=("Helvetica", 10, "bold"),
                bg=COLOR_ACENTO, fg="#FFFFFF", bd=0,
                padx=14, pady=7, cursor="hand2",
                activebackground="#e05a25", activeforeground="#FFFFFF",
                command=lambda: webbrowser.open(
                    f"https://www.google.com/maps/search/?api=1&query={q}"
                ),
            ).pack(side="left", padx=5)

        tel = r.get("telefono", "").replace(" ", "").replace("-", "")
        if tel:
            tk.Button(
                btns, text="📞 Llamar",
                font=("Helvetica", 10, "bold"),
                bg=COLOR_VERDE, fg="#FFFFFF", bd=0,
                padx=14, pady=7, cursor="hand2",
                activebackground="#27ae60", activeforeground="#FFFFFF",
                command=lambda: webbrowser.open(f"tel:{tel}"),
            ).pack(side="left", padx=5)

        tk.Frame(self, bg=COLOR_BORDE, height=1).pack(fill="x")
        tk.Button(self, text="Cerrar", font=("Helvetica", 10),
                  bg=BG_HEADER, fg=COLOR_GRIS, bd=0, pady=9, cursor="hand2",
                  activebackground=BG_HEADER, activeforeground=COLOR_TEXTO,
                  command=self.destroy).pack(fill="x")

    def _fila(self, parent, icono, texto):
        if not texto:
            return
        f = tk.Frame(parent, bg=BG_PRINCIPAL)
        f.pack(fill="x", pady=3)
        tk.Label(f, text=icono, font=("Helvetica", 12),
                 bg=BG_PRINCIPAL, fg=COLOR_ACENTO, width=3).pack(side="left")
        tk.Label(f, text=texto, font=("Helvetica", 10),
                 bg=BG_PRINCIPAL, fg=COLOR_TEXTO,
                 anchor="w", wraplength=320, justify="left").pack(side="left", fill="x", expand=True)


# ── Pantalla principal del mapa ───────────────────────────────────────────────
class PantallaMapa(tk.Frame):
    """
    Frame embebible con mapa interactivo de Tuluá.
    Requiere: pip install tkintermapview

    Callbacks:
    on_volver : callable
    usuario   : dict | None
    """

    def __init__(self, parent, on_volver, usuario=None, **kwargs):
        super().__init__(parent, bg=BG_PRINCIPAL, **kwargs)
        self._on_volver    = on_volver
        self._usuario      = usuario
        self._restaurantes = _leer_restaurantes()
        self._marcadores   = []
        self._filtro_cat   = tk.StringVar(value="Todos")
        self._construir_ui()

    # ── UI ────────────────────────────────────────────────────────────────────

    def _construir_ui(self):
        self._construir_header()
        tk.Frame(self, bg=COLOR_BORDE, height=1).pack(fill="x")
        self._construir_filtros()
        self._construir_mapa()
        self._construir_footer()

    def _construir_header(self):
        header = tk.Frame(self, bg=BG_HEADER, pady=14)
        header.pack(fill="x")

        tk.Button(
            header, text="← Volver",
            font=("Helvetica", 10),
            bg=BG_HEADER, fg=COLOR_GRIS, bd=0, cursor="hand2",
            activebackground=BG_HEADER, activeforeground=COLOR_TEXTO,
            command=self._on_volver,
        ).pack(side="left", padx=16)

        tk.Label(
            header, text="🗺  Mapa de Restaurantes",
            font=("Georgia", 17, "bold"),
            bg=BG_HEADER, fg=COLOR_TEXTO,
        ).pack(side="left", expand=True)

        tk.Label(header, bg=BG_HEADER, width=10).pack(side="right", padx=16)

    def _construir_filtros(self):
        """Barra de filtro por categoría."""
        barra = tk.Frame(self, bg=BG_CARD, pady=8)
        barra.pack(fill="x")

        tk.Label(
            barra, text="Filtrar:",
            font=("Helvetica", 10),
            bg=BG_CARD, fg=COLOR_GRIS,
        ).pack(side="left", padx=(16, 8))

        categorias = ["Todos", "Almuerzos", "Comida Rápida", "Bebidas"]
        for cat in categorias:
            color = COLORES_CAT.get(cat, COLOR_ACENTO) if cat != "Todos" else COLOR_GRIS
            btn = tk.Button(
                barra, text=cat,
                font=("Helvetica", 9, "bold"),
                bg=color, fg="#FFFFFF",
                bd=0, padx=10, pady=4,
                cursor="hand2",
                activebackground=color,
                activeforeground="#FFFFFF",
                command=lambda c=cat: self._aplicar_filtro(c),
            )
            btn.pack(side="left", padx=4)

        # Contador
        self._lbl_contador = tk.Label(
            barra,
            text=f"{len(self._restaurantes)} lugares",
            font=("Helvetica", 9),
            bg=BG_CARD, fg=COLOR_GRIS,
        )
        self._lbl_contador.pack(side="right", padx=16)

    def _construir_mapa(self):
        if not MAPA_DISPONIBLE:
            tk.Label(
                self,
                text="⚠️  Instala tkintermapview:\npip install tkintermapview",
                font=("Helvetica", 13),
                bg=BG_PRINCIPAL, fg=COLOR_ACENTO,
                pady=60, justify="center",
            ).pack(expand=True)
            return

        self._mapa = tkintermapview.TkinterMapView(
            self, corner_radius=0
        )
        self._mapa.pack(fill="both", expand=True)

        # Centrar en Tuluá zoom 14
        self._mapa.set_position(TULUA_LAT, TULUA_LON)
        self._mapa.set_zoom(14)

        self._colocar_marcadores(self._restaurantes)

    def _construir_footer(self):
        tk.Frame(self, bg=COLOR_BORDE, height=1).pack(fill="x")
        footer = tk.Frame(self, bg=BG_HEADER, pady=8)
        footer.pack(fill="x")
        tk.Label(
            footer, text="Menugo © 2025  •  Tuluá, Valle del Cauca",
            font=("Helvetica", 9), bg=BG_HEADER, fg=COLOR_GRIS,
        ).pack()

    # ── Marcadores ────────────────────────────────────────────────────────────

    def _colocar_marcadores(self, restaurantes: list):
        if not MAPA_DISPONIBLE:
            return

        # Limpiar anteriores
        for m in self._marcadores:
            m.delete()
        self._marcadores.clear()

        for r in restaurantes:
            rid  = r.get("id", "")
            coords = COORDENADAS.get(rid, (TULUA_LAT, TULUA_LON))
            emoji  = r.get("imagen_emoji", "🍽️")
            nombre = r.get("nombre", "Restaurante")

            marcador = self._mapa.set_marker(
                coords[0], coords[1],
                text=f"{emoji} {nombre}",
                command=lambda m, rest=r: self._on_marcador_click(rest),
            )
            self._marcadores.append(marcador)

        # Actualizar contador
        self._lbl_contador.configure(
            text=f"{len(restaurantes)} lugar{'es' if len(restaurantes) != 1 else ''}"
        )

    def _on_marcador_click(self, restaurante: dict):
        PopupRestaurante(self.winfo_toplevel(), restaurante)

    def _aplicar_filtro(self, categoria: str):
        if categoria == "Todos":
            filtrados = self._restaurantes
        else:
            filtrados = [
                r for r in self._restaurantes
                if r.get("categoria") == categoria
            ]
        self._colocar_marcadores(filtrados)