import os
import bcrypt
from datetime import date, datetime
from typing import List,Optional
from fastapi import FastAPI ,Query,HTTPException,Depends,status ,Form ,File ,UploadFile
from sqlalchemy.orm import Session,joinedload
from conexion import crear, get_db
from modelo import base, Inscripcion as JugadoresModel,Usuario as UsuarioModel,Implementos,Prestar,Pagos,EquipoInscripcion,Equipo,Torneo,Encuentros,Estadisticas
from shemas import Jugador as JugadoresSchema,UsuarioSchema ,ImplementosSchema,PrestarSchema,UsuarioSchemaActualizar,PagoSchema,EquipoInscripcionShema,EquipoSchema,TorneoSchema,EncuentroBase,EncuentroBase2,EstadisticasBase,PrestarSchemaActu,DocumentoSchema
from shemas import Login as log
from shemas import LoginUsuario 
from shemas import VerificationCode
from shemas import VerificationCode2
from shemas import CategoriaSchema
from shemas import UsuarioSchema

from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.exc import SQLAlchemyError,IntegrityError
from sqlalchemy import func
from fastapi.staticfiles import StaticFiles

# Crear la instancia de FastAPI
app = FastAPI()


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # O especifica tus orígenes permitidos
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# Crear las tablas en la base de datos
base.metadata.create_all(bind=crear)


@app.get("/consultarDocumentosTorneo/{torneo_id}", response_model=List[DocumentoSchema])
async def consultar_documentos_torneo(torneo_id: int, bd: Session = Depends(get_db)):
    try:
        # Ejecutar la consulta para obtener documentos únicos
        documentos = bd.query(EquipoInscripcion.documento).\
            join(Equipo).\
            join(Encuentros).\
            join(Torneo).\
            filter(Torneo.torneo_id == torneo_id).\
            distinct().all()
        
        # Convertir la lista de tuplas a una lista de diccionarios
        return [{"documento": doc[0]} for doc in documentos]
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Codigo para verificar deportista y administrador 
#////////////////////////////////////////////////////////////////////////////////////////////////////
#////////////////////////////////////////////////////////////////////////////////////////////////////
#////////////////////////////////////////////////////////////////////////////////////////////////////
verification_code = "0000"
@app.post("/verify_code")
async def verify_code(data: VerificationCode):
    if data.code == verification_code:
        return {"mensaje": "Código verificado correctamente"}
    else:
        raise HTTPException(status_code=400, detail="Código incorrecto")
    
verification_code2 = "0001"
@app.post("/verify_code2")
async def verify_code2(data: VerificationCode2):
    if data.code2 == verification_code2:
        return {"mensaje": "Código verificado correctamente"}
    else:
        raise HTTPException(status_code=400, detail="Código incorrecto")


# Codigo para Jugador 
#////////////////////////////////////////////////////////////////////////////////////////////////////
#////////////////////////////////////////////////////////////////////////////////////////////////////
#////////////////////////////////////////////////////////////////////////////////////////////////////
@app.post("/InsertarJ")
async def registrar_equipo(
    documento: int = Form(...),
    usuario: str = Form(...),
    password: str = Form(...),
    nombre: str = Form(...),
    apellidos: str = Form(...),
    edad: int = Form(...),
    fecha_nacimiento: str = Form(...),
    eps: str = Form(...),
    telefono: str = Form(...),
    email: str = Form(...),
    foto: UploadFile = File(...),
    nombre_acudiente: str = Form(...),
    telefono_acudiente: str = Form(...),
    email_acudiente: str = Form(...),
    categoria: str = Form(...),
    bd: Session = Depends(get_db)
):
    
    # Consulta para verificar si el documento ya existe
    nombre_user = bd.query(JugadoresModel).filter(JugadoresModel.documento == documento).first()
    if nombre_user:
        raise HTTPException(status_code=400, detail="El documento ya existe")

    # Validación para que el deportista no pase de 30 años
    if edad > 30:
        raise HTTPException(status_code=400, detail="La edad no puede ser mayor a 30 años")

    # Validar que el correo no esté repetido
    correo_existente = bd.query(JugadoresModel).filter(JugadoresModel.email == email).first()
    if correo_existente:
        raise HTTPException(status_code=400, detail="El correo ya está en uso")

    # Validar que el teléfono no esté repetido
    telefono_existente = bd.query(JugadoresModel).filter(JugadoresModel.telefono == telefono).first()
    if telefono_existente:
        raise HTTPException(status_code=400, detail="El teléfono ya está en uso")

    # Encriptar la contraseña
    encriptacion = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    
    # Validar el tipo de archivo
    if foto.content_type not in ["image/jpeg", "image/png" ,"image/jpg"]:
        raise HTTPException(status_code=400, detail="Formato de archivo no soportado")

    folder_path = "micarpetaimg"
    file_location = os.path.join(folder_path, foto.filename)

    # Asegúrate de que la carpeta existe
    os.makedirs(folder_path, exist_ok=True)

    # Guarda el archivo en el servidor
    with open(file_location, "wb") as buffer:
        buffer.write(await foto.read())

    foto_perfil_url = f"/micarpetaimg/{foto.filename}"

    # Crear una nueva instancia del modelo Jugadores
    nuevo_user = JugadoresModel(
        documento=documento,
        usuario=usuario,
        password=encriptacion.decode('utf-8'),  
        nombre=nombre,
        apellidos=apellidos,
        edad=edad,
        fecha_nacimiento=fecha_nacimiento,
        eps=eps,
        telefono=telefono,
        email=email,
        foto=foto_perfil_url,
        nombre_acudiente=nombre_acudiente,
        telefono_acudiente=telefono_acudiente,
        email_acudiente=email_acudiente,
        categoria=categoria
    )
    
    # Agregar el nuevo usuario a la base de datos
    bd.add(nuevo_user)
    bd.commit()
    bd.refresh(nuevo_user)
    
    return nuevo_user


app.mount("/micarpetaimg", StaticFiles(directory="micarpetaimg"), name="imagenes")


