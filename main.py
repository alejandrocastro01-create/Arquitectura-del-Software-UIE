from models.Producto import ProductoElectronico, ProductoRopa
from services.Tienda_service import TiendaService


def main() -> None:
    """pruebo aqui el funcionamiento de toda la tienda desde consola"""
    tienda = TiendaService()

    # registro tres clientes y un administrador
    cliente1 = tienda.registrar_usuario('cliente', 'Alex', 'alejandro.castro.01@uie,edu', 'Calle Real 1')
    cliente2 = tienda.registrar_usuario('cliente', 'Manuel', 'manuel.lopez2@uie.edu', 'Rúa Nova 5')
    cliente3 = tienda.registrar_usuario('cliente', 'Juan', 'juan.garcia.01@uie.edu', 'Avenida Fisterra 10')
    tienda.registrar_usuario('administrador', 'Administrador', 'administrador@uie.edu')

    # creo cinco productos de categorias distintas y los anhado al inventario
    producto1 = ProductoElectronico('Portatil', 800.0, 10, 24)
    producto2 = ProductoElectronico('Cascos', 50.0, 20, 12)
    producto3 = ProductoRopa('Camiseta', 15.0, 30, 'M', 'azul')
    producto4 = ProductoRopa('Pantalones', 25.0, 15, 'L', 'negro')
    producto5 = ProductoElectronico('Raton', 20.0, 25, 6)

    for producto in [producto1, producto2, producto3, producto4, producto5]:
        tienda.anhadir_producto(producto)

    # listo los productos para comprobar que el inventario se ha llenado bien
    print('Productos en la tienda:')
    for producto in tienda.listar_productos():
        print(producto)

    # simulo tres pedidos hechos por clientes distintos
    pedido1 = tienda.realizar_pedido(cliente1.id, [(producto1.id, 1), (producto3.id, 2)])
    pedido2 = tienda.realizar_pedido(cliente2.id, [(producto2.id, 3)])
    pedido3 = tienda.realizar_pedido(cliente3.id, [(producto4.id, 1), (producto5.id, 2)])

    print('\nPedidos realizados:')
    for pedido in [pedido1, pedido2, pedido3]:
        print(pedido)

    # compruebo el stock actualizado despues de los pedidos
    print('\nStock actualizado:')
    for producto in tienda.listar_productos():
        print(producto)

    # compruebo el historico de pedidos de un cliente
    print(f'\nHistorico de pedidos de {cliente1.nombre}:')
    for pedido in tienda.listar_pedidos_usuario(cliente1.id):
        print(pedido)


if __name__ == '__main__':
    main()