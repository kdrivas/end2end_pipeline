# Features
TARGET_COL = 'Precio_leche'

PERIOD_COLS = [
    'anio',
    'mes',
]

PIB_COLS = [
    'PIB_Agropecuario_silvicola',
    'PIB_Pesca',
    'PIB_Mineria',
    'PIB_Mineria_del_cobre',
    'PIB_Otras_actividades_mineras',
    'PIB_Industria_Manufacturera',
    'PIB_Alimentos',
    'PIB_Bebidas_y_tabaco',
    'PIB_Textil',
    'PIB_Maderas_y_muebles',
    'PIB_Celulosa',
    'PIB_Refinacion_de_petroleo',
    'PIB_Quimica',
    'PIB_Minerales_no_metalicos_y_metalica_basica',
    'PIB_Productos_metalicos',
    'PIB_Electricidad',
    'PIB_Construccion',
    'PIB_Comercio',
    'PIB_Restaurantes_y_hoteles',
    'PIB_Transporte',
    'PIB_Comunicaciones',
    'PIB_Servicios_financieros',
    'PIB_Servicios_empresariales',
    'PIB_Servicios_de_vivienda',
    'PIB_Servicios_personales',
    'PIB_Administracion_publica',
    'PIB_a_costo_de_factores',
    'PIB',
]

IMACEC_INDICE_COLS = [
    'Imacec_empalmado',
    'Imacec_produccion_de_bienes',
    'Imacec_minero',
    'Imacec_industria',
    'Imacec_resto_de_bienes',
    'Imacec_comercio',
    'Imacec_servicios',
    'Imacec_a_costo_de_factores',
    'Imacec_no_minero',
    'Indice_de_ventas_comercio_real_no_durables_IVCM'
]

CITY_COLS = [
    'Coquimbo',
    'Valparaiso',
    'Metropolitana_de_Santiago',
    'Libertador_Gral__Bernardo_O_Higgins',
    'Maule',
    'Biobio',
    'La_Araucania',
    'Los_Rios'
]

MILK_COLS = PERIOD_COLS

BANK_COLS = PERIOD_COLS + PIB_COLS + IMACEC_INDICE_COLS

PREP_COLS = PERIOD_COLS + CITY_COLS

MERGE_COLS = PERIOD_COLS + CITY_COLS + PIB_COLS + IMACEC_INDICE_COLS 