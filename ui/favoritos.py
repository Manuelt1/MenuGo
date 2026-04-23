"""
ui/favoritos.py
Pantalla de restaurantes favoritos del usuario.
Muestra todos los restaurantes que el usuario ha guardado,
con opción de eliminarlos desde aquí.
"""

import tkinter as tk
from tkinter import ttk
from utils.file_handler import (
    leer_favoritos_de_usuario,
    eliminar_favorito,
)

BG_PRINCIPAL  = "#0F1923"
BG_HEADER     = "#111D2B"
BG_CARD       = "#1A2535"
BG_CARD_HOVER = "#1F2E42"
COLOR_ACENTO  = "#FF6B35"
COLOR_TEXTO   = "#F0EDE8"
COLOR_GRIS    = "#8A9BB0"
COLOR_BORDE   = "#2A3D55"
COLOR_ROJO    = "#E05252"

COLORES_CATEGORIA = {
    "Almuerzos":     "#E8593C",
    "Comida Rápida": "#F0A500",
    "Bebidas":       "#2196A6",
}
EMOJIS_CATEGORIA = {
    "Almuerzos":     "🍲",
    "Comida Rápida": "🍔",
    "Bebidas":       "🥤",
}


class PantallaFavoritos(tk.Frame):
    """
    Frame que muestra los restaurantes favoritos del usuario.
    Parámetros:
      parent    – widget padre
      usuario   – dict con datos del usuario autenticado
      on_volver – callback() para regresar a la pantalla principal
    """

    def __init__(self, parent, usuario: dict, on_volver=None):
        super().__init__(parent, bg=BG_PRINCIPAL)
        self.usuario   = usuario
        self.on_volver = on_volver
        self._construir()

    # ──────────────────────────────────────────
    #  Construcción
    # ──────────────────────────────────────────

    def _construir(self):
        self._construir_header()
        self._construir_cuerpo()
        self._construir_footer()

    def _construir_header(self):
        barra = tk.Frame(self, bg=BG_HEADER, height=64)
        barra.pack(fill="x")
        barra.pack_propagate(False)

        tk.Button(
            barra, text="← Volver",
            font=("Helvetica", 10),
            bg=BG_HEADER, fg=COLOR_GRIS,
            activebackground=BG_HEADER, activeforeground=COLOR_TEXTO,
            relief="flat", cursor="hand2",
            command=lambda: self.on_volver() if self.on_volver else None,
        ).pack(side="left", padx=16, pady=16)

        tk.Label(
            barra,
            text="❤️  Mis favoritos",
            font=("Georgia", 17, "bold"),
            bg=BG_HEADER, fg=COLOR_TEXTO,
        ).pack(side="left", pady=16)

        tk.Label(
            barra,
            text=f"👤 {self.usuario.get('nombre', '')}",
            font=("Helvetica", 10),
            bg=BG_HEADER, fg=COLOR_GRIS,
        ).pack(side="right", padx=20)

    def _construir_cuerpo(self):
        """Área con scroll que contiene las tarjetas de restaurantes favoritos."""
        correo      = self.usuario.get("correo", "")
        favoritos   = leer_favoritos_de_usuario(correo)

        # Subtítulo
        plural = "restaurante guardado" if len(favoritos) == 1 else "restaurantes guardados"
        tk.Label(
            self,
            text=f"{len(favoritos)} {plural}",
            font=("Helvetica", 11),
            bg=BG_PRINCIPAL, fg=COLOR_GRIS,
        ).pack(anchor="w", padx=32, pady=(20, 4))

        tk.Frame(self, bg=COLOR_BORDE, height=1).pack(fill="x", padx=32, pady=(0, 12))

        # Scroll
        frame_scroll = tk.Frame(self, bg=BG_PRINCIPAL)
        frame_scroll.pack(fill="both", expand=True, padx=24)

        canvas = tk.Canvas(frame_scroll, bg=BG_PRINCIPAL,
                           highlightthickness=0, bd=0)
        scrollbar = ttk.Scrollbar(frame_scroll, orient="vertical",
                                  command=canvas.yview)
        self._frame_contenido = tk.Frame(canvas, bg=BG_PRINCIPAL)

        self._frame_contenido.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all")),
        )

        canvas.create_window((0, 0), window=self._frame_contenido, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        canvas.bind_all(
            "<MouseWheel>",
            lambda e: canvas.yview_scroll(int(-1 * (e.delta / 120)), "units"),
        )

        self._canvas    = canvas
        self._favoritos = favoritos

        self._renderizar_tarjetas()

    def _renderizar_tarjetas(self):
        """Limpia y vuelve a dibujar todas las tarjetas de favoritos."""
        for w in self._frame_contenido.winfo_children():
            w.destroy()

        correo    = self.usuario.get("correo", "")
        favoritos = leer_favoritos_de_usuario(correo)

        if not favoritos:
            self._mostrar_estado_vacio()
            return

        for restaurante in favoritos:
            self._crear_tarjeta(restaurante)

    def _mostrar_estado_vacio(self):
        tk.Label(
            self._frame_contenido,
            text="💔",
            font=("Helvetica", 42),
            bg=BG_PRINCIPAL,
        ).pack(pady=(48, 8))

        tk.Label(
            self._frame_contenido,
            text="Aún no tienes favoritos",
            font=("Georgia", 15, "bold"),
            bg=BG_PRINCIPAL, fg=COLOR_TEXTO,
        ).pack()

        tk.Label(
            self._frame_contenido,
            text="Explora categorías y guarda los\nrestaurantes que más te gusten.",
            font=("Helvetica", 11),
            bg=BG_PRINCIPAL, fg=COLOR_GRIS,
            justify="center",
        ).pack(pady=(8, 0))

    def _crear_tarjeta(self, restaurante: dict):
        """Crea una tarjeta visual para un restaurante favorito."""
        cat   = restaurante.get("categoria", "")
        color = COLORES_CATEGORIA.get(cat, "#6C7A9C")
        emoji = EMOJIS_CATEGORIA.get(cat, restaurante.get("imagen_emoji", "🍽️"))

        card = tk.Frame(self._frame_contenido, bg=BG_CARD)
        card.pack(fill="x", pady=6, padx=2)

        # Franja de color según categoría
        tk.Frame(card, bg=color, height=4).pack(fill="x")

        # Cuerpo
        cuerpo = tk.Frame(card, bg=BG_CARD, padx=18, pady=16)
        cuerpo.pack(fill="x")

        # Fila superior: emoji + nombre + botón eliminar
        fila_top = tk.Frame(cuerpo, bg=BG_CARD)
        fila_top.pack(fill="x")

        tk.Label(
            fila_top,
            text=emoji,
            font=("Helvetica", 22),
            bg=BG_CARD,
        ).pack(side="left", padx=(0, 10))

        tk.Label(
            fila_top,
            text=restaurante.get("nombre", ""),
            font=("Georgia", 14, "bold"),
            bg=BG_CARD, fg=COLOR_TEXTO,
            anchor="w",
        ).pack(side="left", fill="x", expand=True)

        # Botón eliminar de favoritos
        btn_eliminar = tk.Button(
            fila_top,
            text="✕ Quitar",
            font=("Helvetica", 9),
            bg=COLOR_ROJO, fg="#FFFFFF",
            activebackground="#C04040",
            relief="flat", cursor="hand2",
            padx=8, pady=4,
            command=lambda rid=restaurante["id"]: self._quitar_favorito(rid),
        )
        btn_eliminar.pack(side="right")

        # Descripción
        desc = restaurante.get("descripcion", "")
        if desc:
            tk.Label(
                cuerpo,
                text=desc,
                font=("Helvetica", 10),
                bg=BG_CARD, fg=COLOR_GRIS,
                anchor="w",
            ).pack(fill="x", pady=(8, 4))

        # Badge categoría
        badge_frame = tk.Frame(cuerpo, bg=BG_CARD)
        badge_frame.pack(fill="x", pady=(4, 0))

        tk.Label(
            badge_frame,
            text=f"  {cat}  ",
            font=("Helvetica", 9, "bold"),
            bg=color, fg="#FFFFFF",
            padx=4, pady=2,
        ).pack(side="left")

        # Número de productos
        n_prods = len(restaurante.get("productos", []))
        tk.Label(
            badge_frame,
            text=f"  🍽️ {n_prods} producto{'s' if n_prods != 1 else ''}",
            font=("Helvetica", 9),
            bg=BG_CARD, fg=COLOR_GRIS,
        ).pack(side="left", padx=10)

    def _quitar_favorito(self, restaurante_id: str):
        """Elimina el restaurante de favoritos y refresca la lista."""
        correo = self.usuario.get("correo", "")
        eliminar_favorito(correo, restaurante_id)
        self._renderizar_tarjetas()

    def _construir_footer(self):
        footer = tk.Frame(self, bg=BG_HEADER, height=36)
        footer.pack(fill="x", side="bottom")
        footer.pack_propagate(False)
        tk.Label(
            footer,
            text="Menugo © 2025",
            font=("Helvetica", 9),
            bg=BG_HEADER, fg=COLOR_GRIS,
        ).pack(expand=True)


# ── Prueba independiente ──────────────────────
if __name__ == "__main__":
    import sys
    sys.path.insert(0, ".")
    from utils.file_handler import agregar_favorito

    usuario_prueba = {"nombre": "Ana García", "correo": "ana@test.com"}
    # Agregar dos favoritos de prueba
    agregar_favorito("ana@test.com", "r001")
    agregar_favorito("ana@test.com", "r003")

    root = tk.Tk()
    root.title("Menugo — Favoritos")
    root.geometry("620x600")
    root.configure(bg=BG_PRINCIPAL)
    root.resizable(False, False)

    pantalla = PantallaFavoritos(root, usuario_prueba, on_volver=root.destroy)
    pantalla.pack(fill="both", expand=True)
    root.mainloop()