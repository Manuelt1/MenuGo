"""
ui/main.py
Pantalla principal de Menugo.
Muestra las categorías de comida disponibles como tarjetas interactivas.
Al hacer clic en una categoría se navega a la pantalla de productos.
"""

import tkinter as tk
from utils.file_handler import leer_categorias, leer_restaurantes_por_categoria

# ──────────────────────────────────────────────
#  Paleta de colores (tema oscuro Menugo)
# ──────────────────────────────────────────────
BG_PRINCIPAL  = "#0F1923"
BG_HEADER     = "#111D2B"
BG_CARD       = "#1A2535"
BG_CARD_HOVER = "#1F2E42"
COLOR_ACENTO  = "#FF6B35"
COLOR_TEXTO   = "#F0EDE8"
COLOR_GRIS    = "#8A9BB0"
COLOR_BORDE   = "#2A3D55"

# Emoji y color de acento por categoría
METADATA_CATEGORIA = {
    "Almuerzos":    {"emoji": "🍲", "color": "#E8593C", "desc": "Platos del día y caseros"},
    "Comida Rápida":{"emoji": "🍔", "color": "#F0A500", "desc": "Rápido, rico y sin complicaciones"},
    "Bebidas":      {"emoji": "🥤", "color": "#2196A6", "desc": "Jugos, café y más"},
}
EMOJI_DEFAULT = "🍽️"
COLOR_DEFAULT = "#6C7A9C"
DESC_DEFAULT  = "Explora esta categoría"


