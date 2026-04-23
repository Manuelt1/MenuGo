"""
ui/filtros.py  ─  feature/filtros
Pantalla de búsqueda y filtrado de productos.
Usa buscar_productos() de file_handler y reutiliza el estilo de tarjetas
de ui/productos.py mediante _crear_tarjeta_producto local.
"""

import tkinter as tk
from tkinter import ttk
from utils.file_handler import buscar_productos, leer_categorias

# ── Paleta global ──────────────────────────────────────────────────────────────
BG_PRINCIPAL  = "#0F1923"
BG_HEADER     = "#111D2B"
BG_CARD       = "#1A2535"
BG_CARD_HOVER = "#1F2E42"
COLOR_ACENTO  = "#FF6B35"
COLOR_TEXTO   = "#F0EDE8"
COLOR_GRIS    = "#8A9BB0"
COLOR_BORDE   = "#2A3D55"

COLORES_CAT = {
    "Almuerzos":     "#E8593C",
    "Comida Rápida": "#F0A500",
    "Bebidas":       "#2196A6",
}
COLOR_CAT_DEFAULT = COLOR_ACENTO

PRECIO_MIN     = 0
PRECIO_MAX     = 50_000
PRECIO_PASO    = 500
PRECIO_DEFAULT = 50_000          # Sin límite activo por defecto