@app.put("/ActualizarJ/{documento}", response_model=JugadoresSchema)
async def actualizar_jugador(documento: str, modelojugador: JugadoresSchema, bd: Session = Depends(get_db)):
    try:
        # Buscar el jugador por documento
        jugador_existente = bd.query(JugadoresModel).filter(JugadoresModel.documento == documento).first()
        if not jugador_existente:
            raise HTTPException(status_code=404, detail="Jugador no encontrado")

        # Actualizar los campos necesarios
        for key, value in modelojugador.dict().items():
            setattr(jugador_existente, key, value)

        # Guardar los cambios en la base de datos
        bd.commit()
        bd.refresh(jugador_existente)
        return jugador_existente

    except Exception as e:
        bd.rollback()  # Asegúrate de hacer un rollback en caso de error
        raise HTTPException(status_code=422, detail=f"Error al actualizar: {str(e)}")

@app.delete("/EliminarJ/{documento}", response_model=dict)
async def eliminar_jugador(documento: str, bd: Session = Depends(get_db)):
    # Buscar el jugador por documento
    jugador_existente = bd.query(JugadoresModel).filter(JugadoresModel.documento == documento).first()
    if not jugador_existente:
        raise HTTPException(status_code=404, detail="Jugador no encontrado")
    
    # Eliminar el jugador de la base de datos
    bd.delete(jugador_existente)
    bd.commit()
    return {"detail": "Jugador eliminado exitosamente"}


@app.get("/ConsultarJugadores", response_model=List[JugadoresSchema])
async def consultar_jugadores(bd: Session = Depends(get_db)):
    try:
        datos_jugador = bd.query(JugadoresModel).all()
        if not datos_jugador:
            raise HTTPException(status_code=404, detail="No se encontraron jugadores")

        # Convertir datetime a date para cada jugador
        for jugador in datos_jugador:
            if isinstance(jugador.fecha_nacimiento, datetime):
                jugador.fecha_nacimiento = jugador.fecha_nacimiento.date()

        return datos_jugador
    except Exception as e:
        print(f"Error en consultar_jugadores: {str(e)}")
        raise HTTPException(status_code=500, detail="Error interno del servidor al consultar los jugadores")
    


@app.get("/ConsultarCategorias", response_model=List[CategoriaSchema])
async def consultar_categoria(bd: Session = Depends(get_db)):
    datos_jugador = bd.query(JugadoresModel).all()
    categorias = {}
    
    for jugador in datos_jugador:
        categoria = str(jugador.categoria)
        if categoria not in categorias:
            categorias[categoria] = []
        categorias[categoria].append(jugador.nombre)

    return [{"name": cat, "players": players} for cat, players in categorias.items()]

@app.get("/Jugadores/{documento_deportista}", response_model=JugadoresSchema)
async def consultar_documento_deportista(documento_deportista: int, bd: Session = Depends(get_db)):
    dato_equipo = bd.query(JugadoresModel).filter(JugadoresModel.documento == documento_deportista).first()
    if dato_equipo is None:
        raise HTTPException(status_code=404, detail="Dato no encontrado")
    return dato_equipo

@app.post("/loginDeportista")
async def login_usuario(usuario: log, db: Session = Depends(get_db)):
    user_in_db = db.query(JugadoresModel).filter(JugadoresModel.usuario == usuario.Loginusuario).first()
    if not user_in_db:
        raise HTTPException(status_code=400, detail="Usuario no encontrado")
    if not bcrypt.checkpw(usuario.password.encode('utf-8'), user_in_db.password.encode('utf-8')):
        raise HTTPException(status_code=400, detail="Contraseña incorrecta")
    return {"mensaje": "Login exitoso", "datos": user_in_db}

@app.post("/loginDeportistaJAVA")
async def login_usuario(usuario: LoginUsuario, db: Session = Depends(get_db)):
    user_in_db = db.query(JugadoresModel).filter(JugadoresModel.usuario == usuario.Loginusuario).first()
    if not user_in_db:
        raise HTTPException(status_code=400, detail="Usuario no encontrado")
    # Aquí se compara directamente la contraseña sin cifrar
    if usuario.password != user_in_db.password:  # Cambiado de LoginUsuario.password a usuario.password
        raise HTTPException(status_code=400, detail="Contraseña incorrecta")
    return {"mensaje": "Login exitoso", "datos": user_in_db}

@app.get("/CumpleanosEsteMes", response_model=list[JugadoresSchema])
async def obtener_cumpleanos_mes(bd: Session = Depends(get_db)):
    fecha_actual = datetime.now()
    mes_actual = fecha_actual.month
    # Aquí usamos func.date para extraer solo la fecha (sin la hora)
    jugadores_cumpleanos = bd.query(JugadoresModel).filter(
        func.extract('month', JugadoresModel.fecha_nacimiento) == mes_actual
    ).all()
    
    # Asegurémonos de formatear la fecha correctamente
    for jugador in jugadores_cumpleanos:
        jugador.fecha_nacimiento = jugador.fecha_nacimiento.date() 
    return jugadores_cumpleanos


#////////////////////////////////////////////////////////////////////////////////////////////////////
#////////////////////////////////////////////////////////////////////////////////////////////////////
#////////////////////////////////////////////////////////////////////////////////////////////////////
#USUARIO


@app.post("/InsertarUsuario", response_model=UsuarioSchema)
async def registrar_usuario(
    Documento: int = Form(...),
    usuario: str = Form(...),
    password: str = Form(...),
    nombre: str = Form(...),
    telefono: str = Form(...),
    correo_electronico: str = Form(...),
    rol: str = Form(...),
    foto: UploadFile = File(...),
    inscripcion_documento: Optional[int] = Form(None),
    bd: Session = Depends(get_db)
):
    # Verifica si el usuario ya existe
    usuario_existente = bd.query(UsuarioModel).filter(UsuarioModel.usuario == usuario).first()
    if usuario_existente:
        raise HTTPException(status_code=400, detail="El usuario ya existe")

    # Validar que el correo no esté repetido
    correo_existente = bd.query(UsuarioModel).filter(UsuarioModel.correo_electronico == correo_electronico).first()
    if correo_existente:
        raise HTTPException(status_code=400, detail="El correo ya está en uso")

    # Validar que el teléfono no esté repetido
    telefono_existente = bd.query(UsuarioModel).filter(UsuarioModel.telefono == telefono).first()
    if telefono_existente:
        raise HTTPException(status_code=400, detail="El teléfono ya está en uso")

    # Encriptar la contraseña
    encriptacion = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

    # Validar el tipo de archivo
    if foto.content_type not in ["image/jpeg", "image/png", "image/jpg"]:
        raise HTTPException(status_code=400, detail="Formato de archivo no soportado")

    folder_path = "micarpetaimg"
    file_location = os.path.join(folder_path, foto.filename)

    # Asegúrate de que la carpeta existe
    os.makedirs(folder_path, exist_ok=True)

    # Guarda el archivo en el servidor
    try:
        with open(file_location, "wb") as buffer:
            buffer.write(await foto.read())
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al guardar la foto: {str(e)}")

    # Crear el URL de la foto de perfil
    foto_perfil_url = f"/micarpetaimg/{foto.filename}"

    nuevo_usuario = UsuarioModel(
        Documento=Documento,
        correo_electronico=correo_electronico,
        nombre=nombre,
        password=encriptacion.decode('utf-8'),
        usuario=usuario,
        telefono=telefono,
        rol=rol, 
        foto=foto_perfil_url,
        inscripcion_documento=inscripcion_documento  
    )

    bd.add(nuevo_usuario)
    bd.commit()
    bd.refresh(nuevo_usuario)

    return nuevo_usuario