class PantallaPrincipal(tk.Frame):
    """
    Frame de la pantalla principal con tarjetas de categorías.
    Recibe la ventana raíz y el usuario autenticado.
    Llama a on_categoria(categoria_str) cuando el usuario selecciona una.
    """

    def __init__(self, parent, usuario: dict, on_categoria=None):
        super().__init__(parent, bg=BG_PRINCIPAL)
        self.usuario = usuario
        self.on_categoria = on_categoria
        self._tarjetas = []   # guardamos refs para efectos hover
        self._construir()

    # ──────────────────────────────────────────
    #  Construcción de la UI
    # ──────────────────────────────────────────

    def _construir(self):
        self._construir_header()
        self._construir_saludo()
        self._construir_grid_categorias()
        self._construir_footer()

    def _construir_header(self):
        header = tk.Frame(self, bg=BG_HEADER, height=64)
        header.pack(fill="x")
        header.pack_propagate(False)

        # Logo / nombre app
        tk.Label(
            header,
            text="🍽️  Menugo",
            font=("Georgia", 18, "bold"),
            bg=BG_HEADER, fg=COLOR_ACENTO,
        ).pack(side="left", padx=24, pady=14)

        # Nombre del usuario (derecha)
        tk.Label(
            header,
            text=f"👤  {self.usuario.get('nombre', '')}",
            font=("Helvetica", 11),
            bg=BG_HEADER, fg=COLOR_GRIS,
        ).pack(side="right", padx=24)

    def _construir_saludo(self):
        saludo_frame = tk.Frame(self, bg=BG_PRINCIPAL)
        saludo_frame.pack(fill="x", padx=32, pady=(28, 4))

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

        # Separador
        sep = tk.Frame(self, bg=COLOR_BORDE, height=1)
        sep.pack(fill="x", padx=32, pady=20)

    def _construir_grid_categorias(self):
        categorias = leer_categorias()   # ["Almuerzos", "Bebidas", "Comida Rápida"]

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

        # Configurar columnas (2 columnas)
        contenedor.columnconfigure(0, weight=1)
        contenedor.columnconfigure(1, weight=1)

        for i, cat in enumerate(categorias):
            fila = i // 2
            col  = i % 2
            self._crear_tarjeta(contenedor, cat, fila, col)

    def _crear_tarjeta(self, parent, categoria: str, fila: int, col: int):
        meta  = METADATA_CATEGORIA.get(categoria, {})
        emoji = meta.get("emoji", EMOJI_DEFAULT)
        color = meta.get("color", COLOR_DEFAULT)
        desc  = meta.get("desc",  DESC_DEFAULT)

        # Contar restaurantes de esta categoría
        cantidad = len(leer_restaurantes_por_categoria(categoria))
        plural   = "restaurante" if cantidad == 1 else "restaurantes"

        # Frame exterior (borde de color al hover)
        outer = tk.Frame(parent, bg=BG_PRINCIPAL, padx=6, pady=6)
        outer.grid(row=fila, column=col, sticky="nsew", padx=8, pady=8)
        parent.rowconfigure(fila, weight=1)

        # Frame de la tarjeta
        card = tk.Frame(outer, bg=BG_CARD, cursor="hand2")
        card.pack(fill="both", expand=True)

        # Franja superior de color
        franja = tk.Frame(card, bg=color, height=5)
        franja.pack(fill="x")

        # Cuerpo de la tarjeta
        cuerpo = tk.Frame(card, bg=BG_CARD, padx=20, pady=20)
        cuerpo.pack(fill="both", expand=True)

        # Emoji grande
        lbl_emoji = tk.Label(
            cuerpo,
            text=emoji,
            font=("Helvetica", 38),
            bg=BG_CARD,
        )
        lbl_emoji.pack(anchor="w")

        # Nombre de categoría
        lbl_cat = tk.Label(
            cuerpo,
            text=categoria,
            font=("Georgia", 15, "bold"),
            bg=BG_CARD, fg=COLOR_TEXTO,
            anchor="w",
        )
        lbl_cat.pack(fill="x", pady=(8, 2))

        # Descripción
        lbl_desc = tk.Label(
            cuerpo,
            text=desc,
            font=("Helvetica", 10),
            bg=BG_CARD, fg=COLOR_GRIS,
            anchor="w",
        )
        lbl_desc.pack(fill="x")

        # Contador de restaurantes
        lbl_count = tk.Label(
            cuerpo,
            text=f"📍 {cantidad} {plural}",
            font=("Helvetica", 10, "bold"),
            bg=BG_CARD, fg=color,
            anchor="w",
        )
        lbl_count.pack(fill="x", pady=(12, 0))

        # ── Efectos hover ──────────────────────
        todos = [card, cuerpo, franja, lbl_emoji, lbl_cat, lbl_desc, lbl_count]

        def on_enter(e, widgets=todos, c=BG_CARD_HOVER):
            for w in widgets:
                try:
                    w.configure(bg=c)
                except Exception:
                    pass

        def on_leave(e, widgets=todos, c=BG_CARD):
            for w in widgets:
                try:
                    w.configure(bg=c)
                    # franja mantiene su color
                except Exception:
                    pass
            franja.configure(bg=color)

        def on_click(e, cat=categoria):
            if self.on_categoria:
                self.on_categoria(cat)

        for widget in todos:
            widget.bind("<Enter>", on_enter)
            widget.bind("<Leave>", on_leave)
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


# ──────────────────────────────────────────────
#  Prueba independiente (python ui/main.py)
# ──────────────────────────────────────────────
if __name__ == "__main__":
    from ui.productos import abrir_productos   # importación diferida para pruebas

    usuario_prueba = {"nombre": "Ana García", "correo": "ana@test.com"}

    root = tk.Tk()
    root.title("Menugo")
    root.geometry("620x560")
    root.configure(bg=BG_PRINCIPAL)
    root.resizable(False, False)

    def al_seleccionar_categoria(cat):
        # Destruye el frame actual y abre productos
        for w in root.winfo_children():
            w.destroy()
        abrir_productos(cat, usuario_prueba, on_volver=lambda: _reabrir_main())

    def _reabrir_main():
        for w in root.winfo_children():
            w.destroy()
        pantalla = PantallaPrincipal(root, usuario_prueba, on_categoria=al_seleccionar_categoria)
        pantalla.pack(fill="both", expand=True)

    pantalla = PantallaPrincipal(root, usuario_prueba, on_categoria=al_seleccionar_categoria)
    pantalla.pack(fill="both", expand=True)
    root.mainloop()