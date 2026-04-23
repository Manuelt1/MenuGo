"""
ui/main.py
Pantalla principal de Menugo.
Sprint 2: añadidos botones ⭐ Menú del día y 🔍 Buscar en el header.
"""

import tkinter as tk
from utils.file_handler import leer_categorias, leer_restaurantes_por_categoria

BG_PRINCIPAL  = "#0F1923"
BG_HEADER     = "#111D2B"
BG_CARD       = "#1A2535"
BG_CARD_HOVER = "#1F2E42"
COLOR_ACENTO  = "#FF6B35"
COLOR_TEXTO   = "#F0EDE8"
COLOR_GRIS    = "#8A9BB0"
COLOR_BORDE   = "#2A3D55"

METADATA_CATEGORIA = {
    "Almuerzos":     {"emoji": "", "color": "#E8593C", "desc": "Platos del día y caseros"},
    "Comida Rápida": {"emoji": "", "color": "#F0A500", "desc": "Rápido, rico y sin complicaciones"},
    "Bebidas":       {"emoji": "", "color": "#2196A6", "desc": "Jugos, café y más"},
}
EMOJI_DEFAULT = ""
COLOR_DEFAULT = "#6C7A9C"
DESC_DEFAULT  = "Explora esta categoría"


class PantallaPrincipal(tk.Frame):
    """
    Frame principal con tarjetas de categorías.
    Callbacks:
      on_categoria(str)  → navegar a productos de esa categoría
      on_favoritos()     → navegar a favoritos
      on_menu_dia()      → navegar al menú del día   [Sprint 2]
      on_filtros()       → navegar a búsqueda        [Sprint 2]
    """

    def __init__(
        self,
        parent,
        usuario: dict,
        on_categoria=None,
        on_favoritos=None,
        on_menu_dia=None,
        on_filtros=None,
    ):
        super().__init__(parent, bg=BG_PRINCIPAL)
        self.usuario      = usuario
        self.on_categoria = on_categoria
        self.on_favoritos = on_favoritos
        self.on_menu_dia  = on_menu_dia or (lambda: None)
        self.on_filtros   = on_filtros  or (lambda: None)
        self._tarjetas    = []
        self._construir()

    def _construir(self):
        self._construir_header()
        self._construir_saludo()
        self._construir_grid_categorias()
        self._construir_footer()

    def _construir_header(self):
        header = tk.Frame(self, bg=BG_HEADER, height=64)
        header.pack(fill="x")
        header.pack_propagate(False)

        # Logo
        tk.Label(
            header,
            text="🍽️  Menugo",
            font=("Georgia", 18, "bold"),
            bg=BG_HEADER, fg=COLOR_ACENTO,
        ).pack(side="left", padx=24, pady=14)

        # Nombre usuario (derecha)
        tk.Label(
            header,
            text=f"👤  {self.usuario.get('nombre', '')}",
            font=("Helvetica", 10),
            bg=BG_HEADER, fg=COLOR_GRIS,
        ).pack(side="right", padx=16)

        # Botón Favoritos
        tk.Button(
            header,
            text=" Favoritos",
            font=("Helvetica", 9, "bold"),
            bg=BG_CARD, fg=COLOR_TEXTO,
            activebackground=BG_CARD_HOVER,
            activeforeground=COLOR_TEXTO,
            relief="flat", cursor="hand2",
            padx=10, pady=5,
            command=lambda: self.on_favoritos() if self.on_favoritos else None,
        ).pack(side="right", padx=4)

        # Botón Menú del día  ── Sprint 2
        tk.Button(
            header,
            text=" Menú del día",
            font=("Helvetica", 9, "bold"),
            bg=COLOR_ACENTO, fg="#FFFFFF",
            activebackground="#E55A26",
            activeforeground="#FFFFFF",
            relief="flat", cursor="hand2",
            padx=10, pady=5,
            command=self.on_menu_dia,
        ).pack(side="right", padx=4)

        # Botón Buscar  ── Sprint 2
        tk.Button(
            header,
            text=" Buscar",
            font=("Helvetica", 9, "bold"),
            bg=BG_CARD, fg=COLOR_TEXTO,
            activebackground=BG_CARD_HOVER,
            activeforeground=COLOR_TEXTO,
            relief="flat", cursor="hand2",
            padx=10, pady=5,
            command=self.on_filtros,
        ).pack(side="right", padx=4)

    def _construir_saludo(self):
        saludo_frame = tk.Frame(self, bg=BG_PRINCIPAL)
        saludo_frame.pack(fill="x", padx=32, pady=(24, 4))

        tk.Label(
            saludo_frame,
            text="¿Qué quieres comer hoy?",
            font=("Georgia", 20, "bold"),
            bg=BG_PRINCIPAL, fg=COLOR_TEXTO,
            anchor="w",
        ).pack(fill="x")

        tk.Label(
            saludo_frame,
            text="Elige una categoría para explorar el menú",
            font=("Helvetica", 12),
            bg=BG_PRINCIPAL, fg=COLOR_GRIS,
            anchor="w",
        ).pack(fill="x", pady=(4, 0))

        tk.Frame(self, bg=COLOR_BORDE, height=1).pack(fill="x", padx=32, pady=16)

    def _construir_grid_categorias(self):
        categorias = leer_categorias()

        if not categorias:
            tk.Label(
                self,
                text="No hay categorías disponibles.",
                font=("Helvetica", 13),
                bg=BG_PRINCIPAL, fg=COLOR_GRIS,
            ).pack(pady=60)
            return

        contenedor = tk.Frame(self, bg=BG_PRINCIPAL)
        contenedor.pack(fill="both", expand=True, padx=32)

        contenedor.columnconfigure(0, weight=1)
        contenedor.columnconfigure(1, weight=1)

        for i, cat in enumerate(categorias):
            self._crear_tarjeta(contenedor, cat, i // 2, i % 2)

    def _crear_tarjeta(self, parent, categoria: str, fila: int, col: int):
        meta  = METADATA_CATEGORIA.get(categoria, {})
        emoji = meta.get("emoji", EMOJI_DEFAULT)
        color = meta.get("color", COLOR_DEFAULT)
        desc  = meta.get("desc",  DESC_DEFAULT)

        cantidad = len(leer_restaurantes_por_categoria(categoria))
        plural   = "restaurante" if cantidad == 1 else "restaurantes"

        outer = tk.Frame(parent, bg=BG_PRINCIPAL, padx=6, pady=6)
        outer.grid(row=fila, column=col, sticky="nsew", padx=8, pady=8)
        parent.rowconfigure(fila, weight=1)

        card = tk.Frame(outer, bg=BG_CARD, cursor="hand2")
        card.pack(fill="both", expand=True)

        franja = tk.Frame(card, bg=color, height=5)
        franja.pack(fill="x")

        cuerpo = tk.Frame(card, bg=BG_CARD, padx=20, pady=20)
        cuerpo.pack(fill="both", expand=True)

        lbl_emoji = tk.Label(cuerpo, text=emoji, font=("Helvetica", 38), bg=BG_CARD)
        lbl_emoji.pack(anchor="w")

        lbl_cat = tk.Label(
            cuerpo, text=categoria,
            font=("Georgia", 15, "bold"),
            bg=BG_CARD, fg=COLOR_TEXTO, anchor="w",
        )
        lbl_cat.pack(fill="x", pady=(8, 2))

        lbl_desc = tk.Label(
            cuerpo, text=desc,
            font=("Helvetica", 10),
            bg=BG_CARD, fg=COLOR_GRIS, anchor="w",
        )
        lbl_desc.pack(fill="x")

        lbl_count = tk.Label(
            cuerpo, text=f" {cantidad} {plural}",
            font=("Helvetica", 10, "bold"),
            bg=BG_CARD, fg=color, anchor="w",
        )
        lbl_count.pack(fill="x", pady=(12, 0))

        todos = [card, cuerpo, franja, lbl_emoji, lbl_cat, lbl_desc, lbl_count]

        def on_enter(e, widgets=todos):
            for w in widgets:
                try: w.configure(bg=BG_CARD_HOVER)
                except Exception: pass

        def on_leave(e, widgets=todos):
            for w in widgets:
                try: w.configure(bg=BG_CARD)
                except Exception: pass
            franja.configure(bg=color)

        def on_click(e, cat=categoria):
            if self.on_categoria:
                self.on_categoria(cat)

        for widget in todos:
            widget.bind("<Enter>",    on_enter)
            widget.bind("<Leave>",    on_leave)
            widget.bind("<Button-1>", on_click)

        self._tarjetas.append(card)

    def _construir_footer(self):
        footer = tk.Frame(self, bg=BG_HEADER, height=36)
        footer.pack(fill="x", side="bottom")
        footer.pack_propagate(False)
        tk.Label(
            footer,
            text="Menugo © 2025  —  Tu guía de sabores",
            font=("Helvetica", 9),
            bg=BG_HEADER, fg=COLOR_GRIS,
        ).pack(expand=True)