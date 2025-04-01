# Se llaman las bibliotecas para vilcular mysql
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

#llamamos url de la base de datos creada en sql
# URL_DB="mysql+mysqlconnector://root:0000@localhost:3306/cef1"
URL_DB="mysql+mysqlconnector://admin_adso:1@127.0.0.1:3366/cef1"
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
