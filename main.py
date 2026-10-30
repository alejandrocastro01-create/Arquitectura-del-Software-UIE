#Autor: Alejandro Castro Rodriguez
#Importacion de librerias
from typing import List
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from esquemas import (CreacionUsuario, LeerUsuario, CreacionProducto, LeerProducto,
                      CreacionPedido, LeerPedido, LeerPedidoItem)
from models.Producto import Producto, ProductoElectronico, ProductoRopa
from models.Usuario import Usuario
from models.Pedido import Pedido
from services.Tienda_service import TiendaService
from services.excepciones import UsuarioNoEncontrado, ProductoNoEncontrado, UsuarioNoEsCliente, StockInsuficiente

#Creo la propia aplicacion y la guardo en una variabble
#Le pongo titulo, descripcion y version para que se vean arriba en /docs
app=FastAPI(title='Tienda online', description='API de la tienda online de la Practica 2: usuarios, productos y pedidos',
            version='2.0')
#Permito que el frontend, abierto desde otro origen, pueda hacer peticiones a la API (CORS)
app.add_middleware(CORSMiddleware, allow_origins=['*'], allow_methods=['*'], allow_headers=['*'])
#Guardo un unico servicio global para que todas las peticiones compartan los datos en memoria
tienda= TiendaService()


#Funciones auxiliares para pasar de los modelos a los esquemas
def a_leer_usuario(usuario: Usuario) -> LeerUsuario:
    '''paso un usuario del modelo al esquema de lectura'''
    return LeerUsuario(id=usuario.id, nombre=usuario.nombre, email=usuario.email, es_admin=usuario.is_admin())


def a_leer_producto(producto: Producto) -> LeerProducto:
    '''paso un producto del modelo al esquema de lectura, calculando su tipo segun la clase'''
    if isinstance(producto, ProductoElectronico):
        tipo = 'electronico'
    elif isinstance(producto, ProductoRopa):
        tipo = 'ropa'
    else:
        tipo = 'generico'
    return LeerProducto(id=producto.id, tipo=tipo, nombre=producto.nombre, precio=producto.precio,
                        stock=producto.stock,
                        meses_garantia=getattr(producto, 'meses_garantia', None),
                        talla=getattr(producto, 'talla', None),
                        color=getattr(producto, 'color', None))


def a_leer_pedido(pedido: Pedido) -> LeerPedido:
    '''paso un pedido del modelo al esquema de lectura, con una linea por cada producto'''
    items = [LeerPedidoItem(id_producto=producto.id, nombre=producto.nombre, precio_unitario=producto.precio,
                            cantidad=cantidad, subtotal=producto.precio * cantidad)
             for producto, cantidad in pedido.productos]
    return LeerPedido(id=pedido.id, fecha=pedido.fecha, cliente=a_leer_usuario(pedido.cliente),
                      total=pedido.calcular_total(), items=items)


#Defino la propia ruta de la aplicacion
@app.get('/', tags=['Raiz'])
def raiz():
    return {'mensaje': 'La tienda online funciona'}


#Endpoints de usuarios
@app.post('/usuarios', response_model=LeerUsuario, status_code=201, tags=['Usuarios'])
def crear_usuario(datos: CreacionUsuario):
    '''creo un usuario, un cliente tiene que traer su direccion postal'''
    if datos.tipo == 'cliente' and not datos.direccion:
        raise HTTPException(status_code=422, detail='un cliente tiene que tener direccion')
    usuario = tienda.registrar_usuario(datos.tipo, datos.nombre, datos.email, datos.direccion)
    return a_leer_usuario(usuario)


@app.get('/usuarios', response_model=List[LeerUsuario], tags=['Usuarios'])
def listar_usuarios():
    '''devuelvo todos los usuarios registrados'''
    return [a_leer_usuario(usuario) for usuario in tienda.listar_usuarios()]


@app.get('/usuarios/{usuario_id}', response_model=LeerUsuario, tags=['Usuarios'],
         responses={404: {'description': 'El usuario no existe'}})
def obtener_usuario(usuario_id: str):
    '''devuelvo un usuario concreto, 404 si no existe'''
    try:
        usuario = tienda.obtener_usuario(usuario_id)
    except UsuarioNoEncontrado as error:
        raise HTTPException(status_code=404, detail=str(error))
    return a_leer_usuario(usuario)


