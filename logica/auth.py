"""
logica/auth.py
Maneja la lógica de registro e inicio de sesión.
No toca archivos directamente; usa file_handler para todo.
"""

import hashlib
from menugo.utils.file_handler import (
    buscar_usuario_por_correo,
    agregar_usuario
)


def _hashear(contrasena: str) -> str:
    """Convierte la contraseña en un hash SHA-256 antes de guardarla."""
    return hashlib.sha256(contrasena.encode('utf-8')).hexdigest()


def registrar_usuario(nombre: str, correo: str, contrasena: str) -> dict:
    """
    Intenta registrar un nuevo usuario.
    Devuelve un dict con 'exito' (bool) y 'mensaje' (str).
    """
    nombre = nombre.strip()
    correo = correo.strip().lower()
    contrasena = contrasena.strip()

    if not nombre or not correo or not contrasena:
        return {'exito': False, 'mensaje': 'Todos los campos son obligatorios.'}

    if '@' not in correo or '.' not in correo:
        return {'exito': False, 'mensaje': 'El correo no tiene un formato válido.'}

    if len(contrasena) < 4:
        return {'exito': False, 'mensaje': 'La contraseña debe tener al menos 4 caracteres.'}

    if buscar_usuario_por_correo(correo):
        return {'exito': False, 'mensaje': 'Este correo ya está registrado.'}

    agregar_usuario({
        'nombre': nombre,
        'correo': correo,
        'contrasena': _hashear(contrasena)
    })

    return {'exito': True, 'mensaje': f'¡Bienvenido, {nombre}! Tu cuenta fue creada.'}


def iniciar_sesion(correo: str, contrasena: str) -> dict:
    """
    Verifica las credenciales del usuario.
    Devuelve un dict con 'exito' (bool), 'mensaje' (str)
    y opcionalmente 'usuario' (dict) si el login fue exitoso.
    """
    correo = correo.strip().lower()
    contrasena = contrasena.strip()

    if not correo or not contrasena:
        return {'exito': False, 'mensaje': 'Ingresa tu correo y contraseña.'}

    usuario = buscar_usuario_por_correo(correo)

    if not usuario:
        return {'exito': False, 'mensaje': 'Correo o contraseña incorrectos.'}

    if usuario['contrasena'] != _hashear(contrasena):
        return {'exito': False, 'mensaje': 'Correo o contraseña incorrectos.'}

    return {
        'exito': True,
        'mensaje': f'Bienvenido de nuevo, {usuario["nombre"]}.',
        'usuario': usuario
    }