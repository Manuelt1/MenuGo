"""
ui/login.py
Pantalla de inicio de sesión.
Expone PantallaLogin(Frame) para uso con el controlador main.py.
"""

import tkinter as tk
from logica.auth import iniciar_sesion

BG_PRINCIPAL = "#0F1923"
BG_CARD      = "#1A2535"
COLOR_ACENTO = "#FF6B35"
COLOR_TEXTO  = "#F0EDE8"
COLOR_GRIS   = "#8A9BB0"
COLOR_BORDE  = "#2A3D55"
COLOR_ERROR  = "#FF6B6B"
COLOR_OK     = "#6FCF6F"


class PantallaLogin(tk.Frame):
    """
    Frame de inicio de sesión.
    Parámetros:
      parent            – widget padre
      on_login_exitoso  – callback(usuario: dict) al autenticarse con éxito
      on_ir_registro    – callback() para navegar al registro
    """

    def __init__(self, parent, on_login_exitoso=None, on_ir_registro=None):
        super().__init__(parent, bg=BG_PRINCIPAL)
        self.on_login_exitoso = on_login_exitoso
        self.on_ir_registro   = on_ir_registro
        self._construir()

    def _construir(self):
        # ── Logo ──────────────────────────────
        tk.Label(
            self, text="🍽️  Menugo",
            font=("Georgia", 24, "bold"),
            bg=BG_PRINCIPAL, fg=COLOR_ACENTO,
        ).pack(pady=(56, 4))

        tk.Label(
            self, text="Tu guía de sabores",
            font=("Helvetica", 12),
            bg=BG_PRINCIPAL, fg=COLOR_GRIS,
        ).pack(pady=(0, 32))

        # ── Card del formulario ───────────────
        card = tk.Frame(self, bg=BG_CARD, padx=36, pady=32)
        card.pack(padx=60)

        # Franja superior de acento
        tk.Frame(card, bg=COLOR_ACENTO, height=4).pack(fill="x", pady=(0, 24))

        # Correo
        self._campo(card, "Correo electrónico")
        self.ent_correo = self._entrada(card)

        # Contraseña
        self._campo(card, "Contraseña")
        self.ent_contrasena = self._entrada(card, ocultar=True)

        # Bind Enter para login rápido
        self.ent_contrasena.bind("<Return>", lambda e: self._iniciar_sesion())

        # Mensaje de feedback
        self.lbl_msg = tk.Label(
            card, text="",
            font=("Helvetica", 10),
            bg=BG_CARD, fg=COLOR_ERROR,
            wraplength=320,
        )
        self.lbl_msg.pack(pady=(8, 0))

        # Botón ingresar
        tk.Button(
            card, text="Ingresar",
            font=("Helvetica", 12, "bold"),
            bg=COLOR_ACENTO, fg="#FFFFFF",
            activebackground="#E55A28",
            relief="flat", cursor="hand2",
            padx=20, pady=10,
            command=self._iniciar_sesion,
        ).pack(fill="x", pady=(16, 0))

        # Enlace al registro
        enlace_frame = tk.Frame(card, bg=BG_CARD)
        enlace_frame.pack(pady=(16, 0))

        tk.Label(
            enlace_frame, text="¿No tienes cuenta? ",
            font=("Helvetica", 10),
            bg=BG_CARD, fg=COLOR_GRIS,
        ).pack(side="left")

        lbl_reg = tk.Label(
            enlace_frame, text="Regístrate",
            font=("Helvetica", 10, "underline"),
            bg=BG_CARD, fg=COLOR_ACENTO, cursor="hand2",
        )
        lbl_reg.pack(side="left")
        lbl_reg.bind("<Button-1>", lambda e: self.on_ir_registro() if self.on_ir_registro else None)

    # ── Helpers ───────────────────────────────

    def _campo(self, parent, texto: str):
        tk.Label(
            parent, text=texto,
            font=("Helvetica", 10),
            bg=BG_CARD, fg=COLOR_GRIS, anchor="w",
        ).pack(fill="x", pady=(12, 2))

    def _entrada(self, parent, ocultar=False):
        ent = tk.Entry(
            parent,
            font=("Helvetica", 12),
            bg="#0F1923", fg=COLOR_TEXTO,
            insertbackground=COLOR_TEXTO,
            relief="flat",
            show="●" if ocultar else "",
        )
        ent.pack(fill="x", ipady=8)
        tk.Frame(parent, bg=COLOR_BORDE, height=1).pack(fill="x")
        return ent

    # ── Lógica ────────────────────────────────

    def _iniciar_sesion(self):
        correo     = self.ent_correo.get()
        contrasena = self.ent_contrasena.get()

        resultado = iniciar_sesion(correo, contrasena)

        if resultado['exito']:
            self.lbl_msg.configure(fg=COLOR_OK, text=resultado['mensaje'])
            if self.on_login_exitoso:
                self.after(600, lambda: self.on_login_exitoso(resultado['usuario']))
        else:
            self.lbl_msg.configure(fg=COLOR_ERROR, text=resultado['mensaje'])


# ── Prueba independiente ──────────────────────
if __name__ == "__main__":
    root = tk.Tk()
    root.title("Menugo — Login")
    root.geometry("520x520")
    root.configure(bg=BG_PRINCIPAL)
    root.resizable(False, False)

    def on_exito(u):
        print(f"Sesión iniciada: {u['nombre']}")
        root.destroy()

    pantalla = PantallaLogin(root, on_login_exitoso=on_exito)
    pantalla.pack(fill="both", expand=True)
    root.mainloop()