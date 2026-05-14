"""
ui/restaurantes.py
Pantalla que lista todos los restaurantes.
Al hacer clic en un restaurante se abre un popup con su info completa.
"""

import tkinter as tk
import json
import os
import webbrowser

# ── Paleta (igual al resto del proyecto) ──────────────────────────────────────
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
COLOR_CAT_DEFAULT = COLOR_ACENTO


def _leer_restaurantes() -> list:
    """Lee restaurantes.json desde la carpeta datos/."""
    ruta = os.path.join(
        os.path.dirname(os.path.dirname(__file__)), "datos", "restaurantes.json"
    )
    try:
        with open(ruta, encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return []


class PopupRestaurante(tk.Toplevel):
    """Ventana emergente con la información completa de un restaurante."""

    def __init__(self, parent, restaurante: dict):
        super().__init__(parent)
        self.title(restaurante.get("nombre", "Restaurante"))
        self.configure(bg=BG_PRINCIPAL)
        self.resizable(False, False)

        # Centrar sobre la ventana padre
        self.transient(parent)
        self.grab_set()
        parent.update_idletasks()
        px = parent.winfo_rootx()
        py = parent.winfo_rooty()
        pw = parent.winfo_width()
        ph = parent.winfo_height()
        w, h = 420, 480
        x = px + (pw - w) // 2
        y = py + (ph - h) // 2
        self.geometry(f"{w}x{h}+{x}+{y}")

        self._restaurante = restaurante
        self._construir()

    def _construir(self):
        r = self._restaurante
        categoria  = r.get("categoria", "")
        color_cat  = COLORES_CAT.get(categoria, COLOR_CAT_DEFAULT)

        # ── Franja superior de color ──
        tk.Frame(self, bg=color_cat, height=5).pack(fill="x")

        # ── Cabecera con emoji + nombre ──
        cab = tk.Frame(self, bg=BG_HEADER, pady=18)
        cab.pack(fill="x")

        emoji = r.get("imagen_emoji", "🍽️")
        tk.Label(
            cab, text=emoji, font=("Helvetica", 36),
            bg=BG_HEADER, fg=COLOR_TEXTO,
        ).pack()
        tk.Label(
            cab, text=r.get("nombre", "—"),
            font=("Georgia", 16, "bold"),
            bg=BG_HEADER, fg=COLOR_TEXTO, wraplength=360,
        ).pack(pady=(6, 0))

        # Etiqueta categoría
        if categoria:
            tk.Label(
                cab, text=categoria,
                font=("Helvetica", 9, "bold"),
                bg=color_cat, fg="#FFFFFF", padx=8, pady=3,
            ).pack(pady=(6, 0))

        # ── Separador ──
        tk.Frame(self, bg=COLOR_BORDE, height=1).pack(fill="x")

        # ── Cuerpo ──
        cuerpo = tk.Frame(self, bg=BG_PRINCIPAL, padx=28, pady=20)
        cuerpo.pack(fill="both", expand=True)

        # Descripción
        desc = r.get("descripcion", "")
        if desc:
            tk.Label(
                cuerpo, text=desc,
                font=("Helvetica", 11),
                bg=BG_PRINCIPAL, fg=COLOR_TEXTO,
                wraplength=360, justify="center",
            ).pack(pady=(0, 16))

        # Datos de contacto
        self._fila_info(cuerpo, "📍", r.get("direccion", ""))
        self._fila_info(cuerpo, "📞", r.get("telefono", ""))
        self._fila_info(cuerpo, "🕐", r.get("horario", ""))

        # Cantidad de productos
        n_prod = len(r.get("productos", []))
        if n_prod:
            self._fila_info(cuerpo, "🍴", f"{n_prod} productos en carta")

        # Botones
        frame_btns = tk.Frame(cuerpo, bg=BG_PRINCIPAL)
        frame_btns.pack(pady=(20, 0))

        # Botón Ver en mapa (solo si tiene dirección)
        direccion = r.get("direccion", "")
        if direccion:
            query = direccion.replace(" ", "+")
            url_mapa = f"https://www.google.com/maps/search/?api=1&query={query}"
            btn_mapa = tk.Button(
                frame_btns,
                text="📍 Ver en mapa",
                font=("Helvetica", 10, "bold"),
                bg=COLOR_ACENTO, fg="#FFFFFF",
                bd=0, padx=16, pady=8,
                cursor="hand2",
                activebackground="#e05a25",
                activeforeground="#FFFFFF",
                command=lambda u=url_mapa: webbrowser.open(u),
            )
            btn_mapa.pack(side="left", padx=6)

        # Botón Llamar (solo si tiene teléfono)
        telefono = r.get("telefono", "").replace(" ", "")
        if telefono:
            tel_limpio = telefono.replace("-", "").replace("(", "").replace(")", "")
            btn_tel = tk.Button(
                frame_btns,
                text=f"📞 Llamar",
                font=("Helvetica", 10, "bold"),
                bg=COLOR_VERDE, fg="#FFFFFF",
                bd=0, padx=16, pady=8,
                cursor="hand2",
                activebackground="#27ae60",
                activeforeground="#FFFFFF",
                command=lambda t=tel_limpio: webbrowser.open(f"tel:{t}"),
            )
            btn_tel.pack(side="left", padx=6)

        # Botón cerrar
        tk.Frame(self, bg=COLOR_BORDE, height=1).pack(fill="x")
        tk.Button(
            self,
            text="Cerrar",
            font=("Helvetica", 10),
            bg=BG_HEADER, fg=COLOR_GRIS,
            bd=0, pady=10, cursor="hand2",
            activebackground=BG_HEADER,
            activeforeground=COLOR_TEXTO,
            command=self.destroy,
        ).pack(fill="x")

    def _fila_info(self, parent, icono: str, texto: str):
        if not texto:
            return
        fila = tk.Frame(parent, bg=BG_PRINCIPAL)
        fila.pack(fill="x", pady=4)
        tk.Label(
            fila, text=icono,
            font=("Helvetica", 12),
            bg=BG_PRINCIPAL, fg=COLOR_ACENTO, width=3,
        ).pack(side="left")
        tk.Label(
            fila, text=texto,
            font=("Helvetica", 10),
            bg=BG_PRINCIPAL, fg=COLOR_TEXTO,
            anchor="w", wraplength=330, justify="left",
        ).pack(side="left", fill="x", expand=True)


class PantallaRestaurantes(tk.Frame):
    """
    Frame embebible que lista todos los restaurantes.

    Callbacks esperados:
    on_volver : callable  → regresa a PantallaPrincipal
    usuario   : dict      → usuario activo (puede ser None)
    """

    def __init__(self, parent, on_volver, usuario=None, **kwargs):
        super().__init__(parent, bg=BG_PRINCIPAL, **kwargs)
        self._on_volver = on_volver
        self._usuario   = usuario
        self._construir_ui()

    # ── Construcción ──────────────────────────────────────────────────────────

    def _construir_ui(self):
        self._construir_header()
        tk.Frame(self, bg=COLOR_BORDE, height=1).pack(fill="x")
        self._construir_area_scroll()
        self._cargar_restaurantes()
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
            header, text="  Restaurantes",
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

    # ── Datos ─────────────────────────────────────────────────────────────────

    def _cargar_restaurantes(self):
        for w in self._frame_lista.winfo_children():
            w.destroy()

        restaurantes = _leer_restaurantes()

        if not restaurantes:
            tk.Label(
                self._frame_lista,
                text="No hay restaurantes registrados.",
                font=("Helvetica", 13), bg=BG_PRINCIPAL,
                fg=COLOR_GRIS, pady=40,
            ).pack()
            return

        # Subtítulo
        tk.Label(
            self._frame_lista,
            text=f"{len(restaurantes)} restaurante{'s' if len(restaurantes) != 1 else ''} disponible{'s' if len(restaurantes) != 1 else ''}",
            font=("Helvetica", 10),
            bg=BG_PRINCIPAL, fg=COLOR_GRIS, pady=10,
        ).pack(anchor="w", padx=20)

        for r in restaurantes:
            self._crear_tarjeta(r)

    def _crear_tarjeta(self, restaurante: dict):
        categoria = restaurante.get("categoria", "")
        color_cat = COLORES_CAT.get(categoria, COLOR_CAT_DEFAULT)

        wrapper = tk.Frame(self._frame_lista, bg=BG_PRINCIPAL)
        wrapper.pack(fill="x", padx=20, pady=6)

        card = tk.Frame(wrapper, bg=BG_CARD, cursor="hand2")
        card.pack(fill="x")

        # Franja color arriba
        tk.Frame(card, bg=color_cat, height=4).pack(fill="x")

        cuerpo = tk.Frame(card, bg=BG_CARD, padx=16, pady=12)
        cuerpo.pack(fill="x")

        # Fila superior: emoji + nombre + flecha
        fila_top = tk.Frame(cuerpo, bg=BG_CARD)
        fila_top.pack(fill="x")

        emoji = restaurante.get("imagen_emoji", "🍽️")
        tk.Label(
            fila_top, text=emoji,
            font=("Helvetica", 20),
            bg=BG_CARD, fg=COLOR_TEXTO,
        ).pack(side="left", padx=(0, 10))

        nombre_frame = tk.Frame(fila_top, bg=BG_CARD)
        nombre_frame.pack(side="left", fill="x", expand=True)

        nombre_lbl = tk.Label(
            nombre_frame,
            text=restaurante.get("nombre", "—"),
            font=("Georgia", 13, "bold"),
            bg=BG_CARD, fg=COLOR_TEXTO,
            anchor="w", cursor="hand2",
        )
        nombre_lbl.pack(anchor="w")

        # Dirección abreviada
        direccion = restaurante.get("direccion", "")
        if direccion:
            tk.Label(
                nombre_frame, text=f"📍 {direccion}",
                font=("Helvetica", 8),
                bg=BG_CARD, fg=COLOR_GRIS, anchor="w",
            ).pack(anchor="w")

        tk.Label(
            fila_top, text="›",
            font=("Helvetica", 18),
            bg=BG_CARD, fg=COLOR_GRIS,
        ).pack(side="right")

        # Descripción
        desc = restaurante.get("descripcion", "")
        if desc:
            tk.Label(
                cuerpo, text=desc,
                font=("Helvetica", 10),
                bg=BG_CARD, fg=COLOR_GRIS,
                anchor="w", wraplength=420, justify="left",
            ).pack(fill="x", pady=(6, 0))

        # Fila inferior: teléfono + categoría
        fila_bot = tk.Frame(cuerpo, bg=BG_CARD)
        fila_bot.pack(fill="x", pady=(8, 0))

        telefono = restaurante.get("telefono", "")
        if telefono:
            tk.Label(
                fila_bot, text=f"📞 {telefono}",
                font=("Helvetica", 9),
                bg=BG_CARD, fg=COLOR_GRIS,
            ).pack(side="left")

        if categoria:
            tk.Label(
                fila_bot, text=categoria,
                font=("Helvetica", 8, "bold"),
                bg=color_cat, fg="#FFFFFF", padx=6, pady=2,
            ).pack(side="right")

        # Separador
        tk.Frame(self._frame_lista, bg=COLOR_BORDE, height=1).pack(fill="x", padx=20)

        # Hover + clic → popup
        todos = [card, cuerpo, fila_top, nombre_frame, nombre_lbl, fila_bot]
        for w in todos:
            w.bind("<Enter>", lambda e, c=card: self._hover_enter(c))
            w.bind("<Leave>", lambda e, c=card: self._hover_leave(c))
            w.bind("<Button-1>", lambda e, r=restaurante: self._abrir_popup(r))

    # ── Eventos ───────────────────────────────────────────────────────────────

    def _abrir_popup(self, restaurante: dict):
        PopupRestaurante(self.winfo_toplevel(), restaurante)

    def _hover_enter(self, card):
        card.configure(bg=BG_CARD_HOVER)
        for c in card.winfo_children():
            try: c.configure(bg=BG_CARD_HOVER)
            except tk.TclError: pass

    def _hover_leave(self, card):
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