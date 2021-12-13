from enum import Flag
from sqlalchemy import Column, Integer, Float, Integer, String

from .database import Base

class Prediction(Base):
    __tablename__ = "predictions"

    id = Column(Integer, primary_key=True, index=True)
    dummyUniqueID = Column(Integer)
    anio = Column(Integer)
    mes = Column(Integer)
    Precio_leche = Column(Float)
    Coquimbo = Column(Float)
    Valparaiso = Column(Float)
    Metropolitana_de_Santiago = Column(Float)
    Maule = Column(Float)
    Biobio = Column(Float)
    La_Araucania = Column(Float)
    Los_Rios = Column(Float)
    PIB_Agropecuario_silvicola = Column(String)
    PIB_Pesca = Column(String)
    PIB_Mineria = Column(String)
    PIB_Mineria_del_cobre = Column(String)
    PIB_Otras_actividades_mineras = Column(String)
    PIB_Industria_Manufacturera = Column(String)
    PIB_Alimentos = Column(String)
    PIB_Bebidas_y_tabaco = Column(String)
    PIB_Textil = Column(String)
    PIB_Maderas_y_muebles = Column(String)
    PIB_Celulosa = Column(String)
    PIB_Refinacion_de_petroleo = Column(String)
    PIB_Minerales_no_metalicos_y_metalica_basica = Column(String)
    PIB_Productos_metalicos = Column(String)
    PIB_Electricidad = Column(String)
    PIB_Construccion = Column(String)
    PIB_Comercio = Column(String)
    PIB_Restaurantes_y_hoteles = Column(String)
    PIB_Transporte = Column(String)
    PIB_Comunicaciones = Column(String)
    PIB_Servicios_financieros = Column(String)
    PIB_Servicios_empresariales = Column(String)
    PIB_Servicios_de_vivienda = Column(String)
    PIB_Servicios_personales = Column(String)
    PIB_Administracion_publica = Column(String)
    PIB_a_costo_de_factores = Column(String)
    PIB = Column(String)
    Imacec_empalmado = Column(String)
    Imacec_produccion_de_bienes = Column(String)
    Imacec_minero = Column(String)
    Imacec_industria = Column(String)
    Imacec_resto_de_bienes = Column(String)
    Imacec_comercio = Column(String)
    Imacec_servicios = Column(String)
    Imacec_a_costo_de_factores = Column(String)
    Imacec_no_minero = Column(String)
    Indice_de_ventas_comercio_real_no_durables_IVCM = Column(String)
    pred = Column(Float)