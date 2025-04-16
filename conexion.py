# Se llaman las bibliotecas para vilcular mysql
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

#railway externa
#URL_DB="mysql+mysqlconnector://root:aFxlxpAZVRUFRtPefCFcNjrkfVTFNitf@gondola.proxy.rlwy.net:41398/cef1"

#railway interna
URL_DB="mysql+mysqlconnector://root:aFxlxpAZVRUFRtPefCFcNjrkfVTFNitf@mysql.railway.internal:3306/cef1"


# docker
# URL_DB="mysql+mysqlconnector://root:0000@host.docker.internal:3306/cef1"

#sql
#URL_DB="mysql+mysqlconnector://root:0000@localhost:3306/cef1"

#sql daniela
#URL_DB="mysql+mysqlconnector://root:Mondangi707@localhost:3306/cef1"

# Mariadb
# URL_DB="mysql+mysqlconnector://admin_adso:1@127.0.0.1:3366/cef1"
crear=create_engine(URL_DB)
sessionlocal=sessionmaker(autocommit=False,autoflush=False,bind=crear)
base=declarative_base()
#try para crear y finalizar la base de datos
def get_db():
    cnn=sessionlocal()
    try:
        yield cnn
    finally:
        cnn.close()
