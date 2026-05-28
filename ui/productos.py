"""
ui/productos.py
Pantalla que muestra los productos de una categoría seleccionada.
Sprint 4: añadido botón 💳 Pagar que abre el navegador en /pago.
"""

import tkinter as tk
from tkinter import ttk
import webbrowser
from utils.file_handler import leer_productos_por_categoria

COLORES_CATEGORIA = {
    'Almuerzos':     '#E8593C',
    'Comida Rápida': '#F0A500',
    'Bebidas':       '#2196A6',
}

EMOJIS_CATEGORIA = {
    'Almuerzos':     '🍱',
    'Comida Rápida': '🍔',
    'Bebidas':       '🥤',
}

PUERTO_WEB = 5000


def abrir_productos(categoria: str, usuario: dict, on_volver=None):
    ventana = tk.Tk()
    ventana.title(f"Menugo — {categoria}")
    ventana.geometry("500x620")
    ventana.resizable(False, False)
    ventana.configure(bg="#F7F5F2")

    color    = COLORES_CATEGORIA.get(categoria, '#888888')
    emoji    = EMOJIS_CATEGORIA.get(categoria, '🍽️')
    productos = leer_productos_por_categoria(categoria)

    # ── Barra superior ───────────────────────────
    barra = tk.Frame(ventana, bg=color, height=64)
    barra.pack(fill="x")
    barra.pack_propagate(False)

    tk.Button(
        barra, text="← Volver",
        font=("Helvetica", 10), bg=color, fg="#FFFFFF",
        activebackground=color, activeforeground="#FFFFFF",
        relief="flat", cursor="hand2",
        command=lambda: [ventana.destroy(), on_volver() if on_volver else None]
    ).pack(side="left", padx=16, pady=16)

    tk.Label(barra, text=f"{emoji}  {categoria}",
             font=("Helvetica", 16, "bold"),
             bg=color, fg="#FFFFFF").pack(side="left", pady=16)

    # ── Subtítulo ────────────────────────────────
    tk.Label(ventana,
             text=f"{len(productos)} producto{'s' if len(productos) != 1 else ''} disponibles",
             font=("Helvetica", 11), bg="#F7F5F2", fg="#888888").pack(pady=(18, 12))

    # ── Contenedor con scroll ────────────────────
    frame_scroll = tk.Frame(ventana, bg="#F7F5F2")
    frame_scroll.pack(fill="both", expand=True, padx=24)

    canvas = tk.Canvas(frame_scroll, bg="#F7F5F2", highlightthickness=0, bd=0)
    scrollbar = ttk.Scrollbar(frame_scroll, orient="vertical", command=canvas.yview)
    frame_contenido = tk.Frame(canvas, bg="#F7F5F2")

    frame_contenido.bind(
        "<Configure>",
        lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
    )

    canvas.create_window((0, 0), window=frame_contenido, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)
    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")

    canvas.bind_all("<MouseWheel>",
                    lambda e: canvas.yview_scroll(int(-1 * (e.delta / 120)), "units"))

    # ── Tarjetas de productos ────────────────────
    if not productos:
        tk.Label(frame_contenido,
                 text="No hay productos disponibles\nen esta categoría.",
                 font=("Helvetica", 13), bg="#F7F5F2",
                 fg="#AAAAAA", justify="center").pack(pady=60)
    else:
        for producto in productos:
            _crear_tarjeta_producto(frame_contenido, producto, color)

    # ── Pie ──────────────────────────────────────
    tk.Label(ventana, text=f"Conectado como {usuario.get('nombre', '')}",
             font=("Helvetica", 9), bg="#F7F5F2", fg="#CCCCCC").pack(pady=10)

    ventana.mainloop()


def _crear_tarjeta_producto(parent, producto: dict, color_acento: str):
    card = tk.Frame(parent, bg="#FFFFFF", relief="flat")
    card.pack(fill="x", pady=6)

    tk.Frame(card, bg=color_acento, height=4).pack(fill="x")

    cuerpo = tk.Frame(card, bg="#FFFFFF")
    cuerpo.pack(fill="x", padx=18, pady=14)

    # Nombre + precio
    fila_top = tk.Frame(cuerpo, bg="#FFFFFF")
    fila_top.pack(fill="x")

    tk.Label(fila_top,
             text=producto.get('nombre', ''),
             font=("Helvetica", 13, "bold"),
             bg="#FFFFFF", fg="#1A1A1A", anchor="w").pack(side="left")

    precio = producto.get('precio', 0)
    tk.Label(fila_top,
             text=f"${precio:,}",
             font=("Helvetica", 13, "bold"),
             bg="#FFFFFF", fg=color_acento, anchor="e").pack(side="right")

    # Descripción
    descripcion = producto.get('descripcion', '')
    if descripcion:
        tk.Label(cuerpo, text=descripcion,
                 font=("Helvetica", 10), bg="#FFFFFF", fg="#888888",
                 anchor="w", wraplength=400, justify="left").pack(fill="x", pady=(4, 6))

    # Restaurante + badge menú del día
    frame_rest = tk.Frame(cuerpo, bg="#FFFFFF")
    frame_rest.pack(fill="x", pady=(2, 0))

    tk.Label(frame_rest, text="📍", font=("Helvetica", 10), bg="#FFFFFF").pack(side="left")
    tk.Label(frame_rest,
             text=producto.get('restaurante', ''),
             font=("Helvetica", 10), bg="#FFFFFF", fg="#AAAAAA",
             anchor="w").pack(side="left", padx=4)

    if producto.get('menu_del_dia'):
        tk.Label(frame_rest, text="⭐ Menú del día",
                 font=("Helvetica", 9, "bold"),
                 bg="#FFF3E0", fg="#E65100",
                 padx=6, pady=2).pack(side="right")

    # ── Botón Pagar ── Sprint 4
    rid = producto.get('restaurante_id', '')
    pid = producto.get('id', '')

    tk.Button(
        cuerpo,
        text="💳 Pagar",
        font=("Helvetica", 10, "bold"),
        bg="#FF6B35", fg="#FFFFFF",
        activebackground="#E55A26", activeforeground="#FFFFFF",
        relief="flat", cursor="hand2",
        padx=12, pady=6,
        command=lambda r=rid, p=pid: webbrowser.open(
            f"http://127.0.0.1:{PUERTO_WEB}/pago?restaurante_id={r}&producto_id={p}"
        )
    ).pack(anchor="e", pady=(10, 0))