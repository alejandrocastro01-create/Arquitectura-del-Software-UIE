#Autor: Alejandro Castro Rodriguez
#Cliente de la API de la tienda. No importa nada del servidor, todo va por peticiones HTTP
#Importacion de librerias
import os
import sys
import requests

#Direccion base de la API, se puede cambiar con un argumento o con la variable de entorno BASE_URL
#Ejemplos: python cliente.py http://192.168.1.34:8000
if len(sys.argv) > 1:
    BASE_URL = sys.argv[1]
else:
    BASE_URL = os.environ.get('BASE_URL', 'http://localhost:8000')
BASE_URL = BASE_URL.rstrip('/')

#Segundos que espero como maximo a que la API responda
TIEMPO_ESPERA = 10


def comprobar(respuesta: requests.Response, codigo_esperado: int):
    '''compruebo el codigo de estado http y devuelvo el json de la respuesta'''
    if respuesta.status_code != codigo_esperado:
        raise RuntimeError(f'{respuesta.request.method} {respuesta.url}: esperaba {codigo_esperado} '
                           f'y recibi {respuesta.status_code} -> {respuesta.text}')
    if respuesta.status_code == 204:
        return None
    return respuesta.json()


def crear_usuario(nombre: str, email: str, tipo: str, direccion: str = None) -> dict:
    '''POST /usuarios, creo un usuario y devuelvo el usuario creado'''
    datos = {'nombre': nombre, 'email': email, 'tipo': tipo, 'direccion': direccion}
    respuesta = requests.post(f'{BASE_URL}/usuarios', json=datos, timeout=TIEMPO_ESPERA)
    return comprobar(respuesta, 201)


def listar_usuarios() -> list:
    '''GET /usuarios, devuelvo la lista de usuarios'''
    respuesta = requests.get(f'{BASE_URL}/usuarios', timeout=TIEMPO_ESPERA)
    return comprobar(respuesta, 200)


def crear_producto(tipo: str, nombre: str, precio: float, stock: int,
                   meses_garantia: int = None, talla: str = None, color: str = None) -> dict:
    '''POST /productos, creo un producto de cualquier tipo y devuelvo el producto creado'''
    datos = {'tipo': tipo, 'nombre': nombre, 'precio': precio, 'stock': stock,
             'meses_garantia': meses_garantia, 'talla': talla, 'color': color}
    respuesta = requests.post(f'{BASE_URL}/productos', json=datos, timeout=TIEMPO_ESPERA)
    return comprobar(respuesta, 201)


def listar_productos() -> list:
    '''GET /productos, devuelvo la lista de productos'''
    respuesta = requests.get(f'{BASE_URL}/productos', timeout=TIEMPO_ESPERA)
    return comprobar(respuesta, 200)


def crear_pedido(cliente_id: str, items: list, codigo_esperado: int = 201) -> dict:
    '''POST /pedidos, items es una lista de (id_producto, cantidad), devuelvo el pedido creado'''
    datos = {'cliente_id': cliente_id,
             'items': [{'id_producto': id_producto, 'cantidad': cantidad} for id_producto, cantidad in items]}
    respuesta = requests.post(f'{BASE_URL}/pedidos', json=datos, timeout=TIEMPO_ESPERA)
    return comprobar(respuesta, codigo_esperado)


def listar_pedidos_usuario(cliente_id: str) -> list:
    '''GET /usuarios/{cliente_id}/pedidos, devuelvo los pedidos de ese cliente'''
    respuesta = requests.get(f'{BASE_URL}/usuarios/{cliente_id}/pedidos', timeout=TIEMPO_ESPERA)
    return comprobar(respuesta, 200)


def main() -> None:
    '''pruebo el flujo basico de la tienda usando solo la API'''
    print(f'Usando la API en {BASE_URL}')

    # creo un cliente y un administrador
    cliente = crear_usuario('Alex', 'alejandro.castro.01@uie.edu', 'cliente', 'Calle Real 1')
    print('\nUsuario creado:', cliente)
    crear_usuario('Administrador', 'administrador@uie.edu', 'administrador')

    print('\nUsuarios registrados:')
    for usuario in listar_usuarios():
        nombre = usuario['nombre']
        email = usuario['email']
        es_admin = usuario['es_admin']
        print(f'- {nombre} ({email}), admin: {es_admin}')

    # creo un producto de cada tipo
    portatil = crear_producto('electronico', 'Portatil', 800.0, 10, meses_garantia=24)
    camiseta = crear_producto('ropa', 'Camiseta', 15.0, 30, talla='M', color='azul')
    taza = crear_producto('generico', 'Taza', 4.5, 50)
    print('\nProductos creados:', portatil['nombre'], camiseta['nombre'], taza['nombre'])

    print('\nProductos en la tienda:')
    for producto in listar_productos():
        nombre = producto['nombre']
        tipo = producto['tipo']
        precio = producto['precio']
        stock = producto['stock']
        print(f'- {nombre} ({tipo}), precio: {precio}, stock: {stock}')

    # hago un pedido correcto y compruebo el total
    pedido = crear_pedido(cliente['id'], [(portatil['id'], 1), (camiseta['id'], 2)])
    total = pedido['total']
    print(f'\nPedido creado, total: {total}')
    assert pedido['total'] == 830.0, 'el total del pedido no es el esperado'

    # intento un pedido con demasiada cantidad, la API tiene que responder 400
    crear_pedido(cliente['id'], [(portatil['id'], 999)], codigo_esperado=400)
    print('Pedido sin stock rechazado con 400, como esperaba')

    nombre_cliente = cliente['nombre']
    print(f'\nPedidos de {nombre_cliente}:')
    for pedido in listar_pedidos_usuario(cliente['id']):
        fecha = pedido['fecha']
        numero_lineas = len(pedido['items'])
        total = pedido['total']
        print(f'- {fecha}: {numero_lineas} lineas, total {total}')


if __name__ == '__main__':
    try:
        main()
    except requests.exceptions.ConnectionError:
        print(f'No he podido conectar con la API en {BASE_URL}. Esta arrancada y la direccion es correcta?')
        sys.exit(1)
    except RuntimeError as error:
        print('Error en la respuesta de la API:', error)
        sys.exit(1)
