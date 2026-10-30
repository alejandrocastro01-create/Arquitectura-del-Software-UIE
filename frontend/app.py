#Autor: Alejandro Castro Rodriguez
#Frontend de la tienda hecho en Python con Streamlit. No importa nada del servidor, todo va por peticiones HTTP
#Se arranca con: python -m streamlit run frontend_python/app.py
#Importacion de librerias
import requests
import streamlit as st

#Direccion base de la API por defecto, se cambia en la caja de arriba de la pagina
#Pongo 127.0.0.1 y no localhost porque en Windows localhost tarda 2 segundos en cada peticion
#(primero lo intenta por IPv6 y uvicorn solo escucha en IPv4), y la pagina hace varias peticiones cada vez
BASE_URL= 'http://127.0.0.1:8000'

#Segundos que espero como maximo a que la API responda
TIEMPO_ESPERA= 10


#Funciones auxiliares
def sacar_error(respuesta: requests.Response) -> str:
    '''saco el detail del error que devuelve la API, si no hay devuelvo el texto tal cual'''
    try:
        datos= respuesta.json()
    except ValueError:
        return f'Error {respuesta.status_code}: {respuesta.text}'
    if 'detail' not in datos:
        return f'Error {respuesta.status_code}: {respuesta.text}'
    detalle= datos['detail']
    #Si el error lo pone pydantic (422) el detail es una lista, me quedo con el mensaje de cada error
    if isinstance(detalle, list):
        mensajes= []
        for error in detalle:
            mensajes.append(str(error.get('loc', '')) + ' ' + str(error.get('msg', '')))
        detalle= ', '.join(mensajes)
    return f'Error {respuesta.status_code}: {detalle}'


def comprobar(respuesta: requests.Response, codigo_esperado: int):
    '''compruebo el codigo de estado http y devuelvo (True, json) si va bien o (False, mensaje) si no'''
    if respuesta.status_code != codigo_esperado:
        return False, sacar_error(respuesta)
    return True, respuesta.json()


#Funciones que hacen las peticiones, una por cada endpoint (igual que en cliente.py)
def crear_usuario(nombre: str, email: str, tipo: str, direccion: str = None):
    '''POST /usuarios, creo un usuario y devuelvo el usuario creado'''
    datos= {'nombre': nombre, 'email': email, 'tipo': tipo, 'direccion': direccion}
    respuesta= requests.post(f'{BASE_URL}/usuarios', json=datos, timeout=TIEMPO_ESPERA)
    return comprobar(respuesta, 201)


def listar_usuarios():
    '''GET /usuarios, devuelvo la lista de usuarios'''
    respuesta= requests.get(f'{BASE_URL}/usuarios', timeout=TIEMPO_ESPERA)
    return comprobar(respuesta, 200)


def crear_producto(tipo: str, nombre: str, precio: float, stock: int,
                   meses_garantia: int = None, talla: str = None, color: str = None):
    '''POST /productos, creo un producto de cualquier tipo y devuelvo el producto creado'''
    datos= {'tipo': tipo, 'nombre': nombre, 'precio': precio, 'stock': stock,
            'meses_garantia': meses_garantia, 'talla': talla, 'color': color}
    respuesta= requests.post(f'{BASE_URL}/productos', json=datos, timeout=TIEMPO_ESPERA)
    return comprobar(respuesta, 201)


def listar_productos():
    '''GET /productos, devuelvo la lista de productos'''
    respuesta= requests.get(f'{BASE_URL}/productos', timeout=TIEMPO_ESPERA)
    return comprobar(respuesta, 200)


def crear_pedido(cliente_id: str, lineas: list):
    '''POST /pedidos, lineas es una lista de diccionarios con id_producto y cantidad'''
    datos= {'cliente_id': cliente_id, 'items': lineas}
    respuesta= requests.post(f'{BASE_URL}/pedidos', json=datos, timeout=TIEMPO_ESPERA)
    return comprobar(respuesta, 201)


