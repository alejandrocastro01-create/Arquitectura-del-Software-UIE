import uuid


class Usuario:
    """clase padre para cualquier persona que interactue con la tienda"""

    def __init__(self, nombre: str, email: str) -> None:
        """el id lo genero yo solo con uuid, no lo paso como parametro"""
        self.id: str = str(uuid.uuid4())
        self.nombre: str = nombre
        self.email: str = email

    def is_admin(self) -> bool:
        """por defecto un usuario no es administrador"""
        return False

    def __str__(self) -> str:
        """devuelvo el texto con los datos principales del usuario"""
        return f'Usuario: {self.nombre}, email: {self.email}'


class Cliente(Usuario):
    """subclase para los clientes, anhado la direccion postal"""

    def __init__(self, nombre: str, email: str, direccion: str) -> None:
        """llamo al constructor del padre y anhado el atributo nuevo"""
        super().__init__(nombre, email)
        self.direccion: str = direccion

    def __str__(self) -> str:
        """cojo el str del padre y le anhado la direccion"""
        return f'{super().__str__()}, direccion: {self.direccion}'


class Administrador(Usuario):
    """subclase para los gestores de la tienda"""

    def is_admin(self) -> bool:
        """sobrescribo is_admin para que un administrador siempre de True"""
        return True