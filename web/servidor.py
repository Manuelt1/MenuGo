"""
web/servidor.py  —  Menugo (versión web completa, sin Tkinter)
Rutas: login, registro, principal, productos, favoritos, menu_dia, filtros, mapa, guia, pago
API:   /api/restaurantes  /api/restaurante/<rid>  /api/pago  /api/favorito
"""

import json, os, random, string, time
from flask import (
    Flask, render_template, jsonify, request,
    redirect, url_for, session
)

from logica.auth import registrar_usuario, iniciar_sesion
from utils.file_handler import (
    leer_restaurantes, leer_restaurantes_por_categoria,
    leer_productos_por_categoria, leer_menu_del_dia,
    buscar_productos, leer_favoritos_de_usuario,
    agregar_favorito, eliminar_favorito, es_favorito,
)

app = Flask(
    __name__,
    template_folder=os.path.join(os.path.dirname(__file__), "templates"),
    static_folder=os.path.join(os.path.dirname(__file__), "static"),
)
app.secret_key = "menugo-tulua-2025-clave-secreta"


# ── Helpers ───────────────────────────────────────────────────────────────────

def _usuario_activo():
    """Devuelve el dict del usuario en sesión, o None."""
    return session.get("usuario")

def _login_requerido(destino="login"):
    """Si no hay sesión activa retorna redirect, si no retorna None."""
    if not _usuario_activo():
        return redirect(url_for(destino))
    return None


# ── Páginas de autenticación ──────────────────────────────────────────────────

@app.route("/")
def index():
    if _usuario_activo():
        return redirect(url_for("principal"))
    return redirect(url_for("login"))

@app.route("/login", methods=["GET", "POST"])
def login():
    if _usuario_activo():
        return redirect(url_for("principal"))
    error = None
    if request.method == "POST":
        correo    = request.form.get("correo", "")
        contrasena = request.form.get("contrasena", "")
        resultado = iniciar_sesion(correo, contrasena)
        if resultado["exito"]:
            session["usuario"] = resultado["usuario"]
            return redirect(url_for("principal"))
        error = resultado["mensaje"]
    return render_template("login.html", error=error)

@app.route("/registro", methods=["GET", "POST"])
def registro():
    if _usuario_activo():
        return redirect(url_for("principal"))
    error = None
    exito = None
    if request.method == "POST":
        nombre    = request.form.get("nombre", "")
        correo    = request.form.get("correo", "")
        contrasena = request.form.get("contrasena", "")
        resultado = registrar_usuario(nombre, correo, contrasena)
        if resultado["exito"]:
            exito = resultado["mensaje"]
        else:
            error = resultado["mensaje"]
    return render_template("registro.html", error=error, exito=exito)

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


# ── Páginas principales (requieren sesión) ────────────────────────────────────

@app.route("/principal")
def principal():
    redir = _login_requerido()
    if redir: return redir
    restaurantes = leer_restaurantes()
    categorias = {}
    for r in restaurantes:
        cat = r.get("categoria", "Otro")
        categorias.setdefault(cat, 0)
        categorias[cat] += 1
    return render_template("principal.html",
                           usuario=_usuario_activo(),
                           categorias=categorias,
                           total_restaurantes=len(restaurantes))

@app.route("/productos/<categoria>")
def productos(categoria):
    redir = _login_requerido()
    if redir: return redir
    lista = leer_productos_por_categoria(categoria)
    return render_template("productos.html",
                           usuario=_usuario_activo(),
                           categoria=categoria,
                           productos=lista)

@app.route("/favoritos")
def favoritos():
    redir = _login_requerido()
    if redir: return redir
    usuario = _usuario_activo()
    lista = leer_favoritos_de_usuario(usuario["correo"])
    return render_template("favoritos.html",
                           usuario=usuario,
                           favoritos=lista)

@app.route("/menu-dia")
def menu_dia():
    redir = _login_requerido()
    if redir: return redir
    lista = leer_menu_del_dia()
    return render_template("menu_dia.html",
                           usuario=_usuario_activo(),
                           productos=lista)