@app.get("/usuario/porRol", response_model=List[UsuarioSchema])
async def obtener_usuarios_por_rol(
    rol: Optional[str] = None,  # Añade el parámetro 'rol' con un valor por defecto None
    bd: Session = Depends(get_db)
):
    try:
        # Si no se proporciona un rol, devuelve todos los usuarios
        if rol is None:
            usuarios = bd.query(UsuarioModel).all()
        else:
            # Filtra los usuarios por el rol proporcionado
            usuarios = bd.query(UsuarioModel).filter(UsuarioModel.rol == rol).all()
        
        if not usuarios:
            raise HTTPException(status_code=404, detail="No se encontraron usuarios")
        
        return usuarios
    
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/ConsultarUsuarios", response_model=List[UsuarioSchema])
async def consultar_usuarios(bd: Session = Depends(get_db)):
    try:
        usuarios = bd.query(UsuarioModel).all()
        return usuarios
    
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=str(e))

def hash_password(password: str) -> str:
    # Genera un "salt" y luego hashea la contraseña con bcrypt
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed_password.decode('utf-8')


@app.put("/ActualizarUsuario/{Documento}", response_model=UsuarioSchemaActualizar)
async def actualizar_usuario(
    Documento: int, 
    modelousuario: UsuarioSchemaActualizar, 
    bd: Session = Depends(get_db)
):
    # Buscar el usuario en la base de datos
    usuario = bd.query(UsuarioModel).filter(UsuarioModel.Documento == Documento).first()

    if not usuario:
        # Si el usuario no se encuentra, lanzamos un error HTTP
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    # Actualizar los campos del usuario con los nuevos valores proporcionados
    usuario.correo_electronico = modelousuario.correo_electronico
    usuario.nombre = modelousuario.nombre
    usuario.usuario = modelousuario.usuario
    usuario.telefono = modelousuario.telefono
    usuario.rol = modelousuario.rol
    usuario.foto = modelousuario.foto  

    try:
        # Guardamos los cambios en la base de datos
        bd.commit()
        bd.refresh(usuario)
        return usuario  # Retorna el usuario actualizado
    except Exception as e:
        # Si ocurre un error en la actualización, lanzamos una excepción con el mensaje del error
        bd.rollback()  # Hacemos un rollback en caso de error
        raise HTTPException(status_code=500, detail=f"Error al actualizar el usuario: {str(e)}")
    

    
@app.delete("/EliminarUsuario/{documento}", response_model=dict)
async def eliminar_usuario(documento: int, bd: Session = Depends(get_db)):
    # Obtener el usuario por documento
    usuario = bd.query(UsuarioModel).filter(UsuarioModel.Documento == documento).first()

    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    # Eliminar al usuario y sus préstamos asociados en cascada
    bd.delete(usuario)
    bd.commit()

    return {"detail": "Usuario y préstamos asociados eliminados exitosamente"}


@app.post("/loginUsuario")
async def login(login_request: LoginUsuario, bd: Session = Depends(get_db)):
    usuario = bd.query(UsuarioModel).filter(UsuarioModel.usuario == login_request.Loginusuario).first()

    if usuario and bcrypt.checkpw(login_request.password.encode('utf-8'), usuario.password.encode('utf-8')):
        return {
            "mensaje": "Login exitoso",
            "datos": {
                "Documento":usuario.Documento,
                "usuario":usuario.usuario,
                "nombre": usuario.nombre,
                "email": usuario.correo_electronico,
                "rol":usuario.rol,
                "telefono":usuario.telefono,
                "foto":usuario.foto
            }
            
        }
    
    raise HTTPException(status_code=400, detail="Usuario o contraseña incorrectos")

@app.post("/loginUsuarioJAVA")
async def login(login_request: LoginUsuario, bd: Session = Depends(get_db)):
    usuario = bd.query(UsuarioModel).filter(UsuarioModel.usuario == login_request.Loginusuario).first()

    if usuario and login_request.password == usuario.password:
        return {
            "mensaje": "Login exitoso",
            "datos": {
                "Documento":usuario.Documento,
                "usuario":usuario.usuario,
                "nombre": usuario.nombre,
                "email": usuario.correo_electronico,
                "rol":usuario.rol,
                "telefono":usuario.telefono,
                "foto":usuario.foto
            }
            
        }
    
    raise HTTPException(status_code=400, detail="Usuario o contraseña incorrectos")


#////////////////////////////////////////////////////////////////////////////////////////////////////
#////////////////////////////////////////////////////////////////////////////////////////////////////
#////////////////////////////////////////////////////////////////////////////////////////////////////
#IMPLEMETOS

# Crear un nuevo implemento
@app.post("/insertarImplemento", response_model=ImplementosSchema)
async def insertar_implemento(
    implemento: ImplementosSchema,  # Recibe el esquema como argumento
    bd: Session = Depends(get_db)
):
    nuevo_implemento = Implementos(
        implementos=implemento.implementos,
        cantidad=implemento.cantidad,
        descripcion=implemento.descripcion,
        nombre=implemento.nombre
    )
    bd.add(nuevo_implemento)
    bd.commit()
    bd.refresh(nuevo_implemento)
    return nuevo_implemento

# Consultar un implemento por ID
@app.get("/consultarImplementos", response_model=List[ImplementosSchema])
async def consultar_implementos(bd: Session = Depends(get_db)):
    implementos = bd.query(Implementos).all()
    return implementos

