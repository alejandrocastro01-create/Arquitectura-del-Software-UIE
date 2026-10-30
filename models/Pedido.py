from datetime import datetime
from typing import List, Tuple
import uuid

from .Producto import Producto
from .Usuario import Cliente


class Pedido:
    """clase para representar un pedido que hace un cliente"""

    def __init__(self, cliente: Cliente, productos: List[Tuple[Producto, int]]) -> None:
        """el id y la fecha los genero yo solo, productos es una lista de tuplas de producto y cantidad"""
        self.id: str = str(uuid.uuid4())
        self.cliente: Cliente = cliente
        self.productos: List[Tuple[Producto, int]] = productos
        self.fecha: datetime = datetime.now()

    def calcular_total(self) -> float:
        """sumo el precio por la cantidad de cada producto que hay en el pedido"""
        total: float = 0.0
        for producto, cantidad in self.productos:
            total += producto.precio * cantidad
        return total

    def __str__(self) -> str:
        """devuelvo un resumen legible del pedido, con el nombre del cliente y el total"""
        return f'Pedido de {self.cliente.nombre}, total: {self.calcular_total()}€, fecha: {self.fecha}'