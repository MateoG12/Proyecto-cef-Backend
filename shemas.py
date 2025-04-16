# Importamos pydantica
from pydantic import BaseModel
from datetime import date
from typing import List,Optional
#Creamos el la clase de equipo con baseModel para llamar todos los datos 


class Jugador(BaseModel):
    documento: int
    usuario: str
    password: str
    nombre: str
    apellidos: str
    edad: int
    fecha_nacimiento: date
    eps: str
    telefono: str
    email: str
    foto: str
    nombre_acudiente: str
    telefono_acudiente: str
    email_acudiente: str
    categoria: str

class DocumentoSchema(BaseModel):
    documento: int

class Login(BaseModel):
    Loginusuario:str
    password:str
    
class LoginUsuario(BaseModel):
    Loginusuario:str
    password:str

class VerificationCode(BaseModel):
    code: str
class VerificationCode2(BaseModel):
    code2: str
class CategoriaSchema(BaseModel):
    name: str
    players: List[str]


class UsuarioSchema(BaseModel):
    Documento: int
    correo_electronico: str  
    nombre: str
    password: str
    usuario: str
    telefono: str  
    rol: str
    foto: str
    inscripcion_documento: Optional[int] = None

class UsuarioSchemaActualizar(BaseModel):
    correo_electronico: str
    nombre: str
    usuario: str
    telefono: str
    rol: str
    foto: str

# Esquema para Equipo
class EquipoSchema(BaseModel):
    equipoid: Optional[int] = None
    nombre: str
    categoria: str
    fechacreacion: date
    usuario_id: int


# Esquema para Implementos
class ImplementosSchema(BaseModel):
    implementos: Optional[int] = None 
    cantidad: int
    descripcion: str
    nombre: str
    
#Esquemas para Prestar
class PrestarSchema(BaseModel):
    usuario_documento: int
    implementos_inventario_id: Optional[int] = None  
    cantidad: int
    fechadepresta: date
    estado: str
    

class PrestarSchemaActu(BaseModel):
    cantidad: int
    estado: str

class PagoSchema(BaseModel):
    pagos_id: Optional[int] = None 
    inscripcion_documento: Optional[int] = None  
    monto: int
    fecha: date
    categoria: str
    descripcion: str
    tipo: str

class EquipoInscripcionShema(BaseModel):
    equipoid:int
    documento:int



class TorneoSchema(BaseModel):
    torneo_id: Optional[int] = None 
    nombre: str
    tipo: str
    ubicacion: str


class EncuentroBase(BaseModel):
    equipo_equipoid: int
    fecha: date
    torneo_torneo_id: int
    encuentroscol: str
    hora: str
    resultado: str
    tipo: str
    ubicacion: str

class EncuentroBase2(BaseModel):
    Encuentro_id:Optional[int] = None 
    equipo_equipoid: int
    fecha: date
    torneo_torneo_id: int
    encuentroscol: str
    hora: str
    resultado: str
    tipo: str
    ubicacion: str


class EstadisticasBase(BaseModel):
    id:Optional[int] = None 
    asistencias: int
    corners: int
    encuentros_encuentro_id:int
    faltas: int
    goles: int
    penales: int
    tarjetasamarillas: int
    tarjetasrojas: int
    tirolibres: int