#Endpoints de productos
@app.post('/productos', response_model=LeerProducto, status_code=201, tags=['Productos'])
def crear_producto(datos: CreacionProducto):
    '''creo un producto validando que los atributos encajan con su tipo'''
    if datos.tipo == 'electronico':
        if datos.meses_garantia is None or datos.meses_garantia < 0:
            raise HTTPException(status_code=422, detail='un producto electronico necesita meses_garantia (0 o mas)')
        if datos.talla is not None or datos.color is not None:
            raise HTTPException(status_code=422, detail='un producto electronico no lleva talla ni color')
        producto: Producto = ProductoElectronico(datos.nombre, datos.precio, datos.stock, datos.meses_garantia)
    elif datos.tipo == 'ropa':
        if not datos.talla or not datos.color:
            raise HTTPException(status_code=422, detail='un producto de ropa necesita talla y color')
        if datos.meses_garantia is not None:
            raise HTTPException(status_code=422, detail='un producto de ropa no lleva meses_garantia')
        producto = ProductoRopa(datos.nombre, datos.precio, datos.stock, datos.talla, datos.color)
    else:
        if datos.meses_garantia is not None or datos.talla is not None or datos.color is not None:
            raise HTTPException(status_code=422, detail='un producto generico no lleva atributos adicionales')
        producto = Producto(datos.nombre, datos.precio, datos.stock)
    tienda.anhadir_producto(producto)
    return a_leer_producto(producto)


@app.get('/productos', response_model=List[LeerProducto], tags=['Productos'])
def listar_productos():
    '''devuelvo todos los productos de la tienda'''
    return [a_leer_producto(producto) for producto in tienda.listar_productos()]


@app.get('/productos/{producto_id}', response_model=LeerProducto, tags=['Productos'],
         responses={404: {'description': 'El producto no existe'}})
def obtener_producto(producto_id: str):
    '''devuelvo un producto concreto, 404 si no existe'''
    try:
        producto = tienda.obtener_producto(producto_id)
    except ProductoNoEncontrado as error:
        raise HTTPException(status_code=404, detail=str(error))
    return a_leer_producto(producto)


@app.delete('/productos/{producto_id}', status_code=204, tags=['Productos'],
            responses={404: {'description': 'El producto no existe'}})
def eliminar_producto(producto_id: str):
    '''elimino un producto, 404 si no existe y 204 sin contenido si todo va bien'''
    try:
        tienda.eliminar_producto(producto_id)
    except ProductoNoEncontrado as error:
        raise HTTPException(status_code=404, detail=str(error))


#Endpoints de pedidos
@app.post('/pedidos', response_model=LeerPedido, status_code=201, tags=['Pedidos'],
          responses={400: {'description': 'El usuario no es cliente o no hay stock suficiente'},
                     404: {'description': 'El cliente o algun producto no existen'}})
def crear_pedido(datos: CreacionPedido):
    '''creo un pedido: 404 si el cliente o un producto no existen, 400 si no es cliente o falta stock'''
    lineas = [(item.id_producto, item.cantidad) for item in datos.items]
    try:
        pedido = tienda.realizar_pedido(datos.cliente_id, lineas)
    except (UsuarioNoEncontrado, ProductoNoEncontrado) as error:
        raise HTTPException(status_code=404, detail=str(error))
    except (UsuarioNoEsCliente, StockInsuficiente) as error:
        raise HTTPException(status_code=400, detail=str(error))
    return a_leer_pedido(pedido)


@app.get('/usuarios/{cliente_id}/pedidos', response_model=List[LeerPedido], tags=['Pedidos'],
         responses={404: {'description': 'El cliente no existe'}})
def listar_pedidos_cliente(cliente_id: str):
    '''devuelvo los pedidos de un cliente, 404 si el cliente no existe'''
    try:
        pedidos = tienda.listar_pedidos_usuario(cliente_id)
    except UsuarioNoEncontrado as error:
        raise HTTPException(status_code=404, detail=str(error))
    return [a_leer_pedido(pedido) for pedido in pedidos]
