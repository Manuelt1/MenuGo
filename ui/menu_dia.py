import tkinter as tk
from utils.file_handler import leer_menu_del_dia

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


class PantallaMenuDia(tk.Frame):
    def __init__(self, parent, on_volver, usuario=None, **kwargs):
        super().__init__(parent, bg=BG_PRINCIPAL, **kwargs)
        self._on_volver = on_volver
        self._usuario   = usuario
        self._construir_ui()

    def _construir_ui(self):
        self._construir_header()
        tk.Frame(self, bg=COLOR_BORDE, height=1).pack(fill="x")
        self._construir_area_scroll()
        self._cargar_productos()
        self._construir_footer()

    def _construir_header(self):
        header = tk.Frame(self, bg=BG_HEADER, pady=14)
        header.pack(fill="x")
        tk.Button(
            header, text="← Volver", font=("Helvetica", 10),
            bg=BG_HEADER, fg=COLOR_GRIS, bd=0, cursor="hand2",
            activebackground=BG_HEADER, activeforeground=COLOR_TEXTO,
            command=self._on_volver,
        ).pack(side="left", padx=16)
        tk.Label(
            header, text="  Menú del Día",
            font=("Georgia", 18, "bold"),
            bg=BG_HEADER, fg=COLOR_TEXTO,
        ).pack(side="left", expand=True)
        tk.Label(header, bg=BG_HEADER, width=10).pack(side="right", padx=16)

    def _construir_area_scroll(self):
        contenedor = tk.Frame(self, bg=BG_PRINCIPAL)
        contenedor.pack(fill="both", expand=True)
        self._canvas = tk.Canvas(contenedor, bg=BG_PRINCIPAL, highlightthickness=0)
        scrollbar = tk.Scrollbar(contenedor, orient="vertical", command=self._canvas.yview)
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
            footer, text="Menugo © 2025",
            font=("Helvetica", 9), bg=BG_HEADER, fg=COLOR_GRIS,
        ).pack()

    def _cargar_productos(self):
        for w in self._frame_lista.winfo_children():
            w.destroy()
        productos = leer_menu_del_dia()
        if not productos:
            tk.Label(
                self._frame_lista,
                text="No hay productos en el menú del día.",
                font=("Helvetica", 13), bg=BG_PRINCIPAL,
                fg=COLOR_GRIS, pady=40,
            ).pack()
            return
        n = len(productos)
        tk.Label(
            self._frame_lista,
            text=f"{n} producto{'s' if n != 1 else ''} disponible{'s' if n != 1 else ''} hoy",
            font=("Helvetica", 10), bg=BG_PRINCIPAL,
            fg=COLOR_GRIS, pady=10,
        ).pack(anchor="w", padx=20)
        for p in productos:
            self._crear_tarjeta_producto(p)

    def _crear_tarjeta_producto(self, producto: dict):
        categoria = producto.get("categoria", "")
        color_cat = COLORES_CAT.get(categoria, COLOR_CAT_DEFAULT)
        wrapper = tk.Frame(self._frame_lista, bg=BG_PRINCIPAL)
        wrapper.pack(fill="x", padx=20, pady=6)
        card = tk.Frame(wrapper, bg=BG_CARD, cursor="hand2")
        card.pack(fill="x")
        tk.Frame(card, bg=color_cat, height=4).pack(fill="x")
        cuerpo = tk.Frame(card, bg=BG_CARD, padx=16, pady=10)
        cuerpo.pack(fill="x")
        fila_top = tk.Frame(cuerpo, bg=BG_CARD)
        fila_top.pack(fill="x")
        tk.Label(
            fila_top, text=producto.get("nombre", "—"),
            font=("Georgia", 13, "bold"),
            bg=BG_CARD, fg=COLOR_TEXTO, anchor="w",
        ).pack(side="left")
        tk.Label(
            fila_top, text=f"${producto.get('precio', 0):,.0f}",
            font=("Helvetica", 12, "bold"),
            bg=BG_CARD, fg=COLOR_ACENTO, anchor="e",
        ).pack(side="right")
        desc = producto.get("descripcion", "")
        if desc:
            tk.Label(
                cuerpo, text=desc, font=("Helvetica", 10),
                bg=BG_CARD, fg=COLOR_GRIS, anchor="w",
                wraplength=480, justify="left",
            ).pack(fill="x", pady=(4, 0))
        fila_bot = tk.Frame(cuerpo, bg=BG_CARD)
        fila_bot.pack(fill="x", pady=(6, 0))
        rest = producto.get("restaurante", "")
        if rest:
            tk.Label(
                fila_bot, text=f"🍽  {rest}",
                font=("Helvetica", 9), bg=BG_CARD, fg=COLOR_GRIS,
            ).pack(side="left")
        if categoria:
            tk.Label(
                fila_bot, text=categoria,
                font=("Helvetica", 8, "bold"),
                bg=color_cat, fg="#FFFFFF", padx=6, pady=2,
            ).pack(side="right")
        tk.Frame(self._frame_lista, bg=COLOR_BORDE, height=1).pack(fill="x", padx=20)
        for w in (card, cuerpo, fila_top, fila_bot):
            w.bind("<Enter>", lambda e, c=card: self._on_hover_enter(c))
            w.bind("<Leave>", lambda e, c=card: self._on_hover_leave(c))

    def _on_hover_enter(self, card):
        card.configure(bg=BG_CARD_HOVER)
        for c in card.winfo_children():
            try: c.configure(bg=BG_CARD_HOVER)
            except tk.TclError: pass

    def _on_hover_leave(self, card):
        card.configure(bg=BG_CARD)
        for c in card.winfo_children():
            try: c.configure(bg=BG_CARD)
            except tk.TclError: pass

    def _on_frame_configure(self, e):
        self._canvas.configure(scrollregion=self._canvas.bbox("all"))

    def _on_canvas_configure(self, e):
        self._canvas.itemconfig(self._canvas_window, width=e.width)

    def _on_mousewheel(self, e):
        if e.num == 4:
            self._canvas.yview_scroll(-1, "units")
        elif e.num == 5:
            self._canvas.yview_scroll(1, "units")
        else:
            self._canvas.yview_scroll(int(-1 * (e.delta / 120)), "units")