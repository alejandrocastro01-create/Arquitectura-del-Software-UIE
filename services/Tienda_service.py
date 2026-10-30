from typing import Dict, List, Optional, Tuple

from models.Producto import Producto
from models.Usuario import Usuario, Cliente, Administrador
from models.Pedido import Pedido
from services.excepciones import UsuarioNoEncontrado, ProductoNoEncontrado, UsuarioNoEsCliente, StockInsuficiente


class TiendaService:
    '''clase que hace de intermediaria entre los usuarios y los productos de la tienda'''

    def __init__(self) -> None:
        '''guardo los usuarios, los productos y los pedidos en diccionarios por id'''
        self.usuarios: Dict[str, Usuario] = {}
        self.productos: Dict[str, Producto] = {}
        self.pedidos: List[Pedido] = []

    def registrar_usuario(self, tipo: str, nombre: str, email: str, direccion: Optional[str] = None) -> Usuario:
        '''creo un cliente o un administrador segun el tipo que me pasen y lo guardo'''
        if tipo == 'cliente':
            usuario: Usuario = Cliente(nombre, email, direccion)
        elif tipo == 'administrador':
            usuario = Administrador(nombre, email)
        else:
            raise ValueError('el tipo de usuario tiene que ser cliente o administrador')
        self.usuarios[usuario.id] = usuario
        return usuario

    def obtener_usuario(self, id_usuario: str) -> Usuario:
        '''devuelvo el usuario con ese id, si no existe lanzo una excepcion'''
        usuario = self.usuarios.get(id_usuario)
        if usuario is None:
            raise UsuarioNoEncontrado('el usuario no existe')
        return usuario

    def listar_usuarios(self) -> List[Usuario]:
        '''devuelvo todos los usuarios registrados'''
        return list(self.usuarios.values())

    def anhadir_producto(self, producto: Producto) -> None:
        '''anhado al inventario un producto ya creado, de cualquier categoria'''
        self.productos[producto.id] = producto

    def obtener_producto(self, id_producto: str) -> Producto:
        '''devuelvo el producto con ese id, si no existe lanzo una excepcion'''
        producto = self.productos.get(id_producto)
        if producto is None:
            raise ProductoNoEncontrado('el producto no existe')
        return producto

    def eliminar_producto(self, id_producto: str) -> None:
        '''elimino un producto del inventario a partir de su id, si no existe lanzo una excepcion'''
        if id_producto not in self.productos:
            raise ProductoNoEncontrado('el producto no existe')
        del self.productos[id_producto]

    def listar_productos(self) -> List[Producto]:
        '''devuelvo todos los productos que tengo en la tienda'''
        return list(self.productos.values())

    def realizar_pedido(self, id_usuario: str, productos_solicitados: List[Tuple[str, int]]) -> Pedido:
        '''compruebo que el usuario existe y que hay stock suficiente antes de generar el pedido'''
        usuario = self.obtener_usuario(id_usuario)
        if not isinstance(usuario, Cliente):
            raise UsuarioNoEsCliente('solo los clientes pueden hacer pedidos')

        productos_pedido: List[Tuple[Producto, int]] = []
        # voy sumando lo pedido de cada producto por si aparece en varias lineas
        reservado: Dict[str, int] = {}
        for id_producto, cantidad in productos_solicitados:
            producto = self.obtener_producto(id_producto)
            total_pedido = reservado.get(id_producto, 0) + cantidad
            if not producto.hay_stock(total_pedido):
                raise StockInsuficiente(f'no hay stock suficiente de {producto.nombre}')
            reservado[id_producto] = total_pedido
            productos_pedido.append((producto, cantidad))

        for producto, cantidad in productos_pedido:
            producto.actualizar_stock(-cantidad)

        pedido = Pedido(usuario, productos_pedido)
        self.pedidos.append(pedido)
        return pedido

    def listar_pedidos_usuario(self, id_usuario: str) -> List[Pedido]:
        '''devuelvo los pedidos de un usuario, ordenados por fecha'''
        self.obtener_usuario(id_usuario)
        pedidos_usuario = [pedido for pedido in self.pedidos if pedido.cliente.id == id_usuario]
        pedidos_usuario.sort(key=lambda pedido: pedido.fecha)
        return pedidos_usuario
