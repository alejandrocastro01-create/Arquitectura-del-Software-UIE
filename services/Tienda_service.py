from typing import Dict, List, Optional, Tuple

from models.Producto import Producto
from models.Usuario import Usuario, Cliente, Administrador
from models.Pedido import Pedido


class TiendaService:
    """clase que hace de intermediaria entre los usuarios y los productos de la tienda"""

    def __init__(self) -> None:
        """guardo los usuarios, los productos y los pedidos en diccionarios por id"""
        self.usuarios: Dict[str, Usuario] = {}
        self.productos: Dict[str, Producto] = {}
        self.pedidos: List[Pedido] = []

    def registrar_usuario(self, tipo: str, nombre: str, email: str, direccion: Optional[str] = None) -> Usuario:
        """creo un cliente o un administrador segun el tipo que me pasen y lo guardo"""
        if tipo == 'cliente':
            usuario: Usuario = Cliente(nombre, email, direccion)
        elif tipo == 'administrador':
            usuario = Administrador(nombre, email)
        else:
            raise ValueError('el tipo de usuario tiene que ser cliente o administrador')
        self.usuarios[usuario.id] = usuario
        return usuario

    def anhadir_producto(self, producto: Producto) -> None:
        """anhado al inventario un producto ya creado, de cualquier categoria"""
        self.productos[producto.id] = producto

    def eliminar_producto(self, id_producto: str) -> None:
        """elimino un producto del inventario a partir de su id"""
        if id_producto in self.productos:
            del self.productos[id_producto]

    def listar_productos(self) -> List[Producto]:
        """devuelvo todos los productos que tengo en la tienda"""
        return list(self.productos.values())

    def realizar_pedido(self, id_usuario: str, productos_solicitados: List[Tuple[str, int]]) -> Optional[Pedido]:
        """compruebo que el usuario existe y que hay stock suficiente antes de generar el pedido"""
        usuario = self.usuarios.get(id_usuario)
        if usuario is None or not isinstance(usuario, Cliente):
            return None

        productos_pedido: List[Tuple[Producto, int]] = []
        for id_producto, cantidad in productos_solicitados:
            producto = self.productos.get(id_producto)
            if producto is None or not producto.hay_stock(cantidad):
                return None
            productos_pedido.append((producto, cantidad))

        for producto, cantidad in productos_pedido:
            producto.actualizar_stock(-cantidad)

        pedido = Pedido(usuario, productos_pedido)
        self.pedidos.append(pedido)
        return pedido

    def listar_pedidos_usuario(self, id_usuario: str) -> List[Pedido]:
        """devuelvo los pedidos de un usuario, ordenados por fecha"""
        pedidos_usuario = [pedido for pedido in self.pedidos if pedido.cliente.id == id_usuario]
        pedidos_usuario.sort(key=lambda pedido: pedido.fecha)
        return pedidos_usuario