class PantallaFiltros(tk.Frame):
    """
    Frame embebible con búsqueda reactiva de productos.

    Callbacks esperados
    ───────────────────
    on_volver : callable  → regresa a PantallaPrincipal
    usuario   : dict      → usuario activo (puede ser None)
    """

    def __init__(self, parent, on_volver, usuario=None, **kwargs):
        super().__init__(parent, bg=BG_PRINCIPAL, **kwargs)
        self._on_volver = on_volver
        self._usuario   = usuario

        # Variables de filtro
        self._var_texto    = tk.StringVar()
        self._var_precio   = tk.IntVar(value=PRECIO_DEFAULT)
        self._var_categoria = tk.StringVar(value="Todas")

        # Debounce: id del after pendiente
        self._after_id = None

        self._construir_ui()
        self._buscar()   # Carga inicial con filtros vacíos

    # ── Construcción ──────────────────────────────────────────────────────────

    def _construir_ui(self):
        self._construir_header()
        tk.Frame(self, bg=COLOR_BORDE, height=1).pack(fill="x")
        self._construir_panel_filtros()
        tk.Frame(self, bg=COLOR_BORDE, height=1).pack(fill="x")
        self._construir_area_scroll()
        self._construir_footer()

    def _construir_header(self):
        header = tk.Frame(self, bg=BG_HEADER, pady=14)
        header.pack(fill="x")

        btn_volver = tk.Button(
            header,
            text="← Volver",
            font=("Helvetica", 10),
            bg=BG_HEADER,
            fg=COLOR_GRIS,
            bd=0,
            cursor="hand2",
            activebackground=BG_HEADER,
            activeforeground=COLOR_TEXTO,
            command=self._on_volver,
        )
        btn_volver.pack(side="left", padx=16)

        titulo = tk.Label(
            header,
            text="🔍  Buscar Productos",
            font=("Georgia", 18, "bold"),
            bg=BG_HEADER,
            fg=COLOR_TEXTO,
        )
        titulo.pack(side="left", expand=True)

        tk.Label(header, bg=BG_HEADER, width=10).pack(side="right", padx=16)

    def _construir_panel_filtros(self):
        """Panel con los tres controles de filtro."""
        panel = tk.Frame(self, bg=BG_HEADER, padx=20, pady=14)
        panel.pack(fill="x")

        # ── Fila 1: texto libre ──────────────────────────────────────────────
        fila1 = tk.Frame(panel, bg=BG_HEADER)
        fila1.pack(fill="x", pady=(0, 10))

        tk.Label(
            fila1,
            text="Buscar:",
            font=("Helvetica", 10, "bold"),
            bg=BG_HEADER,
            fg=COLOR_GRIS,
            width=10,
            anchor="w",
        ).pack(side="left")

        entry_style = {
            "font": ("Helvetica", 11),
            "bg": BG_CARD,
            "fg": COLOR_TEXTO,
            "insertbackground": COLOR_TEXTO,
            "relief": "flat",
            "bd": 0,
            "highlightthickness": 1,
            "highlightbackground": COLOR_BORDE,
            "highlightcolor": COLOR_ACENTO,
        }
        self._entry_texto = tk.Entry(
            fila1, textvariable=self._var_texto, **entry_style
        )
        self._entry_texto.pack(side="left", fill="x", expand=True, ipady=6)
        self._var_texto.trace_add("write", self._on_filtro_cambio)

        # ── Fila 2: categoría + precio ───────────────────────────────────────
        fila2 = tk.Frame(panel, bg=BG_HEADER)
        fila2.pack(fill="x")

        # Categoría
        tk.Label(
            fila2,
            text="Categoría:",
            font=("Helvetica", 10, "bold"),
            bg=BG_HEADER,
            fg=COLOR_GRIS,
            width=10,
            anchor="w",
        ).pack(side="left")

        categorias = ["Todas"] + leer_categorias()
        style = ttk.Style()
        style.theme_use("clam")
        style.configure(
            "Menugo.TCombobox",
            fieldbackground=BG_CARD,
            background=BG_CARD,
            foreground=COLOR_TEXTO,
            selectbackground=BG_CARD_HOVER,
            selectforeground=COLOR_TEXTO,
            arrowcolor=COLOR_ACENTO,
            bordercolor=COLOR_BORDE,
        )
        self._combo = ttk.Combobox(
            fila2,
            textvariable=self._var_categoria,
            values=categorias,
            state="readonly",
            style="Menugo.TCombobox",
            font=("Helvetica", 10),
            width=16,
        )
        self._combo.pack(side="left", padx=(0, 24), ipady=4)
        self._combo.bind("<<ComboboxSelected>>", self._on_filtro_cambio)

        # Precio máximo
        tk.Label(
            fila2,
            text="Precio máx:",
            font=("Helvetica", 10, "bold"),
            bg=BG_HEADER,
            fg=COLOR_GRIS,
        ).pack(side="left")

        self._lbl_precio = tk.Label(
            fila2,
            text=self._formato_precio(PRECIO_DEFAULT),
            font=("Helvetica", 10, "bold"),
            bg=BG_HEADER,
            fg=COLOR_ACENTO,
            width=9,
            anchor="e",
        )
        self._lbl_precio.pack(side="right", padx=(0, 8))

        self._scale = tk.Scale(
            fila2,
            variable=self._var_precio,
            from_=PRECIO_MIN,
            to=PRECIO_MAX,
            resolution=PRECIO_PASO,
            orient="horizontal",
            bg=BG_HEADER,
            fg=COLOR_TEXTO,
            troughcolor=BG_CARD,
            activebackground=COLOR_ACENTO,
            highlightthickness=0,
            showvalue=False,
            command=self._on_precio_cambio,
        )
        self._scale.pack(side="left", fill="x", expand=True, padx=(8, 0))

    def _construir_area_scroll(self):
        contenedor = tk.Frame(self, bg=BG_PRINCIPAL)
        contenedor.pack(fill="both", expand=True)

        self._canvas = tk.Canvas(
            contenedor, bg=BG_PRINCIPAL, highlightthickness=0
        )
        scrollbar = tk.Scrollbar(
            contenedor, orient="vertical", command=self._canvas.yview
        )
        self._canvas.configure(yscrollcommand=scrollbar.set)

        scrollbar.pack(side="right", fill="y")
        self._canvas.pack(side="left", fill="both", expand=True)

        self._frame_lista = tk.Frame(self._canvas, bg=BG_PRINCIPAL)
        self._canvas_window = self._canvas.create_window(
            (0, 0), window=self._frame_lista, anchor="nw"
        )

        self._frame_lista.bind("<Configure>", self._on_frame_configure)
        self._canvas.bind("<Configure>", self._on_canvas_configure)

        self._canvas.bind_all("<MouseWheel>", self._on_mousewheel)
        self._canvas.bind_all("<Button-4>",   self._on_mousewheel)
        self._canvas.bind_all("<Button-5>",   self._on_mousewheel)

    def _construir_footer(self):
        tk.Frame(self, bg=COLOR_BORDE, height=1).pack(fill="x")
        footer = tk.Frame(self, bg=BG_HEADER, pady=8)
        footer.pack(fill="x")
        tk.Label(
            footer,
            text="Menugo © 2025",
            font=("Helvetica", 9),
            bg=BG_HEADER,
            fg=COLOR_GRIS,
        ).pack()

    # ── Lógica de búsqueda ────────────────────────────────────────────────────

    def _on_filtro_cambio(self, *_):
        """Lanza la búsqueda con un pequeño debounce (300 ms)."""
        if self._after_id is not None:
            self.after_cancel(self._after_id)
        self._after_id = self.after(300, self._buscar)

    def _on_precio_cambio(self, valor):
        """Actualiza la etiqueta del precio y dispara búsqueda."""
        self._lbl_precio.configure(text=self._formato_precio(int(float(valor))))
        self._on_filtro_cambio()

    def _buscar(self):
        """Llama a buscar_productos con los filtros actuales y refresca."""
        termino    = self._var_texto.get().strip()
        cat_raw    = self._var_categoria.get()
        categoria  = None if cat_raw == "Todas" else cat_raw
        precio_max = self._var_precio.get()
        # Si el scale está en su máximo lo tratamos como "sin límite"
        pm = None if precio_max >= PRECIO_MAX else precio_max

        productos = buscar_productos(termino, categoria=categoria, precio_max=pm)
        self._refrescar_lista(productos, termino)

    def _refrescar_lista(self, productos: list, termino: str = ""):
        """Destruye los widgets anteriores y renderiza los nuevos."""
        for widget in self._frame_lista.winfo_children():
            widget.destroy()

        # Contador de resultados
        n = len(productos)
        sufijo = f'para "{termino}"' if termino else "con los filtros aplicados"
        msg = (
            f"{n} resultado{'s' if n != 1 else ''} {sufijo}"
            if n > 0
            else f"Sin resultados {sufijo}"
        )
        tk.Label(
            self._frame_lista,
            text=msg,
            font=("Helvetica", 10),
            bg=BG_PRINCIPAL,
            fg=COLOR_GRIS,
            pady=10,
        ).pack(anchor="w", padx=20)

        for producto in productos:
            self._crear_tarjeta_producto(producto, termino)

    def _crear_tarjeta_producto(self, producto: dict, termino: str = ""):
        """Tarjeta de resultado idéntica en estilo a la de ui/productos.py."""
        categoria = producto.get("categoria", "")
        color_cat = COLORES_CAT.get(categoria, COLOR_CAT_DEFAULT)

        wrapper = tk.Frame(self._frame_lista, bg=BG_PRINCIPAL)
        wrapper.pack(fill="x", padx=20, pady=6)

        card = tk.Frame(wrapper, bg=BG_CARD, cursor="hand2")
        card.pack(fill="x")

        # Franja de 4px
        tk.Frame(card, bg=color_cat, height=4).pack(fill="x")

        cuerpo = tk.Frame(card, bg=BG_CARD, padx=16, pady=10)
        cuerpo.pack(fill="x")

        fila_top = tk.Frame(cuerpo, bg=BG_CARD)
        fila_top.pack(fill="x")

        nombre = producto.get("nombre", "—")
        tk.Label(
            fila_top,
            text=nombre,
            font=("Georgia", 13, "bold"),
            bg=BG_CARD,
            fg=COLOR_TEXTO,
            anchor="w",
        ).pack(side="left")

        precio = producto.get("precio", 0)
        tk.Label(
            fila_top,
            text=f"${precio:,.0f}",
            font=("Helvetica", 12, "bold"),
            bg=BG_CARD,
            fg=COLOR_ACENTO,
            anchor="e",
        ).pack(side="right")

        descripcion = producto.get("descripcion", "")
        if descripcion:
            tk.Label(
                cuerpo,
                text=descripcion,
                font=("Helvetica", 10),
                bg=BG_CARD,
                fg=COLOR_GRIS,
                anchor="w",
                wraplength=480,
                justify="left",
            ).pack(fill="x", pady=(4, 0))

        fila_bot = tk.Frame(cuerpo, bg=BG_CARD)
        fila_bot.pack(fill="x", pady=(6, 0))

        restaurante = producto.get("restaurante", "")
        if restaurante:
            tk.Label(
                fila_bot,
                text=f"🍽  {restaurante}",
                font=("Helvetica", 9),
                bg=BG_CARD,
                fg=COLOR_GRIS,
            ).pack(side="left")

        if categoria:
            tk.Label(
                fila_bot,
                text=categoria,
                font=("Helvetica", 8, "bold"),
                bg=color_cat,
                fg="#FFFFFF",
                padx=6,
                pady=2,
            ).pack(side="right")

        # Indicador menú del día
        if producto.get("menu_del_dia"):
            tk.Label(
                fila_bot,
                text="⭐ Menú del día",
                font=("Helvetica", 8),
                bg=BG_CARD,
                fg="#FFD700",
            ).pack(side="left", padx=(8, 0))

        tk.Frame(self._frame_lista, bg=COLOR_BORDE, height=1).pack(
            fill="x", padx=20
        )

        # Hover
        for widget in (card, cuerpo, fila_top, fila_bot):
            widget.bind("<Enter>", lambda e, c=card: self._on_hover_enter(c))
            widget.bind("<Leave>", lambda e, c=card: self._on_hover_leave(c))

    # ── Helpers ───────────────────────────────────────────────────────────────

    @staticmethod
    def _formato_precio(valor: int) -> str:
        if valor >= PRECIO_MAX:
            return "Sin límite"
        return f"${valor:,}"

    def _on_hover_enter(self, card):
        card.configure(bg=BG_CARD_HOVER)
        for child in card.winfo_children():
            try:
                child.configure(bg=BG_CARD_HOVER)
            except tk.TclError:
                pass

    def _on_hover_leave(self, card):
        card.configure(bg=BG_CARD)
        for child in card.winfo_children():
            try:
                child.configure(bg=BG_CARD)
            except tk.TclError:
                pass

    def _on_frame_configure(self, event):
        self._canvas.configure(scrollregion=self._canvas.bbox("all"))

    def _on_canvas_configure(self, event):
        self._canvas.itemconfig(self._canvas_window, width=event.width)

    def _on_mousewheel(self, event):
        if event.num == 4:
            self._canvas.yview_scroll(-1, "units")
        elif event.num == 5:
            self._canvas.yview_scroll(1, "units")
        else:
            self._canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")