def listar_pedidos_usuario(cliente_id: str):
    '''GET /usuarios/{cliente_id}/pedidos, devuelvo los pedidos de ese cliente'''
    respuesta= requests.get(f'{BASE_URL}/usuarios/{cliente_id}/pedidos', timeout=TIEMPO_ESPERA)
    return comprobar(respuesta, 200)


def hacer_peticion(funcion, *argumentos):
    '''llamo a una de las funciones de arriba y si la API no esta arrancada devuelvo el error en vez de romper'''
    try:
        return funcion(*argumentos)
    except requests.exceptions.ConnectionError:
        return False, f'No he podido conectar con la API en {BASE_URL}. Esta arrancada y la direccion es correcta?'
    except requests.exceptions.Timeout:
        return False, f'La API en {BASE_URL} ha tardado demasiado en responder'


#Funciones que pintan cada parte de la pagina
def pintar_productos():
    '''muestro el formulario para crear un producto y debajo la tabla de productos'''
    st.subheader('Crear producto')
    #El tipo lo pongo fuera del formulario para que los campos cambien nada mas elegirlo
    tipo= st.selectbox('Tipo de producto', ['generico', 'electronico', 'ropa'])
    with st.form('formulario_producto', clear_on_submit=True):
        nombre= st.text_input('Nombre')
        precio= st.number_input('Precio', min_value=0.0, step=0.5)
        stock= st.number_input('Stock', min_value=0, step=1)
        meses_garantia= None
        talla= None
        color= None
        #Solo pido los campos que lleva cada tipo
        if tipo == 'electronico':
            meses_garantia= st.number_input('Meses de garantia', min_value=0, step=1)
        if tipo == 'ropa':
            talla= st.text_input('Talla')
            color= st.text_input('Color')
        enviado= st.form_submit_button('Crear producto')

    if enviado:
        #El number_input puede devolver decimales, asi que paso a int lo que tiene que ser entero
        if meses_garantia is not None:
            meses_garantia= int(meses_garantia)
        ok, resultado= hacer_peticion(crear_producto, tipo, nombre, precio, int(stock), meses_garantia, talla, color)
        if ok:
            nombre= resultado['nombre']
            tipo= resultado['tipo']
            st.success(f'Producto creado: {nombre} ({tipo})')
        else:
            st.error(resultado)

    #Pinto la tabla despues del formulario para que ya salga el producto nuevo
    st.subheader('Productos de la tienda')
    ok, productos= hacer_peticion(listar_productos)
    if not ok:
        st.error(productos)
    elif len(productos) == 0:
        st.info('Todavia no hay productos')
    else:
        st.dataframe(productos)


def pintar_usuarios():
    '''muestro el formulario para crear un usuario y debajo la tabla de usuarios'''
    st.subheader('Crear usuario')
    tipo= st.selectbox('Tipo de usuario', ['cliente', 'administrador'])
    with st.form('formulario_usuario', clear_on_submit=True):
        nombre= st.text_input('Nombre')
        email= st.text_input('Email')
        direccion= None
        #La direccion solo la necesita un cliente
        if tipo == 'cliente':
            direccion= st.text_input('Direccion postal')
        enviado= st.form_submit_button('Crear usuario')

    if enviado:
        ok, resultado= hacer_peticion(crear_usuario, nombre, email, tipo, direccion)
        if ok:
            nombre= resultado['nombre']
            email= resultado['email']
            st.success(f'Usuario creado: {nombre} ({email})')
        else:
            st.error(resultado)

    #Pinto la tabla despues del formulario para que ya salga el usuario nuevo
    st.subheader('Usuarios registrados')
    ok, usuarios= hacer_peticion(listar_usuarios)
    if not ok:
        st.error(usuarios)
    elif len(usuarios) == 0:
        st.info('Todavia no hay usuarios')
    else:
        st.dataframe(usuarios)