@app.route("/filtros")
def filtros():
    redir = _login_requerido()
    if redir: return redir
    termino    = request.args.get("q", "").strip()
    categoria  = request.args.get("categoria", "")
    precio_max = request.args.get("precio_max", "")
    resultados = []
    if termino:
        precio_max_int = int(precio_max) if precio_max.isdigit() else None
        resultados = buscar_productos(termino,
                                      categoria or None,
                                      precio_max_int)
    categorias_disponibles = list({r.get("categoria")
                                   for r in leer_restaurantes()
                                   if r.get("categoria")})
    return render_template("filtros.html",
                           usuario=_usuario_activo(),
                           resultados=resultados,
                           termino=termino,
                           categoria=categoria,
                           precio_max=precio_max,
                           categorias=sorted(categorias_disponibles))

@app.route("/mapa")
def mapa():
    redir = _login_requerido()
    if redir: return redir
    return render_template("mapa.html", usuario=_usuario_activo())

@app.route("/guia")
def guia():
    redir = _login_requerido()
    if redir: return redir
    return render_template("guia.html", usuario=_usuario_activo())

@app.route("/pago")
def pago():
    redir = _login_requerido()
    if redir: return redir
    restaurante_id = request.args.get("restaurante_id", "")
    producto_id    = request.args.get("producto_id", "")
    # Buscar datos del producto para mostrarlos
    producto_info = None
    restaurante_info = None
    for r in leer_restaurantes():
        if r["id"] == restaurante_id:
            restaurante_info = r
            for p in r.get("productos", []):
                if p["id"] == producto_id:
                    producto_info = p
                    break
    return render_template("pago.html",
                           usuario=_usuario_activo(),
                           restaurante_id=restaurante_id,
                           producto_id=producto_id,
                           producto=producto_info,
                           restaurante=restaurante_info)


# ── API JSON ──────────────────────────────────────────────────────────────────

@app.route("/api/restaurantes")
def api_restaurantes():
    resultado = [r for r in leer_restaurantes() if r.get("lat") and r.get("lng")]
    return jsonify(resultado)

@app.route("/api/restaurante/<rid>")
def api_restaurante(rid):
    for r in leer_restaurantes():
        if r.get("id") == rid:
            return jsonify(r)
    return jsonify({}), 404

@app.route("/api/favorito", methods=["POST", "DELETE"])
def api_favorito():
    if not _usuario_activo():
        return jsonify({"exito": False, "mensaje": "No autenticado"}), 401
    data = request.get_json(silent=True) or {}
    correo = _usuario_activo()["correo"]
    rid    = data.get("restaurante_id", "")
    if not rid:
        return jsonify({"exito": False, "mensaje": "restaurante_id requerido"}), 400
    if request.method == "POST":
        agregado = agregar_favorito(correo, rid)
        return jsonify({"exito": True, "agregado": agregado,
                        "es_favorito": True})
    else:
        eliminado = eliminar_favorito(correo, rid)
        return jsonify({"exito": True, "eliminado": eliminado,
                        "es_favorito": False})

@app.route("/api/pago", methods=["POST"])
def api_pago():
    data = request.get_json(silent=True) or {}
    requeridos = ["nombre", "correo", "tarjeta", "monto"]
    for campo in requeridos:
        if not data.get(campo):
            return jsonify({"exito": False,
                            "mensaje": f"El campo '{campo}' es obligatorio."}), 400
    tarjeta = str(data.get("tarjeta", "")).replace(" ", "")
    if len(tarjeta) < 13:
        return jsonify({"exito": False,
                        "mensaje": "Número de tarjeta inválido."}), 400
    time.sleep(0.6)
    ref = "MNG-" + "".join(random.choices(string.ascii_uppercase + string.digits, k=8))
    return jsonify({"exito": True, "referencia": ref,
                    "mensaje": f"Pago aprobado. Tu referencia es {ref}.",
                    "monto": data.get("monto"), "nombre": data.get("nombre")})


# ── Arranque ──────────────────────────────────────────────────────────────────

def iniciar_servidor(puerto: int = 5000):
    import logging
    logging.getLogger("werkzeug").setLevel(logging.ERROR)
    app.run(host="127.0.0.1", port=puerto, debug=False, use_reloader=False)

if __name__ == "__main__":
    app.run(debug=True, port=5000)