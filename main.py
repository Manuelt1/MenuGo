"""
main.py  —  Menugo (versión web completa)
Lanza Flask y abre el navegador. Ya no usa Tkinter.
Ejecutar con: python main.py
"""

import threading
import webbrowser
import time

PUERTO = 5000

def _lanzar_flask():
    from web.servidor import iniciar_servidor
    iniciar_servidor(PUERTO)

def main():
    print("=" * 42)
    print("  🍽️  Menugo — iniciando servidor...")
    print("=" * 42)

    hilo = threading.Thread(target=_lanzar_flask, daemon=True)
    hilo.start()

    # Esperar que Flask levante antes de abrir el navegador
    time.sleep(1.5)

    url = f"http://127.0.0.1:{PUERTO}/login"
    print(f"  ✅ Servidor listo en {url}")
    print("  Cierra esta ventana para detener la app.")
    print("=" * 42)

    webbrowser.open(url)

    # Mantener el proceso vivo mientras el hilo daemon corre
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n  👋 Menugo cerrado.")

if __name__ == "__main__":
    main()