"""Create table

Revision ID: 2647b9ffb56c
Revises: 
Create Date: 2021-12-12 18:58:48.780769

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '2647b9ffb56c'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('predictions', 
        sa.Column('id', sa.Integer, index=True, primary_key=True),
        sa.Column('dummyUniqueID', sa.Integer, nullable=False),
        sa.Column('anio', sa.Integer, nullable=False),
        sa.Column('mes', sa.Integer, nullable=False),
        sa.Column('Precio_leche', sa.Float, nullable=False),
        sa.Column('Coquimbo', sa.Float, nullable=False),
        sa.Column('Valparaiso', sa.Float, nullable=False),
        sa.Column('Metropolitana_de_Santiago', sa.Float, nullable=False),
        sa.Column('Maule', sa.Float, nullable=False),
        sa.Column('Biobio', sa.Float, nullable=False),
        sa.Column('La_Araucania', sa.Float, nullable=False),
        sa.Column('Los_Rios', sa.Float, nullable=False),
        sa.Column('PIB_Agropecuario_silvicola', sa.String, nullable=False),
        sa.Column('PIB_Pesca', sa.String, nullable=False),
        sa.Column('PIB_Mineria', sa.String, nullable=False),
        sa.Column('PIB_Mineria_del_cobre', sa.String, nullable=False),
        sa.Column('PIB_Otras_actividades_mineras', sa.String, nullable=False),
        sa.Column('PIB_Industria_Manufacturera', sa.String, nullable=False),
        sa.Column('PIB_Alimentos', sa.String, nullable=False),
        sa.Column('PIB_Bebidas_y_tabaco', sa.String, nullable=False),
        sa.Column('PIB_Textil', sa.String, nullable=False),
        sa.Column('PIB_Maderas_y_muebles', sa.String, nullable=False),
        sa.Column('PIB_Celulosa', sa.String, nullable=False),
        sa.Column('PIB_Refinacion_de_petroleo', sa.String, nullable=False),
        sa.Column('PIB_Minerales_no_metalicos_y_metalica_basica', sa.String, nullable=False),
        sa.Column('PIB_Productos_metalicos', sa.String, nullable=False),
        sa.Column('PIB_Electricidad', sa.String, nullable=False),
        sa.Column('PIB_Construccion', sa.String, nullable=False),
        sa.Column('PIB_Comercio', sa.String, nullable=False),
        sa.Column('PIB_Restaurantes_y_hoteles', sa.String, nullable=False),
        sa.Column('PIB_Transporte', sa.String, nullable=False),
        sa.Column('PIB_Comunicaciones', sa.String, nullable=False),
        sa.Column('PIB_Servicios_financieros', sa.String, nullable=False),
        sa.Column('PIB_Servicios_empresariales', sa.String, nullable=False),
        sa.Column('PIB_Servicios_de_vivienda', sa.String, nullable=False),
        sa.Column('PIB_Servicios_personales', sa.String, nullable=False),
        sa.Column('PIB_Administracion_publica', sa.String, nullable=False),
        sa.Column('PIB_a_costo_de_factores', sa.String, nullable=False),
        sa.Column('PIB', sa.String, nullable=False),
        sa.Column('Imacec_empalmado', sa.String, nullable=False),
        sa.Column('Imacec_produccion_de_bienes', sa.String, nullable=False),
        sa.Column('Imacec_minero', sa.String, nullable=False),
        sa.Column('Imacec_industria', sa.String, nullable=False),
        sa.Column('Imacec_resto_de_bienes', sa.String, nullable=False),
        sa.Column('Imacec_comercio', sa.String, nullable=False),
        sa.Column('Imacec_servicios', sa.String, nullable=False),
        sa.Column('Imacec_a_costo_de_factores', sa.String, nullable=False),
        sa.Column('Imacec_no_minero', sa.String, nullable=False),
        sa.Column('Indice_de_ventas_comercio_real_no_durables_IVCM', sa.String, nullable=False),
        sa.Column('pred', sa.Float, nullable=False),
    )


def downgrade():
    pass
