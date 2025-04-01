from sqlalchemy import create_engine, Column, String, Integer, ForeignKey, DateTime, Date, Double, Boolean
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy.ext.declarative import declarative_base

base = declarative_base()

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

base = declarative_base()

class Inscripcion(base):
    __tablename__ = 'inscripcion'
    
    documento = Column(Integer, primary_key=True)
    edad = Column(Integer, nullable=False)
    fecha_nacimiento = Column(DateTime, nullable=False)
    apellidos = Column(String(100), nullable=False)
    categoria = Column(String(100), nullable=False)
    email = Column(String(100), nullable=False)
    email_acudiente = Column(String(100), nullable=False)
    eps = Column(String(100), nullable=False)
    foto = Column(String(100), nullable=False)
    nombre = Column(String(100), nullable=False)
    nombre_acudiente = Column(String(100), nullable=False)
    password = Column(String(100), nullable=False)
    telefono = Column(String(100), nullable=False)
    telefono_acudiente = Column(String(100), nullable=False)
    usuario = Column(String(100), nullable=False)

    # Relaciones
    usuarios = relationship("Usuario", back_populates="inscripcion")
    pagos = relationship("Pagos", back_populates="inscripcion", cascade="all, delete-orphan")
    asistencias = relationship("Asistencia", back_populates="inscripcion")
    equipos_inscripcion = relationship(
        "EquipoInscripcion", 
        back_populates="inscripcion",
        cascade="all, delete-orphan",  # Agregar acción de cascada, por ejemplo, "all" o "delete-orphan"
        foreign_keys="[EquipoInscripcion.documento]"  # Especificar la clave foránea explícitamente
    )

class Equipo(base):
    __tablename__ = 'equipo'
    
    equipoid = Column(Integer, primary_key=True,autoincrement=True)
    fechacreacion = Column(DateTime, nullable=False)
    categoria = Column(String(100), nullable=False)
    nombre = Column(String(100), nullable=False)
    usuario_id = Column(Integer, ForeignKey('usuario.Documento'))

    # Relación con Usuario
    usuario = relationship("Usuario", back_populates="equipos")
    encuentros = relationship("Encuentros", back_populates="equipo")
    inscripciones = relationship("EquipoInscripcion", back_populates="equipo", cascade="all, delete-orphan")

class EquipoInscripcion(base):
    __tablename__ = 'equipo_inscripcion'
    
    equipoid = Column(Integer, ForeignKey('equipo.equipoid'), primary_key=True)
    documento = Column(Integer, ForeignKey('inscripcion.documento'), primary_key=True)

    # Relaciones con las tablas 'Equipo' e 'Inscripción'
    equipo = relationship("Equipo", back_populates="inscripciones")
    inscripcion = relationship("Inscripcion", back_populates="equipos_inscripcion")


class Usuario(base):
    __tablename__ = 'usuario'
    
    Documento = Column(Integer, primary_key=True)
    correo_electronico = Column(String(45), nullable=False)
    nombre = Column(String(45), nullable=False)
    password = Column(String(100), nullable=False)
    usuario = Column(String(45), nullable=False)
    telefono = Column(String(45), nullable=False)
    rol = Column(String(45), nullable=False)
    foto = Column(String(45), nullable=False)
    inscripcion_documento = Column(Integer, ForeignKey('inscripcion.documento'),nullable=True)

    inscripcion = relationship("Inscripcion", back_populates="usuarios")
    equipos = relationship("Equipo", back_populates="usuario", cascade="all, delete-orphan")
    prestamos = relationship("Prestar", back_populates="usuario", cascade="all, delete-orphan")



# Clase Encuentros
class Encuentros(base):
    __tablename__ = 'encuentros'

    Encuentro_id = Column(Integer, primary_key=True, autoincrement=True)
    fecha = Column(DateTime, nullable=False)
    hora = Column(String(100), nullable=False)
    resultado = Column(String(100), nullable=False)
    ubicacion = Column(String(100), nullable=False)
    tipo = Column(String(45), nullable=False)
    encuentroscol = Column(String(45), nullable=False)

    # Agregar la clave foránea a la tabla Torneo
    torneo_torneo_id = Column(Integer, ForeignKey('torneo.torneo_id'))  # Clave foránea a Torneo

    # Relaciones con otras tablas
    equipo_equipoid = Column(Integer, ForeignKey('equipo.equipoid'))  # Relación con la tabla Equipo
    equipo = relationship("Equipo", back_populates="encuentros", single_parent=True)
    
    torneo = relationship("Torneo", back_populates="encuentros")  # Relación con la tabla Torneo
    estadisticas = relationship("Estadisticas", back_populates="encuentro")

