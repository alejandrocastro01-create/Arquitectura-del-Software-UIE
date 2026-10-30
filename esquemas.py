#Importacion de las librerias
from typing import Literal, Optional, List
from pydantic import BaseModel, EmailStr, Field
from datetime import datetime


#Creacion de clases
class CreacionUsuario(BaseModel):
    nombre:str
    email: EmailStr
    tipo: Literal['cliente', 'administrador']
    direccion: Optional[str] = None

class LeerUsuario(BaseModel):
    id:str
    nombre:str
    email:str
    es_admin: bool

class CreacionProducto(BaseModel):
    tipo: Literal['generico','electronico','ropa']
    nombre: str
    precio: float=Field(gt=0)
    stock: int=Field(ge=0)
    meses_garantia: Optional[int]= None
    talla: Optional[str]= None 
    color: Optional[str]= None

class LeerProducto(BaseModel):
    id: str
    tipo: str
    nombre: str
    precio: float
    stock: int
    meses_garantia: Optional[int]= None
    talla: Optional[str]= None 
    color: Optional[str]= None

class CreacionPedidoItem(BaseModel):
    id_producto: str
    cantidad: int=Field(gt=0)

class LeerPedidoItem(BaseModel):
    id_producto: str
    nombre: str
    precio_unitario: float
    cantidad: int
    subtotal: float

class CreacionPedido(BaseModel):
    cliente_id: str
    items: List[CreacionPedidoItem]=Field(min_length=1)

class LeerPedido(BaseModel):
    id: str
    fecha: datetime
    cliente: LeerUsuario
    total: float
    items: List[LeerPedidoItem]

