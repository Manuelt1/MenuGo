import tkinter as tk
from ui.login import PantallaLogin
from ui.main import PantallaPrincipal
from ui.productos import abrir_productos

class App:
    def __init__(self, root):
        self.root = root
        self.root.title("Menugo")
        self.root.geometry("620x560")
        self.root.resizable(False, False)

        self.usuario = None
        self.mostrar_login()

    # ───────────────────────────────
    # Utilidad para limpiar pantalla
    # ───────────────────────────────
    def limpiar_pantalla(self):
        for widget in self.root.winfo_children():
            widget.destroy()

    # ───────────────────────────────
    # Login
    # ───────────────────────────────
    def mostrar_login(self):
        self.limpiar_pantalla()

        pantalla = PantallaLogin(
            self.root,
            on_login_exitoso=self.on_login_exitoso
        )
        pantalla.pack(fill="both", expand=True)

    def on_login_exitoso(self, usuario):
        self.usuario = usuario
        self.mostrar_main()

    # ───────────────────────────────
    # Pantalla principal
    # ───────────────────────────────
    def mostrar_main(self):
        self.limpiar_pantalla()

        def al_seleccionar_categoria(cat):
            abrir_productos(
                cat,
                self.usuario,
                on_volver=self.mostrar_main
            )

        pantalla = PantallaPrincipal(
            self.root,
            self.usuario,
            on_categoria=al_seleccionar_categoria
        )
        pantalla.pack(fill="both", expand=True)


# ───────────────────────────────
# EJECUCIÓN
# ───────────────────────────────
if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()