@app.get("/consultarImplementos/{implementos}", response_model=List[ImplementosSchema])
async def consultar_implementos(implementos: str, bd: Session = Depends(get_db)):
    implementos = bd.query(Implementos).filter(Implementos.implementos == implementos).all()
    
    if not implementos:
        raise HTTPException(status_code=404, detail="404")
    
    return implementos
# Actualizar un implemento
@app.put("/actualizarImplemento/{implementos}", response_model=ImplementosSchema)
async def actualizar_implemento(
    implementos: int,
    implemento_actualizado: ImplementosSchema,
    bd: Session = Depends(get_db)
):
    implemento = bd.query(Implementos).filter(Implementos.implementos == implementos).first()
    if not implemento:
        raise HTTPException(status_code=404, detail="Implemento no encontrado")

    implemento.cantidad = implemento_actualizado.cantidad
    implemento.descripcion = implemento_actualizado.descripcion
    implemento.nombre = implemento_actualizado.nombre

    bd.commit()
    bd.refresh(implemento)
    return implemento

# Eliminar un implemento
@app.delete("/eliminarImplemento/{implementos}")
async def eliminar_implemento(implementos: int, bd: Session = Depends(get_db)):
    implemento = bd.query(Implementos).filter(Implementos.implementos == implementos).first()
    if not implemento:
        raise HTTPException(status_code=404, detail="Implemento no encontrado")

    bd.delete(implemento)
    bd.commit()
    return {"detail": "Implemento eliminado con éxito"}


#////////////////////////////////////////////////////////////////////////////////////////////////////
#////////////////////////////////////////////////////////////////////////////////////////////////////
#////////////////////////////////////////////////////////////////////////////////////////////////////
#PRESTAMO



@app.post("/insertarPrestamo", response_model=PrestarSchema)
async def insertar_prestamo(
    prestamo: PrestarSchema,
    bd: Session = Depends(get_db)
):
    # Verifica el implemento y su disponibilidad
    implemento = bd.query(Implementos).filter_by(implementos=prestamo.implementos_inventario_id).first()
    if not implemento:
        raise HTTPException(status_code=404, detail="Implemento no encontrado.")
    if implemento.cantidad < prestamo.cantidad:
        raise HTTPException(status_code=400, detail="No hay suficiente cantidad disponible.")

    # Crea y agrega el nuevo préstamo
    nuevo_prestamo = Prestar(
        usuario_documento=prestamo.usuario_documento,
        implementos_inventario_id=prestamo.implementos_inventario_id,
        cantidad=prestamo.cantidad,
        fechadepresta=prestamo.fechadepresta,
        estado=prestamo.estado
    )

    # Agrega el nuevo préstamo a la sesión de la base de datos
    bd.add(nuevo_prestamo)

    try:
        # Realiza la transacción (commit)
        bd.commit()
        bd.refresh(nuevo_prestamo)
        return nuevo_prestamo
    except IntegrityError as e:
        bd.rollback()
        if "duplicate" in str(e.orig):  # Ajusta según el mensaje específico de tu base de datos
            raise HTTPException(status_code=409, detail="El préstamo ya existe o hay datos duplicados.")
        raise HTTPException(status_code=500, detail="Error al realizar el préstamo.")

@app.put("/actualizarPrestamo/{usuario_documento}/{implementos_id}", response_model=PrestarSchemaActu)
async def actualizar_prestamo(
    usuario_documento: int,
    implementos_id: int,
    prestamo: PrestarSchemaActu,
    bd: Session = Depends(get_db)
):
    # Buscar préstamo existente
    prestamo_existente = bd.query(Prestar).filter(
        Prestar.usuario_documento == usuario_documento,
        Prestar.implementos_inventario_id == implementos_id
    ).first()

    if not prestamo_existente:
        raise HTTPException(status_code=404, detail="Préstamo no encontrado")

    # Actualiza los campos del préstamo existente
    prestamo_existente.cantidad = prestamo.cantidad
    prestamo_existente.estado = prestamo.estado

    # Realiza la transacción (commit)
    bd.commit()

    return prestamo_existente


@app.get("/consultarPrestamo/{usuario_documento}/{implementos_id}", response_model=PrestarSchema)
async def consultar_prestamo(
    usuario_documento: int,
    implementos_id: int,
    bd: Session = Depends(get_db)
):
    # Buscar el préstamo por usuario_documento y implementos_inventario_id
    prestamo = bd.query(Prestar).filter(
        Prestar.usuario_documento == usuario_documento,
        Prestar.implementos_inventario_id == implementos_id
    ).first()

    if not prestamo:
        raise HTTPException(status_code=404, detail="Préstamo no encontrado")

    return prestamo

@app.delete("/eliminarPrestamo/{usuario_documento}/{implementos_id}")
async def eliminar_prestamo(
    usuario_documento: int,
    implementos_id: int,
    bd: Session = Depends(get_db)
):
    # Buscar el préstamo a eliminar
    prestamo = bd.query(Prestar).filter(
        Prestar.usuario_documento == usuario_documento,
        Prestar.implementos_inventario_id == implementos_id
    ).first()

    if not prestamo:
        raise HTTPException(status_code=404, detail="Préstamo no encontrado")

    # Eliminar el préstamo
    bd.delete(prestamo)

    # Si es necesario, puedes restablecer la cantidad del implemento
    implemento = bd.query(Implementos).filter(Implementos.implementos == prestamo.implementos_inventario_id).first()
    if implemento:
        implemento.cantidad += prestamo.cantidad

    # Realiza la transacción (commit)
    bd.commit()

    return {"detail": "Préstamo eliminado con éxito"}



#////////////////////////////////////////////////////////////////////////////////////////////////////
#////////////////////////////////////////////////////////////////////////////////////////////////////
#////////////////////////////////////////////////////////////////////////////////////////////////////
#Pago


@app.post("/insertarPago", response_model=PagoSchema)
async def insertar_pago(
    pago: PagoSchema,
    bd: Session = Depends(get_db)
):
    # Verifica si ya existe un pago con el mismo ID
    pago_existente = bd.query(Pagos).filter_by(pagos_id=pago.pagos_id).first()
    if pago_existente:
        raise HTTPException(status_code=409, detail="El pago ya existe.")
    # Generar el próximo pagos_id
    
    # Crea y agrega el nuevo pago
    nuevo_pago = Pagos(
        # pagos_id=pago.pagos_id,
        # inscripcion_documento=pago.inscripcion_documento,
        monto=pago.monto,
        fecha=pago.fecha,
        categoria=pago.categoria,
        descripcion=pago.descripcion,
        tipo=pago.tipo
    )
    bd.add(nuevo_pago)
    try:
        bd.commit()
        bd.refresh(nuevo_pago)
        print(nuevo_pago)
        return nuevo_pago
    except IntegrityError as e:
        bd.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/consultarPago/{inscripcion_documento}", response_model=List[PagoSchema])
