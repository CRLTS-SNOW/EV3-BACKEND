# gestion/auth_utils.py

def check_role(user, roles):
    """
    Comprueba si un usuario pertenece a una lista de roles.
    """
    if not user.is_authenticated:
        return False
    try:
        # Comprueba si el rol del perfil del usuario está en la lista de roles permitidos
        return user.profile.role in roles
    except:
        # Si el usuario no tiene perfil (ej. un superusuario sin perfil)
        # o cualquier otro error, se deniega el acceso.
        return False

def is_admin(user):
    """ Chequea si el usuario es Admin O Superusuario """
    if user.is_superuser:
        return True
    return check_role(user, ['admin'])

def is_bodega_or_admin(user):
    """ Chequea si es Admin O Bodeguero """
    if user.is_superuser:
        return True
    return check_role(user, ['admin', 'bodega'])

def is_ventas_or_admin(user):
    """ Chequea si es Admin O Vendedor """
    if user.is_superuser:
        return True
    return check_role(user, ['admin', 'ventas'])