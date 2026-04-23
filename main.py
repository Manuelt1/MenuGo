"""
main.py  ─  Controlador de navegación de Menugo.
Sprint 2: añadidos _ir_menu_dia() y _ir_filtros().
Ejecutar con: python main.py
"""

import tkinter as tk

from ui.login     import PantallaLogin
from ui.register  import PantallaRegistro
from ui.main      import PantallaPrincipal
from ui.favoritos import PantallaFavoritos
from ui.menu_dia  import PantallaMenuDia
from ui.filtros   import PantallaFiltros

BG_PRINCIPAL = "#0F1923"


class AppMenugo(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Menugo")
        self.geometry("680x660")
        self.resizable(False, False)
        self.configure(bg=BG_PRINCIPAL)

        self._usuario_activo = None
        self._frame_actual   = None

        self._ir_login()

    # ── Motor de navegación ───────────────────────────────────────────────────

    def _cambiar_frame(self, nuevo_frame: tk.Frame):
        if self._frame_actual is not None:
            self._frame_actual.destroy()
        self._frame_actual = nuevo_frame
        self._frame_actual.pack(fill="both", expand=True)

    # ── Rutas ─────────────────────────────────────────────────────────────────

    def _ir_login(self):
        self._cambiar_frame(
            PantallaLogin(
                self,
                on_login_exitoso=self._on_login_exitoso,
                on_ir_registro=self._ir_registro,
            )
        )

    def _ir_registro(self):
        self._cambiar_frame(
            PantallaRegistro(
                self,
                on_registro_exitoso=self._on_login_exitoso,
                on_ir_login=self._ir_login,
            )
        )

    def _ir_principal(self):
        self._cambiar_frame(
            PantallaPrincipal(
                self,
                usuario=self._usuario_activo,
                on_categoria=self._ir_productos,
                on_favoritos=self._ir_favoritos,
                on_menu_dia=self._ir_menu_dia,
                on_filtros=self._ir_filtros,
            )
        )

    def _ir_productos(self, categoria: str):
        from ui.productos import abrir_productos
        abrir_productos(categoria, self._usuario_activo, on_volver=self._ir_principal)

    def _ir_favoritos(self):
        self._cambiar_frame(
            PantallaFavoritos(
                self,
                usuario=self._usuario_activo,
                on_volver=self._ir_principal,
            )
        )

    def _ir_menu_dia(self):
        self._cambiar_frame(
            PantallaMenuDia(
                self,
                on_volver=self._ir_principal,
                usuario=self._usuario_activo,
            )
        )

    def _ir_filtros(self):
        self._cambiar_frame(
            PantallaFiltros(
                self,
                on_volver=self._ir_principal,
                usuario=self._usuario_activo,
            )
        )

    # ── Callbacks ─────────────────────────────────────────────────────────────

    def _on_login_exitoso(self, usuario: dict):
        self._usuario_activo = usuario
        self._ir_principal()


if __name__ == "__main__":
    app = AppMenugo()
    app.mainloop()