async def consultar_pago(
    inscripcion_documento: int,
    bd: Session = Depends(get_db)
):
    # Obtener todos los pagos asociados a un inscripcion_documento
    pagos = bd.query(Pagos).filter(Pagos.inscripcion_documento == inscripcion_documento).all()

    if not pagos:
        raise HTTPException(status_code=404, detail="No se encontraron pagos para este documento")

    return pagos

@app.get("/consultarPago", response_model=List[PagoSchema])
async def consultar_pago(
    bd: Session = Depends(get_db)
):
    # Obtener todos los pagos sin ningún filtro
    pagos = bd.query(Pagos).all()

    if not pagos:
        raise HTTPException(status_code=404, detail="No se encontraron pagos")

    return pagos

# @app.put("/actualizarPago/{inscripcion_documento}/{pagos_id}", response_model=PagoSchema)
# async def actualizar_pago(
#     inscripcion_documento: int,
#     pagos_id: int,
#     pago: PagoSchema,
#     bd: Session = Depends(get_db)
# ):
#     pago_existente = bd.query(Pagos).filter(
#         Pagos.inscripcion_documento == inscripcion_documento,
#         Pagos.Pagos_id == pagos_id
#     ).first()

#     if not pago_existente:
#         raise HTTPException(status_code=404, detail="Pago no encontrado")
    
#     # Actualiza los valores del pago
#     pago_existente.monto = pago.monto
#     pago_existente.fecha = pago.fecha
#     pago_existente.categoria = pago.categoria
#     pago_existente.descripcion = pago.descripcion
#     pago_existente.tipo = pago.tipo

#     bd.commit()
#     return pago_existente


@app.delete("/eliminarPago/{inscripcion_documento}/{pagos_id}")
async def eliminar_pago(
    inscripcion_documento: int,
    pagos_id: int,
    bd: Session = Depends(get_db)
):
    pago = bd.query(Pagos).filter(
        Pagos.inscripcion_documento == inscripcion_documento,
        Pagos.pagos_id == pagos_id
    ).first()

    if not pago:
        raise HTTPException(status_code=404, detail="Pago no encontrado")

    bd.delete(pago)
    bd.commit()
    return {"detail": "Pago eliminado con éxito"}

#////////////////////////////////////////////////////////////////////////////////////////////////////
#////////////////////////////////////////////////////////////////////////////////////////////////////
#////////////////////////////////////////////////////////////////////////////////////////////////////
#EQUIPO--Inscripcion


@app.post("/insertarEquipoInscripcion", response_model=EquipoInscripcionShema)
async def insertar_equipo_Inscripcion(
    equipo_Inscripcion: EquipoInscripcionShema,
    bd: Session = Depends(get_db)
):
    # Verifica si ya existe una relación entre el equipo y la inscripción (por equipoid + documento)
    existe_relacion = bd.query(EquipoInscripcion).filter_by(
        equipoid=equipo_Inscripcion.equipoid,
        documento=equipo_Inscripcion.documento  
    ).first()

    if existe_relacion:
        raise HTTPException(status_code=409, detail="La relación entre el equipo y el usuario ya existe.")
    
    try:
        nueva_relacion = EquipoInscripcion(
            equipoid=equipo_Inscripcion.equipoid,
            documento=equipo_Inscripcion.documento  
        )
        
        bd.add(nueva_relacion)
        bd.commit()
        bd.refresh(nueva_relacion)
        return nueva_relacion
    except IntegrityError as e:
        bd.rollback()
        raise HTTPException(
            status_code=400,
            detail=f"Error de integridad en la base de datos: {str(e)}"
        )
    except Exception as e:
        bd.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Error interno del servidor: {str(e)}"
        )

@app.get("/consultarEquipoInscripcion/{equipoid}", response_model=List[EquipoInscripcionShema])
async def consultar_equipo_Inscripcion_por_equipoid(
    equipoid: int,
    bd: Session = Depends(get_db)
):
    # Obtener todos los usuarios asociados al equipo
    relaciones = bd.query(EquipoInscripcion).filter(EquipoInscripcion.equipoid == equipoid).all()

    if not relaciones:
        raise HTTPException(status_code=404, detail="No se encontraron usuarios para este equipo.")

    return relaciones

@app.get("/consultarEquipoInscripcion", response_model=List[EquipoInscripcionShema])
async def consultar_equipo_Inscripcion(
    bd: Session = Depends(get_db)
):
    # Obtener todas las relaciones entre equipos y usuarios
    relaciones = bd.query(EquipoInscripcion).all()

    if not relaciones:
        raise HTTPException(status_code=404, detail="No se encontraron relaciones entre equipos y usuarios.")

    return relaciones

@app.delete("/eliminarEquipoInscripcion", response_model=EquipoInscripcionShema)
async def eliminar_equipo_inscripcion(
    equipo_Inscripcion: EquipoInscripcionShema,
    bd: Session = Depends(get_db)
):
    # Verifica si la relación existe en la base de datos
    relacion = bd.query(EquipoInscripcion).filter_by(
        equipoid=equipo_Inscripcion.equipoid,
        documento=equipo_Inscripcion.documento
    ).first()

    # Si no existe la relación, lanzamos un error
    if not relacion:
        raise HTTPException(status_code=404, detail="La relación entre el equipo y el usuario no existe.")

    # Elimina la relación
    try:
        bd.delete(relacion)
        bd.commit()
        return relacion  # Devuelve la relación eliminada (esto es opcional)
    except IntegrityError as e:
        bd.rollback()
        raise HTTPException(status_code=500, detail="Error al eliminar la relación.")


#////////////////////////////////////////////////////////////////////////////////////////////////////
#////////////////////////////////////////////////////////////////////////////////////////////////////
#////////////////////////////////////////////////////////////////////////////////////////////////////
#EQUIPO

