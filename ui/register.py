"""
ui/register.py
Pantalla de registro de nuevo usuario.
"""

import tkinter as tk
from logica.auth import registrar_usuario

BG_PRINCIPAL = "#0F1923"
BG_CARD      = "#1A2535"
COLOR_ACENTO = "#FF6B35"
COLOR_TEXTO  = "#F0EDE8"
COLOR_GRIS   = "#8A9BB0"
COLOR_BORDE  = "#2A3D55"
COLOR_ERROR  = "#FF6B6B"
COLOR_OK     = "#6FCF6F"


class PantallaRegistro(tk.Frame):
    def __init__(self, parent, on_registro_exitoso=None, on_ir_login=None):
        super().__init__(parent, bg=BG_PRINCIPAL)
        self.on_registro_exitoso = on_registro_exitoso
        self.on_ir_login         = on_ir_login
        self._construir()

    def _construir(self):
        # Logo
        tk.Label(
            self, text="🍽️  Menugo",
            font=("Georgia", 20, "bold"),
            bg=BG_PRINCIPAL, fg=COLOR_ACENTO,
        ).pack(pady=(20, 2))

        tk.Label(
            self, text="Crea tu cuenta",
            font=("Helvetica", 11),
            bg=BG_PRINCIPAL, fg=COLOR_GRIS,
        ).pack(pady=(0, 10))

        # Card
        card = tk.Frame(self, bg=BG_CARD, padx=36, pady=16)
        card.pack(padx=60, fill="x")

        # Franja de acento
        tk.Frame(card, bg=COLOR_ACENTO, height=4).pack(fill="x", pady=(0, 14))

        # Nombre
        self._campo(card, "Nombre completo")
        self.ent_nombre = self._entrada(card)

        # Correo
        self._campo(card, "Correo electrónico")
        self.ent_correo = self._entrada(card)

        # Contraseña
        self._campo(card, "Contraseña (mínimo 4 caracteres)")
        self.ent_contrasena = self._entrada(card, ocultar=True)

        # Confirmar contraseña
        self._campo(card, "Confirmar contraseña")
        self.ent_confirmar = self._entrada(card, ocultar=True)
        self.ent_confirmar.bind("<Return>", lambda e: self._registrar())

        # Mensaje feedback
        self.lbl_msg = tk.Label(
            card, text="",
            font=("Helvetica", 10),
            bg=BG_CARD, fg=COLOR_ERROR,
            wraplength=320,
        )
        self.lbl_msg.pack(pady=(6, 0))

        # Botón crear cuenta
        tk.Button(
            card, text="Crear cuenta",
            font=("Helvetica", 12, "bold"),
            bg=COLOR_ACENTO, fg="#FFFFFF",
            activebackground="#E55A28",
            relief="flat", cursor="hand2",
            padx=20, pady=8,
            command=self._registrar,
        ).pack(fill="x", pady=(12, 0))

        # Enlace al login
        enlace_frame = tk.Frame(card, bg=BG_CARD)
        enlace_frame.pack(pady=(12, 0))

        tk.Label(
            enlace_frame, text="¿Ya tienes cuenta? ",
            font=("Helvetica", 10),
            bg=BG_CARD, fg=COLOR_GRIS,
        ).pack(side="left")

        lbl_login = tk.Label(
            enlace_frame, text="Inicia sesión",
            font=("Helvetica", 10, "underline"),
            bg=BG_CARD, fg=COLOR_ACENTO, cursor="hand2",
        )
        lbl_login.pack(side="left")
        lbl_login.bind(
            "<Button-1>",
            lambda e: self.on_ir_login() if self.on_ir_login else None,
        )

    def _campo(self, parent, texto: str):
        tk.Label(
            parent, text=texto,
            font=("Helvetica", 9),
            bg=BG_CARD, fg=COLOR_GRIS, anchor="w",
        ).pack(fill="x", pady=(8, 2))

    def _entrada(self, parent, ocultar=False):
        ent = tk.Entry(
            parent,
            font=("Helvetica", 11),
            bg="#0F1923", fg=COLOR_TEXTO,
            insertbackground=COLOR_TEXTO,
            relief="flat",
            show="●" if ocultar else "",
        )
        ent.pack(fill="x", ipady=6)
        tk.Frame(parent, bg=COLOR_BORDE, height=1).pack(fill="x")
        return ent

    def _registrar(self):
        nombre     = self.ent_nombre.get().strip()
        correo     = self.ent_correo.get().strip()
        contrasena = self.ent_contrasena.get().strip()
        confirmar  = self.ent_confirmar.get().strip()

        if contrasena != confirmar:
            self.lbl_msg.configure(fg=COLOR_ERROR, text="Las contraseñas no coinciden.")
            return

        resultado = registrar_usuario(nombre, correo, contrasena)

        if resultado["exito"]:
            self.lbl_msg.configure(fg=COLOR_OK, text=resultado["mensaje"])
            if self.on_ir_login:
                self.after(1000, self.on_ir_login)
        else:
            self.lbl_msg.configure(fg=COLOR_ERROR, text=resultado["mensaje"])