def pintar_crear_pedido():
    '''muestro el formulario para hacer un pedido eligiendo cliente y lineas de producto y cantidad'''
    st.subheader('Crear pedido')
    ok_usuarios, usuarios= hacer_peticion(listar_usuarios)
    ok_productos, productos= hacer_peticion(listar_productos)
    if not ok_usuarios:
        st.error(usuarios)
        return
    if not ok_productos:
        st.error(productos)
        return
    if len(usuarios) == 0 or len(productos) == 0:
        st.info('Para hacer un pedido primero tiene que haber usuarios y productos')
        return

    #Guardo el texto que se ve en la lista y el id que le corresponde
    opciones_usuarios= {}
    for usuario in usuarios:
        nombre= usuario['nombre']
        email= usuario['email']
        opciones_usuarios[f'{nombre} ({email})']= usuario['id']
    opciones_productos= {}
    for producto in productos:
        nombre= producto['nombre']
        precio= producto['precio']
        #No pongo el stock en el texto porque cambia con cada pedido y el selectbox perderia lo elegido
        #Pongo el principio del id para que dos productos con el mismo nombre no se pisen en el diccionario
        id_corto= producto['id'][:8]
        texto= f'{nombre} - {precio} euros ({id_corto})'
        opciones_productos[texto]= producto['id']

    cliente= st.selectbox('Cliente', list(opciones_usuarios.keys()))
    numero_lineas= st.number_input('Numero de lineas del pedido', min_value=1, max_value=10, step=1)

    lineas= []
    for i in range(int(numero_lineas)):
        columna1, columna2= st.columns([3, 1])
        with columna1:
            producto= st.selectbox(f'Producto de la linea {i + 1}', list(opciones_productos.keys()),
                                   key=f'producto_{i}')
        with columna2:
            cantidad= st.number_input('Cantidad', min_value=1, step=1, key=f'cantidad_{i}')
        lineas.append({'id_producto': opciones_productos[producto], 'cantidad': int(cantidad)})

    if st.button('Hacer pedido'):
        ok, pedido= hacer_peticion(crear_pedido, opciones_usuarios[cliente], lineas)
        if ok:
            total= pedido['total']
            st.success(f'Pedido creado, total: {total} euros')
            pintar_pedido(pedido)
        else:
            st.error(pedido)


def pintar_pedido(pedido: dict):
    '''muestro un pedido con su fecha, su total y una tabla con sus lineas'''
    #La fecha viene como 2026-10-23T16:57:05.953273, me quedo con la fecha y la hora sin la T
    fecha= pedido['fecha'][:19].replace('T', ' ')
    total= pedido['total']
    st.write(f'Pedido del {fecha}, total: {total} euros')
    st.table(pedido['items'])


def pintar_pedidos_usuario():
    '''muestro el historial de pedidos del usuario que se elija'''
    st.subheader('Pedidos de un usuario')
    ok, usuarios= hacer_peticion(listar_usuarios)
    if not ok:
        st.error(usuarios)
        return
    if len(usuarios) == 0:
        st.info('Todavia no hay usuarios')
        return

    opciones_usuarios= {}
    for usuario in usuarios:
        nombre= usuario['nombre']
        email= usuario['email']
        opciones_usuarios[f'{nombre} ({email})']= usuario['id']
    usuario=st.selectbox('Usuario', list(opciones_usuarios.keys()), key='usuario_historial')

    ok, pedidos= hacer_peticion(listar_pedidos_usuario, opciones_usuarios[usuario])
    if not ok:
        st.error(pedidos)
    elif len(pedidos) == 0:
        st.info('Este usuario no tiene pedidos')
    else:
        for pedido in pedidos:
            pintar_pedido(pedido)


#Pagina principal
st.set_page_config(page_title='Tienda online')
st.title('Tienda online - Practica 2')
#Dejo cambiar la direccion de la API desde arriba de la pagina, asi sirve para otro equipo de la red
BASE_URL= st.text_input('Direccion de la API', BASE_URL).rstrip('/')

pestanha_productos, pestanha_usuarios, pestanha_pedido, pestanha_historial= st.tabs(
    ['Productos', 'Usuarios', 'Crear pedido', 'Pedidos de un usuario'])
with pestanha_productos:
    pintar_productos()
with pestanha_usuarios:
    pintar_usuarios()
with pestanha_pedido:
    pintar_crear_pedido()
with pestanha_historial:
    pintar_pedidos_usuario()
