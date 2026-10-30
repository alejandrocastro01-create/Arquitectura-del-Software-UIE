class UsuarioNoEncontrado(Exception):
    '''excepcion para cuando busco un usuario que no existe'''


class ProductoNoEncontrado(Exception):
    '''excepcion para cuando busco un producto que no existe'''


class UsuarioNoEsCliente(Exception):
    '''excepcion para cuando un usuario que no es cliente intenta hacer un pedido'''


class StockInsuficiente(Exception):
    '''excepcion para cuando no hay stock suficiente para cubrir una linea del pedido'''
