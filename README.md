# MLOPS end2end toy project

Stack: airflow + fastAPI

# Overview
Este proyecto contiene los archivos necesarios para entrenar y poner en produccion un modelo que predice el precio de la leche basandose en variables de precipitacion, financieras y precios pasados de la leche. 

La solucion construida contempla la obtencion de predicciones con data en tiempo real, pero tambien usando predicciones previamente construidas (batch). A pesar que construi estos dos enfoques, considero que para este caso de uso solo se debio haber considerado una solucion de prediccion por batch y no en tiempo real. Llegue a esta conclusion ya que la data de entrenamiento es una muestra por mes, es decir durante el mes solo se obtiene un precio. Por tanto, en tiempo de prediccion el modelo esperaria que la data tuviese el mismo comportamiento. Considerando estas cosas, se puede concluir que la informacion enviada en distintos dias del mes no cambiara. Finalmente, tener un modelo que corre el predict del modelo usando la misma data daria costos extras que se podrian evitar.

En las siguientes secciones de la documencion se detallara los componentes definidos en el proyecto.

## Contenido
1) Estructura del proyecto
2) Entrenamiento del modelo
3) Prediccion offline por batch
4) Servicio de prediccion
5) Ejecucion
6) Mejoras

## Entrenamiento del modelo
En esta fase se realiza el entrenamiento del modelo y preprocesamiento de la data, asi como tambien, la serializacion de los pipelines generados en estas etapas. Por cada paso, se guarda la data a modo de versionamiento. Tanto los pipelines como la data de output de cada etapa, se guarda de manera local en .pkl o .csv. Idealmente, seria mejor manejar un bucket de AWS o GCP para el guardado de los artefactos (pipeline de entrenamiento y preprocesamiento) y una BD o un bucket con versionamiento para los datos procesados. En la *Fig.1*, se detallan los pasos que componen el dag del entrenamiento del modelo en Airflow.
*Periodicidad de la ejecucion (CRON): Cuando se considere un reentrenamiento del modelo.* 

<figure>
  <img src="docs/training_dag.png" >
  <figcaption>Fig.1 - Dag de entrenamiento del modelo.</figcaption>
</figure> 

A continuacion explicare brevemente el objetivo de cada uno de estos pasos:
  - **Data gathering**: Es el conjunto de pasos donde se recolecta la data y se realizan pequeñas modificaciones, con el fin de preparar la data para el merging. Este dag guarda la data modificada en nuevos archivos .csv en la ruta `/data/interm/collect_*`.
  - **Merge data**: Se realiza el merging de las fuentes con las que se trabajaran, tambien se realiza un ordenamiento de la informacion en funcion a la fecha y se guarda en la ruta `/data/interm/merge_data.csv`
  - **Preprocess data**: Se realiza el preprocesamiento de los datos usando pipelines de sklearn y posteriormente se serializa el pipeline, ademas tambien se guardan los features generados en un .csv, idealmente deberia existir un feature store usando alguna herramienta como Feast. El pipeline se guarda en la carpeta `/artifacts/data_pipeline.pkl`, mientras que el archivo con los features se guarda en `/data/feature_store/efficient_feature_store.csv`
  - **Validate data**: Incorpora algunas validaciones; por cuestion de tiempo, las validaciones incoporadas son muy basicas, pero idealmente en este paso tambien deberia guardarse estadisticas de la data como la media de la distribucion. Estos estadisticos serviran posteriormente para ver si la informacion ha cambiado en cuanto a su distribucion y con ello tomar la decision de reentrenar el modelo.
  - **Hypertune parameters**: Se toma como input la data preprocesada y realiza la busqueda de hiperparametros y se guardan en `/artifacts/best_params.json`.
  - **Training model**: Se lleva a cabo el entrenamiento del modelo tomando como input la data preprocesada y los mejores hiperparametros encontrados. El modelo entrenado se serializa en `/artifacts/model_staging.pkl`, mientras que las metricas se encuentran an `/artifacts/model_metrics.json`
  - **Validate model**: En este paso se verifica si el modelo previamente entrenado es lo suficientemente bueno para ser promovido a prod. Se incorporaron validaciones muy simples, pero idealmente se deberian incorporar mas validaciones como por ejemplo, ver si el nuevo modelo es mejor o parecido al anterior usando las metricas de validacion. El modelo se serializa en `/artifacts/model_prod.pkl`.

## Prediccion offline por batch
En esta seccion se detalla el dag que opera la prediccion por batches. En la *Fig.2*, se detallan los pasos que componen al dag.
*Periodicidad de la ejecucion (CRON): De manera mensual, ya que la data es ingestada de esa forma.* 
<figure>
  <img src="docs/prediction_dag.png" >
  <figcaption>Fig.2 - Dag de entrenamiento del modelo.</figcaption>
</figure> 

A continuacion se detalla el objetivo de los pasos mostrados en la *Fig.2*:
  - **Gathering data y Merge data**: Estos pasos son identicos a los mencionados en la seccion 2. Como mejora de estos procesos, la informacion se deberia guardar de forma separada (actualmente se sobreescriben los mismos archivos), ya que son procesos independientes.
  - **Preprocess batch data**: En esta etapa, la data mergeada se transforma en datos preprocesados usando el pipeline de datos serializado en el dag de entrenamiento. El output sera solo un csv con los nuevos features creados y se guardara en `/data/features_store/super_efficient_feature_store.csv`
  - **Validate prediction data**: El objetivo de este paso es ver si la informacion tiene una distribucion parecida a la data de entrenamiento. Actualmente por falta de tiempo se incluyeron pruebas muy simples. 
  - **Validate prediction data**: Finalmente, usando la data guardada y el modelo serializado se generan las predicciones para el batch de datos y se guarda en `/data/batch_predictions/predictions.csv`

## Servicio de prediccion
El servicio se construyo usando fastAPI y se disponibiliza a traves de Nginx. La configuracion usada es una muy simple.

Respecto a las rutas del servicio, se disponibilizaron las siguientes:

## Ejecucion
- Primero, se debe construir y levantar los contenedores
```
docker-compose build
docker-compose up
```
- En la carpeta se cuenta con archivos que corresponden tanto al modelo serializado como al pipeline de datos serializado; sin embargo si se desea volver a entrenar el modelo, se debe entrar a la ruta `localhost:8080` y colocar como **user** y **password** *airflow*. Una vez dentro de airflow, se debe buscar el dag `training_food_model_v1_0_0` y luego de ingresar, darle click a la opcion Trigger
- Si se deseea ejecutar la prediccion por batch, se debe ingresar a la ruta `localhost:8080` y buscar el dag `prediction_food_model_v1_0_0`
- Para consultar al API, mandar un request a alguna de las rutas especificadas en la seccion 4.

## Mejoras