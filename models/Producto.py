import uuid


class Producto:
    """clase padre para todos los productos de la tienda"""

    def __init__(self, nombre: str, precio: float, stock: int) -> None:
        """el id lo genero yo solo con uuid, no lo paso como parametro"""
        self.id: str = str(uuid.uuid4())
        self.nombre: str = nombre
        self.precio: float = precio
        self.stock: int = stock

    def hay_stock(self, cantidad: int) -> bool:
        """compruebo si el stock que tengo alcanza para la cantidad pedida"""
        return self.stock >= cantidad

    def actualizar_stock(self, cantidad: int) -> None:
        """si la cantidad es positiva repongo stock, si es negativa la descuento por una compra"""
        self.stock += cantidad

    def __str__(self) -> str:
        """devuelvo el texto con los datos principales del producto"""
        return f'Producto: {self.nombre}, precio: {self.precio}, stock: {self.stock}'


class ProductoElectronico(Producto):
    """subclase para los productos electronicos, anhado la garantia"""

    def __init__(self, nombre: str, precio: float, stock: int, meses_garantia: int) -> None:
        """llamo al constructor del padre y anhado el atributo nuevo"""
        super().__init__(nombre, precio, stock)
        self.meses_garantia: int = meses_garantia

    def __str__(self) -> str:
        """cojo el str del padre y le anhado la garantia"""
        return f'{super().__str__()}, garantia: {self.meses_garantia} meses'


class ProductoRopa(Producto):
    """subclase para la ropa, anhado talla y color"""

    def __init__(self, nombre: str, precio: float, stock: int, talla: str, color: str) -> None:
        """llamo al constructor del padre y anhado los atributos nuevos"""
        super().__init__(nombre, precio, stock)
        self.talla: str = talla
        self.color: str = color

    def __str__(self) -> str:
        """cojo el str del padre y le anhado talla y color"""
        return f'{super().__str__()}, talla: {self.talla}, color: {self.color}'