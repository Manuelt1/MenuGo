"""
utils/file_handler.py
Centraliza toda la lectura y escritura de archivos JSON del proyecto Menugo.
Ningún otro módulo debe leer o escribir archivos directamente.
"""

import json
import os

# Ruta base hacia la carpeta datos/ relativa a este archivo
_BASE = os.path.join(os.path.dirname(__file__), '..', 'datos')

RUTA_USUARIOS     = os.path.normpath(os.path.join(_BASE, 'usuarios.json'))
RUTA_RESTAURANTES = os.path.normpath(os.path.join(_BASE, 'restaurantes.json'))
RUTA_FAVORITOS    = os.path.normpath(os.path.join(_BASE, 'favoritos.json'))


# ──────────────────────────────────────────────
# Funciones genéricas (privadas)
# ──────────────────────────────────────────────

def _leer(ruta: str) -> list:
    """Lee un archivo JSON y devuelve su contenido como lista."""
    try:
        with open(ruta, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return []


def _escribir(ruta: str, datos: list) -> None:
    """Escribe una lista en un archivo JSON con formato legible."""
    with open(ruta, 'w', encoding='utf-8') as f:
        json.dump(datos, f, ensure_ascii=False, indent=2)


# ──────────────────────────────────────────────
# Usuarios
# ──────────────────────────────────────────────

def leer_usuarios() -> list:
    """Devuelve la lista completa de usuarios registrados."""
    return _leer(RUTA_USUARIOS)


def guardar_usuarios(usuarios: list) -> None:
    """Reemplaza el archivo de usuarios con la lista recibida."""
    _escribir(RUTA_USUARIOS, usuarios)


def agregar_usuario(usuario: dict) -> None:
    """Agrega un nuevo usuario al archivo sin borrar los existentes."""
    usuarios = leer_usuarios()
    usuarios.append(usuario)
    guardar_usuarios(usuarios)


def buscar_usuario_por_correo(correo: str) -> dict | None:
    """Devuelve el usuario que coincide con el correo, o None si no existe."""
    for usuario in leer_usuarios():
        if usuario.get('correo', '').lower() == correo.lower():
            return usuario
    return None


# ──────────────────────────────────────────────
# Restaurantes
# ──────────────────────────────────────────────

def leer_restaurantes() -> list:
    """Devuelve la lista completa de restaurantes con sus productos."""
    return _leer(RUTA_RESTAURANTES)


def leer_restaurantes_por_categoria(categoria: str) -> list:
    """Filtra y devuelve los restaurantes que pertenecen a la categoría dada."""
    return [r for r in leer_restaurantes() if r.get('categoria') == categoria]


def leer_categorias() -> list:
    """Devuelve la lista de categorías únicas disponibles en los restaurantes."""
    restaurantes = leer_restaurantes()
    categorias = {r.get('categoria') for r in restaurantes if r.get('categoria')}
    return sorted(list(categorias))


def leer_productos_por_categoria(categoria: str) -> list:
    """
    Devuelve una lista de productos de todos los restaurantes de la categoría.
    Cada producto incluye el campo 'restaurante' con el nombre del origen.
    """
    productos = []
    for restaurante in leer_restaurantes_por_categoria(categoria):
        for producto in restaurante.get('productos', []):
            producto_enriquecido = producto.copy()
            producto_enriquecido['restaurante'] = restaurante['nombre']
            producto_enriquecido['restaurante_id'] = restaurante['id']
            productos.append(producto_enriquecido)
    return productos


def leer_menu_del_dia() -> list:
    """Devuelve todos los productos marcados como menu_del_dia=True."""
    productos = []
    for restaurante in leer_restaurantes():
        for producto in restaurante.get('productos', []):
            if producto.get('menu_del_dia'):
                producto_enriquecido = producto.copy()
                producto_enriquecido['restaurante'] = restaurante['nombre']
                producto_enriquecido['restaurante_id'] = restaurante['id']
                productos.append(producto_enriquecido)
    return productos


def buscar_productos(termino: str, categoria: str = None, precio_max: int = None) -> list:
    """
    Busca productos por nombre. Permite filtrar opcionalmente por
    categoría de restaurante y precio máximo.
    """
    resultados = []
    termino = termino.lower().strip()
    for restaurante in leer_restaurantes():
        if categoria and restaurante.get('categoria') != categoria:
            continue
        for producto in restaurante.get('productos', []):
            nombre = producto.get('nombre', '').lower()
            precio = producto.get('precio', 0)
            if termino in nombre:
                if precio_max is None or precio <= precio_max:
                    enriquecido = producto.copy()
                    enriquecido['restaurante'] = restaurante['nombre']
                    enriquecido['restaurante_id'] = restaurante['id']
                    resultados.append(enriquecido)
    return resultados


# ──────────────────────────────────────────────
# Favoritos
# ──────────────────────────────────────────────

def leer_favoritos() -> list:
    """Devuelve la lista completa de relaciones usuario–restaurante favorito."""
    return _leer(RUTA_FAVORITOS)


def guardar_favoritos(favoritos: list) -> None:
    """Reemplaza el archivo de favoritos con la lista recibida."""
    _escribir(RUTA_FAVORITOS, favoritos)


def agregar_favorito(correo_usuario: str, restaurante_id: str) -> bool:
    """
    Agrega un restaurante a los favoritos del usuario.
    Devuelve False si ya existía la relación, True si se agregó.
    """
    favoritos = leer_favoritos()
    for f in favoritos:
        if f['correo'] == correo_usuario and f['restaurante_id'] == restaurante_id:
            return False  # ya existe
    favoritos.append({'correo': correo_usuario, 'restaurante_id': restaurante_id})
    guardar_favoritos(favoritos)
    return True


def eliminar_favorito(correo_usuario: str, restaurante_id: str) -> bool:
    """
    Elimina un restaurante de los favoritos del usuario.
    Devuelve True si se eliminó, False si no existía.
    """
    favoritos = leer_favoritos()
    nuevos = [f for f in favoritos
              if not (f['correo'] == correo_usuario and f['restaurante_id'] == restaurante_id)]
    if len(nuevos) == len(favoritos):
        return False
    guardar_favoritos(nuevos)
    return True


def leer_favoritos_de_usuario(correo_usuario: str) -> list:
    """
    Devuelve la lista de restaurantes completos que el usuario marcó
    como favoritos, cruzando datos con restaurantes.json.
    """
    favoritos = leer_favoritos()
    ids_favoritos = {f['restaurante_id'] for f in favoritos if f['correo'] == correo_usuario}
    return [r for r in leer_restaurantes() if r['id'] in ids_favoritos]


def es_favorito(correo_usuario: str, restaurante_id: str) -> bool:
    """Devuelve True si el restaurante ya está en los favoritos del usuario."""
    for f in leer_favoritos():
        if f['correo'] == correo_usuario and f['restaurante_id'] == restaurante_id:
            return True
    return False