@app.post("/insertarEquipo", response_model=EquipoSchema)
async def insertar_equipo(
    equipo: EquipoSchema,  # Recibe el esquema como argumento
    bd: Session = Depends(get_db)
):
    nuevo_equipo = Equipo(
        # equipoid=equipo.equipoid,
        fechacreacion=equipo.fechacreacion,
        categoria=equipo.categoria,
        nombre=equipo.nombre,
        usuario_id=equipo.usuario_id
    )
    bd.add(nuevo_equipo)
    bd.commit()
    bd.refresh(nuevo_equipo)
    return nuevo_equipo


@app.get("/consultarEquipos", response_model=List[EquipoSchema])
async def consultar_equipos(bd: Session = Depends(get_db)):
    equipos = bd.query(Equipo).all()
    return equipos


@app.get("/consultarEquipos/{nombre}", response_model=List[EquipoSchema])
async def consultar_equipo_por_nombre(nombre: str, bd: Session = Depends(get_db)):
    equipos = bd.query(Equipo).filter(Equipo.nombre == nombre).all()
    
    if not equipos:
        raise HTTPException(status_code=404, detail="No se encontraron equipos con ese nombre")
    
    return equipos


@app.put("/actualizarEquipo/{equipoid}", response_model=EquipoSchema)
async def actualizar_equipo(
    equipoid: int,
    equipo_actualizado: EquipoSchema,
    bd: Session = Depends(get_db)
):
    equipo = bd.query(Equipo).filter(Equipo.equipoid == equipoid).first()
    if not equipo:
        raise HTTPException(status_code=404, detail="Equipo no encontrado")

    equipo.fechacreacion = equipo_actualizado.fechacreacion
    equipo.categoria = equipo_actualizado.categoria
    equipo.nombre = equipo_actualizado.nombre
    equipo.usuario_id = equipo_actualizado.usuario_id

    bd.commit()
    bd.refresh(equipo)
    return equipo