# Definir la clase Torneo
class Torneo(base):
    __tablename__ = 'torneo'

    torneo_id = Column(Integer, primary_key=True, index=True,autoincrement=True)  # Clave primaria de Torneo
    nombre = Column(String, index=True)
    tipo = Column(String)
    ubicacion = Column(String)

    # Relaciones con otras tablas
    encuentros = relationship("Encuentros", back_populates="torneo")  # Relación con Encuentro
    asistencias = relationship("Asistencia", back_populates="torneo") 


class Asistencia(base):
    __tablename__ = 'asistencia'

    asistencia_id = Column(Integer, primary_key=True)  # Clave primaria
    asistio = Column(Boolean, nullable=False)
    documento = Column(Integer, ForeignKey('inscripcion.documento'))  # Relación con Inscripcion
    torneo_torneo_id = Column(Integer, ForeignKey('torneo.torneo_id'))  # Relación con Torneo (nombre corregido)

    # Relaciones con otras tablas
    inscripcion = relationship("Inscripcion", back_populates="asistencias")
    torneo = relationship("Torneo", back_populates="asistencias")

class Estadisticas(base):
    __tablename__ = 'estadisticas'
    
    id = Column(Integer, primary_key=True,autoincrement=True)
    goles = Column(Integer, nullable=False)
    asistencias = Column(Integer, nullable=False)
    tarjetasamarillas = Column(Integer, nullable=False)
    tarjetasrojas = Column(Integer, nullable=False)
    faltas = Column(Integer, nullable=False)
    penales = Column(Integer, nullable=False)
    tirolibres = Column(Integer, nullable=False)
    corners = Column(Integer, nullable=False)

    encuentros_encuentro_id = Column(Integer, ForeignKey('encuentros.Encuentro_id'))  # Clave foránea a Encuentro
    encuentro = relationship("Encuentros", back_populates="estadisticas") 

class Implementos(base):
    __tablename__ = 'implementos'  # Nombre de la tabla de implementos
    
    implementos = Column(Integer, primary_key=True, nullable=False ,autoincrement=True)  # Clave primaria
    cantidad = Column(Integer, nullable=False)
    descripcion = Column(String(100), nullable=False)
    nombre = Column(String(100), nullable=False)

    # Relación con la tabla 'Prestar' para obtener todos los préstamos de este implemento
    prestamos = relationship("Prestar", back_populates="implementos", cascade="all, delete-orphan")

class Pagos(base):
    __tablename__ = 'pagos'
    pagos_id = Column(Integer, primary_key=True,autoincrement=True)
    fecha = Column(Date, nullable=False)
    monto = Column(Double, nullable=False)
    categoria = Column(String(100), nullable=False)
    descripcion = Column(String(100), nullable=False)
    tipo = Column(String(100), nullable=False)
    inscripcion_documento = Column(Integer, ForeignKey('inscripcion.documento', ondelete='CASCADE') ,nullable=True)

    inscripcion = relationship("Inscripcion", back_populates="pagos")

class Prestar(base):
    __tablename__ = 'prestar'  # Nombre de la tabla de préstamos
    
    # Claves primarias compuestas
    usuario_documento = Column(Integer, ForeignKey('usuario.Documento'), primary_key=True)
    implementos_inventario_id = Column(Integer, ForeignKey('implementos.implementos'), primary_key=True)  # Cambiar el nombre de esta columna
    
    # Otros campos
    cantidad = Column(Integer, nullable=False)
    fechadepresta = Column(Date, nullable=False)
    estado = Column(String(45), nullable=False)

    # Relación con la tabla 'Usuario'
    usuario = relationship("Usuario", back_populates="prestamos", single_parent=True)  # Se eliminó el cascade
    
    # Relación con la tabla 'Implementos'
    implementos = relationship("Implementos", back_populates="prestamos", single_parent=True)  # Se eliminó el cascade


