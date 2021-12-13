from pydantic import BaseModel

class PredictionBase(BaseModel):
    dummyUniqueID: int
    anio: int
    mes: int
    Precio_leche: float
    Coquimbo: float
    Valparaiso: float
    Metropolitana_de_Santiago: float
    Maule: float
    Biobio: float
    La_Araucania: float
    Los_Rios: float
    PIB_Agropecuario_silvicola: str
    PIB_Pesca: str
    PIB_Mineria: str
    PIB_Mineria_del_cobre: str
    PIB_Otras_actividades_mineras: str
    PIB_Industria_Manufacturera: str
    PIB_Alimentos: str
    PIB_Bebidas_y_tabaco: str
    PIB_Textil: str
    PIB_Maderas_y_muebles: str
    PIB_Celulosa: str
    PIB_Refinacion_de_petroleo: str
    PIB_Minerales_no_metalicos_y_metalica_basica: str
    PIB_Productos_metalicos: str
    PIB_Electricidad: str
    PIB_Construccion: str
    PIB_Comercio: str
    PIB_Restaurantes_y_hoteles: str
    PIB_Transporte: str
    PIB_Comunicaciones: str
    PIB_Servicios_financieros: str
    PIB_Servicios_empresariales: str
    PIB_Servicios_de_vivienda: str
    PIB_Servicios_personales: str
    PIB_Administracion_publica: str
    PIB_a_costo_de_factores: str
    PIB: str
    Imacec_empalmado: str
    Imacec_produccion_de_bienes: str
    Imacec_minero: str
    Imacec_industria: str
    Imacec_resto_de_bienes: str
    Imacec_comercio: str
    Imacec_servicios: str
    Imacec_a_costo_de_factores: str
    Imacec_no_minero: str
    Indice_de_ventas_comercio_real_no_durables_IVCM: str
    pred: int

class PredictionCreate(PredictionBase):
    pass

class Prediction(PredictionBase):
    id: int

    class Config:
        orm_mode: True