@app.delete("/eliminarEquipo/{equipoid}")
async def eliminar_equipo(equipoid: int, bd: Session = Depends(get_db)):
    try:
        # Primero, busca el equipo
        equipo = bd.query(Equipo).filter(Equipo.equipoid == equipoid).first()
        if not equipo:
            raise HTTPException(status_code=404, detail="Equipo no encontrado")

        # Eliminar las relaciones en equipo_inscripcion
        relaciones = bd.query(EquipoInscripcion).filter(EquipoInscripcion.equipoid == equipoid).all()
        for relacion in relaciones:
            bd.delete(relacion)

        # Ahora eliminar el equipo
        bd.delete(equipo)
        bd.commit()
        return {"detail": "Equipo eliminado con éxito"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


#////////////////////////////////////////////////////////////////////////////////////////////////////
#////////////////////////////////////////////////////////////////////////////////////////////////////
#////////////////////////////////////////////////////////////////////////////////////////////////////
#TORNEO



# Crear un torneo
@app.post("/insertarTorneo", response_model=TorneoSchema)
async def insertar_torneo(torneo: TorneoSchema, bd: Session = Depends(get_db)):
    nuevo_torneo = Torneo(
        # torneo_id=torneo.torneo_id,
        nombre=torneo.nombre,
        tipo=torneo.tipo,
        ubicacion=torneo.ubicacion
    )
    bd.add(nuevo_torneo)
    bd.commit()
    bd.refresh(nuevo_torneo)
    return nuevo_torneo

# Consultar todos los torneos
@app.get("/consultarTorneos", response_model=List[TorneoSchema])
async def consultar_torneos(bd: Session = Depends(get_db)):
    torneos = bd.query(Torneo).all()
    return torneos

# Consultar torneo por nombre
@app.get("/consultarTorneos/{nombre}", response_model=List[TorneoSchema])
async def consultar_torneo_por_nombre(nombre: str, bd: Session = Depends(get_db)):
    torneos = bd.query(Torneo).filter(Torneo.nombre == nombre).all()
    
    if not torneos:
        raise HTTPException(status_code=404, detail="No se encontraron torneos con ese nombre")
    
    return torneos

# Actualizar torneo por ID
@app.put("/actualizarTorneo/{torneo_id}", response_model=TorneoSchema)
async def actualizar_torneo(torneo_id: int, torneo_actualizado: TorneoSchema, bd: Session = Depends(get_db)):
    torneo = bd.query(Torneo).filter(Torneo.torneo_id == torneo_id).first()
    if not torneo:
        raise HTTPException(status_code=404, detail="Torneo no encontrado")

    torneo.nombre = torneo_actualizado.nombre
    torneo.tipo = torneo_actualizado.ubicacion
    torneo.ubicacion = torneo_actualizado.ubicacion

    bd.commit()
    bd.refresh(torneo)
    return torneo

# Eliminar torneo por ID
@app.delete("/eliminarTorneo/{torneo_id}")
async def eliminar_torneo(torneo_id: int, bd: Session = Depends(get_db)):
    torneo = bd.query(Torneo).filter(Torneo.torneo_id == torneo_id).first()
    if not torneo:
        raise HTTPException(status_code=404, detail="Torneo no encontrado")
    
    bd.delete(torneo)
    bd.commit()
    return {"detail": "Torneo eliminado con éxito"}

#////////////////////////////////////////////////////////////////////////////////////////////////////
#////////////////////////////////////////////////////////////////////////////////////////////////////
#////////////////////////////////////////////////////////////////////////////////////////////////////
#ENCUENTROS

@app.post("/insertarEncuentro", response_model=EncuentroBase)
async def insertar_encuentro(encuentro: EncuentroBase, bd: Session = Depends(get_db)):
    # Verificar si ya existe un encuentro entre los mismos equipos en el mismo torneo
    existe_encuentro = bd.query(Encuentros).filter(
        Encuentros.equipo_equipoid == encuentro.equipo_equipoid,
        Encuentros.torneo_torneo_id == encuentro.torneo_torneo_id,
        Encuentros.fecha == encuentro.fecha,
        Encuentros.hora == encuentro.hora  # Puedes ajustar esta validación según tus necesidades
    ).first()

    if existe_encuentro:
        raise HTTPException(status_code=409, detail="Ya existe un encuentro programado entre estos equipos en este torneo.")

    nuevo_encuentro = Encuentros(
        equipo_equipoid=encuentro.equipo_equipoid,
        fecha=encuentro.fecha,
        torneo_torneo_id=encuentro.torneo_torneo_id,
        encuentroscol=encuentro.encuentroscol,
        hora=encuentro.hora,
        resultado=encuentro.resultado,
        tipo=encuentro.tipo,
        ubicacion=encuentro.ubicacion
    )

    bd.add(nuevo_encuentro)
    try:
        bd.commit()
        bd.refresh(nuevo_encuentro)
        return nuevo_encuentro
    except IntegrityError as e:
        bd.rollback()
        raise HTTPException(status_code=500, detail=e)

@app.get("/consultarEncuentros", response_model=List[EncuentroBase2])
async def consultar_encuentros(bd: Session = Depends(get_db)):
    encuentros = bd.query(Encuentros).all()
    return encuentros

@app.put("/actualizarEncuentro/{encuentro_id}", response_model=EncuentroBase2)
async def actualizar_encuentro(encuentro_id: int, encuentro_actualizado: EncuentroBase2, bd: Session = Depends(get_db)):
    encuentro = bd.query(Encuentros).filter(Encuentros.Encuentro_id == encuentro_id).first()
    if not encuentro:
        raise HTTPException(status_code=404, detail="Encuentro no encontrado")

    encuentro.equipo_equipoid = encuentro_actualizado.equipo_equipoid
    encuentro.fecha = encuentro_actualizado.fecha
    encuentro.torneo_torneo_id = encuentro_actualizado.torneo_torneo_id
    encuentro.encuentroscol = encuentro_actualizado.encuentroscol
    encuentro.hora = encuentro_actualizado.hora
    encuentro.resultado = encuentro_actualizado.resultado
    encuentro.tipo = encuentro_actualizado.tipo
    encuentro.ubicacion = encuentro_actualizado.ubicacion

    bd.commit()
    bd.refresh(encuentro)
    return encuentro


@app.delete("/eliminarEncuentro/{encuentro_id}")
async def eliminar_encuentro(encuentro_id: int, bd: Session = Depends(get_db)):
    encuentro = bd.query(Encuentros).filter(Encuentros.Encuentro_id == encuentro_id).first()
    if not encuentro:
        raise HTTPException(status_code=404, detail="Encuentro no encontrado")
    
    # Primero eliminamos las estadísticas asociadas al encuentro (si existen)
    if encuentro.estadisticas:
        for estadistica in encuentro.estadisticas:
            bd.delete(estadistica)
    
    # Ahora eliminamos el encuentro
    bd.delete(encuentro)
    bd.commit()
    
    return {"detail": "Encuentro eliminado con éxito"}

#////////////////////////////////////////////////////////////////////////////////////////////////////
#////////////////////////////////////////////////////////////////////////////////////////////////////
#////////////////////////////////////////////////////////////////////////////////////////////////////
#ESTADISTICAS

@app.post("/insertarEstadisticas/{encuentro_id}", response_model=EstadisticasBase)
async def insertar_estadisticas(encuentro_id: int, estadisticas: EstadisticasBase, bd: Session = Depends(get_db)):
    nuevo_estadisticas = Estadisticas(
        id=estadisticas.id,
        encuentros_encuentro_id=encuentro_id,
        asistencias=estadisticas.asistencias,
        corners=estadisticas.corners,
        faltas=estadisticas.faltas,
        goles=estadisticas.goles,
        penales=estadisticas.penales,
        tarjetasamarillas=estadisticas.tarjetasamarillas,
        tarjetasrojas=estadisticas.tarjetasrojas,
        tirolibres=estadisticas.tirolibres
    )
    bd.add(nuevo_estadisticas)
    bd.commit()
    bd.refresh(nuevo_estadisticas)
    return nuevo_estadisticas

@app.get("/consultarEstadisticas/{encuentro_id}", response_model=List[EstadisticasBase])  # Cambia a List[EstadisticasBase]
async def consultar_estadisticas(encuentro_id: int, bd: Session = Depends(get_db)):
    estadisticas = bd.query(Estadisticas).filter(Estadisticas.encuentros_encuentro_id == encuentro_id).all()  # Cambia .first() por .all()
    
    if not estadisticas:
        raise HTTPException(status_code=404, detail="Estadísticas no encontradas")
    
    return estadisticas

@app.put("/actualizarEstadisticas/{encuentro_id}", response_model=EstadisticasBase)
async def actualizar_estadisticas(encuentro_id: int, estadisticas_actualizadas: EstadisticasBase, bd: Session = Depends(get_db)):
    estadisticas = bd.query(Estadisticas).filter(Estadisticas.encuentros_encuentro_id == encuentro_id).first()
    if not estadisticas:
        raise HTTPException(status_code=404, detail="Estadísticas no encontradas")

    estadisticas.asistencias = estadisticas_actualizadas.asistencias
    estadisticas.corners = estadisticas_actualizadas.corners
    estadisticas.faltas = estadisticas_actualizadas.faltas
    estadisticas.goles = estadisticas_actualizadas.goles
    estadisticas.penales = estadisticas_actualizadas.penales
    estadisticas.tarjetasamarillas = estadisticas_actualizadas.tarjetasamarillas
    estadisticas.tarjetasrojas = estadisticas_actualizadas.tarjetasrojas
    estadisticas.tirolibres = estadisticas_actualizadas.tirolibres

    bd.commit()
    bd.refresh(estadisticas)
    return estadisticas

@app.delete("/eliminarEstadisticas/{encuentro_id}")
async def eliminar_estadisticas(encuentro_id: int, bd: Session = Depends(get_db)):
    estadisticas = bd.query(Estadisticas).filter(Estadisticas.encuentros_encuentro_id == encuentro_id).first()
    if not estadisticas:
        raise HTTPException(status_code=404, detail="Estadísticas no encontradas")
    
    bd.delete(estadisticas)
    bd.commit()
    return {"detail": "Estadísticas eliminadas con éxito"}






def format_date(db_date):
    if db_date:
        if isinstance(db_date, datetime):
            return db_date.date()
        return db_date
    return None

# 1. Endpoint para obtener equipo del deportista con relaciones
@app.get("/consultarEquipoPorDeportista/{documento}", response_model=EquipoSchema)
async def obtener_equipo_deportista(
    documento: int, 
    bd: Session = Depends(get_db)
):
    
    try:
        # Buscar la relación equipo-inscripción del deportista
        equipo_inscripcion = bd.query(EquipoInscripcion).options(
            joinedload(EquipoInscripcion.equipo).joinedload(Equipo.usuario)
        ).filter(
            EquipoInscripcion.documento == documento
        ).first()

        if not equipo_inscripcion or not equipo_inscripcion.equipo:
            raise HTTPException(
                status_code=404, 
                detail="Deportista no está inscrito en ningún equipo"
            )

        equipo = equipo_inscripcion.equipo
        
        # Obtener información del entrenador (usuario asociado al equipo)
        entrenador = equipo.usuario
        
        if not entrenador:
            raise HTTPException(
                status_code=404,
                detail="El equipo no tiene entrenador asignado"
            )

        # Verificar que el usuario es realmente un entrenador
        if entrenador.rol != "Entrenador":
            raise HTTPException(
                status_code=400,
                detail="El usuario asignado al equipo no tiene rol de entrenador"
            )

        return {
            "equipoid": equipo.equipoid,
            "nombre": equipo.nombre,
            "categoria": equipo.categoria,
            "fechacreacion": format_date(equipo.fechacreacion),
            "usuario_id": equipo.usuario_id,  # ID del entrenador
            "entrenador": {
                "Documento": entrenador.Documento,
                "nombre": entrenador.nombre,
                "correo_electronico": entrenador.correo_electronico,
                "usuario": entrenador.usuario,
                "telefono": entrenador.telefono,
                "rol": entrenador.rol,
                "foto": entrenador.foto
            }
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Error al consultar el equipo: {str(e)}"
        )

# 2. Endpoint para compañeros de equipo con información completa
@app.get("/consultarCompanerosEquipo/{equipoid}", response_model=List[UsuarioSchema])
async def obtener_companeros_equipo(
    equipoid: int,
    excluir_documento: Optional[int] = None,
    bd: Session = Depends(get_db)
):
    try:
        query = bd.query(EquipoInscripcion).options(
            joinedload(EquipoInscripcion.inscripcion).joinedload(inscripciones.usuarios)
        ).filter(
            EquipoInscripcion.equipoid == equipoid
        )

        if excluir_documento:
            query = query.filter(EquipoInscripcion.documento != excluir_documento)

        inscripciones = query.all()

        companeros = []
        for insc in inscripciones:
            if insc.inscripcion and insc.inscripcion.usuarios:
                for usuario in insc.inscripcion.usuarios:
                    companeros.append({
                        "Documento": usuario.Documento,
                        "nombre": usuario.nombre,
                        "usuario": usuario.usuario,
                        "correo_electronico": usuario.correo_electronico,
                        "telefono": usuario.telefono,
                        "rol": usuario.rol,
                        "foto": usuario.foto,
                        "inscripcion_documento": usuario.inscripcion_documento
                    })

        return companeros

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# 3. Endpoint para encuentros del equipo con estadísticas
@app.get("/consultarEncuentrosEquipo/{equipoid}", response_model=List[EncuentroBase2])
async def obtener_encuentros_equipo(
    equipoid: int,
    fecha_desde: Optional[date] = None,
    fecha_hasta: Optional[date] = None,
    bd: Session = Depends(get_db)
):
    try:
        query = bd.query(Encuentros).options(
            joinedload(Encuentros.torneo),
            joinedload(Encuentros.estadisticas)
        ).filter(
            Encuentros.equipo_equipoid == equipoid
        )

        if fecha_desde:
            query = query.filter(Encuentros.fecha >= fecha_desde)
        if fecha_hasta:
            query = query.filter(Encuentros.fecha <= fecha_hasta)

        encuentros = query.order_by(Encuentros.fecha).all()

        result = []
        for enc in encuentros:
            encuentro_data = {
                "Encuentro_id": enc.Encuentro_id,
                "equipo_equipoid": enc.equipo_equipoid,
                "fecha": format_date(enc.fecha),
                "torneo_torneo_id": enc.torneo_torneo_id,
                "encuentroscol": enc.encuentroscol,
                "hora": enc.hora,
                "resultado": enc.resultado,
                "tipo": enc.tipo,
                "ubicacion": enc.ubicacion,
                "torneo": {
                    "nombre": enc.torneo.nombre,
                    "tipo": enc.torneo.tipo,
                    "ubicacion": enc.torneo.ubicacion
                } if enc.torneo else None,
                "estadisticas": [{
                    "id": est.id,
                    "asistencias": est.asistencias,
                    "corners": est.corners,
                    "faltas": est.faltas,
                    "goles": est.goles,
                    "penales": est.penales,
                    "tarjetasamarillas": est.tarjetasamarillas,
                    "tarjetasrojas": est.tarjetasrojas,
                    "tirolibres": est.tirolibres
                } for est in enc.estadisticas]
            }
            result.append(encuentro_data)

        return result

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# 4. Endpoint para torneos del equipo con encuentros
@app.get("/consultarTorneosEquipo/{equipoid}", response_model=List[TorneoSchema])
async def obtener_torneos_equipo(
    equipoid: int,
    bd: Session = Depends(get_db)
):
    try:
        # Obtener encuentros del equipo con torneos
        encuentros = bd.query(Encuentros).options(
            joinedload(Encuentros.torneo)
        ).filter(
            Encuentros.equipo_equipoid == equipoid,
            Encuentros.torneo_torneo_id.isnot(None)
        ).distinct(Encuentros.torneo_torneo_id).all()

        torneos = []
        for enc in encuentros:
            if enc.torneo:
                torneos.append({
                    "torneo_id": enc.torneo.torneo_id,
                    "nombre": enc.torneo.nombre,
                    "tipo": enc.torneo.tipo,
                    "ubicacion": enc.torneo.ubicacion,
                    "encuentros": [{
                        "fecha": format_date(e.fecha),
                        "resultado": e.resultado
                    } for e in bd.query(Encuentros).filter(
                        Encuentros.torneo_torneo_id == enc.torneo.torneo_id,
                        Encuentros.equipo_equipoid == equipoid
                    ).all()]
                })

        return torneos

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# 5. Endpoint para estadísticas de encuentro
@app.get("/consultarEstadisticasEncuentro/{encuentro_id}", response_model=EstadisticasBase)
async def obtener_estadisticas_encuentro(
    encuentro_id: int,
    bd: Session = Depends(get_db)
):
    try:
        estadisticas = bd.query(Estadisticas).filter(
            Estadisticas.encuentros_encuentro_id == encuentro_id
        ).first()

        if not estadisticas:
            raise HTTPException(status_code=404, detail="Estadísticas no encontradas")

        return estadisticas

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))