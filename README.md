# YouTube Video Data Analysis

Este proyecto obtiene, transforma y almacena datos de videos de YouTube en una base de datos PostgreSQL. Utiliza la API de YouTube para extraer información de los videos de un canal específico, realiza transformaciones de los datos y luego los almacena en una base de datos para su análisis posterior.

## Estructura del Proyecto

- `main.py`: Script principal que coordina el flujo de trabajo. Extrae los datos de la API de YouTube, los transforma y los guarda en una base de datos PostgreSQL.
- `src/extract/youtube_api.py`: Contiene las funciones que interactúan con la API de YouTube para obtener los metadatos de los videos.
- `src/transform/transform_data.py`: Realiza las transformaciones necesarias a los datos obtenidos (como convertir duraciones y fechas, limpiar títulos, etc.).
- `src/load/load_data.py`: Maneja la conexión a la base de datos PostgreSQL e inserta los datos transformados en las tablas correspondientes.
- `notebooks/Notebook.ipynb`: Un notebook para analizar visualmente los datos de YouTube obtenidos y almacenados en la base de datos.
- `.env`: Archivo para almacenar las variables de entorno como la clave de la API de YouTube y las credenciales de la base de datos.
- `requirements.txt`: Lista de dependencias necesarias para ejecutar el proyecto.

## Requisitos

Este proyecto requiere Python 3.11 y las siguientes dependencias que puedes instalar utilizando `pip`:

```bash
pip install -r requirements.txt
```

Las librerías necesarias son:

- `google-api-python-client`
- `google-auth-oauthlib`
- `google-auth-httplib2`
- `python-dotenv`
- `psycopg2`
- `pytz`
- `notebook`
- `pandas`
- `matplotlib`
- `SQLAlchemy`
- `plotly`
- `dash`

## Configuración

1. Crea el archivo `.env` en la raíz del proyecto y agrega tus credenciales de la API de YouTube y de la base de datos PostgreSQL:

```env
YOUTUBE_API_KEY=<your_youtube_api_key>
YOUTUBE_CHANNEL_ID=<your_channel_id>
YOUTUBE_MAX_RESULTS=10
DB_HOST=<your_db_host>
DB_PORT=<your_db_port>
DB_DATABASE=<your_db_name>
DB_USER=<your_db_user>
DB_PASSWORD=<your_db_password>
```

Asegúrate de reemplazar los valores entre `< >` con tus propios valores.

2. Base de datos PostgreSQL: Asegúrate de tener una base de datos PostgreSQL en funcionamiento. Además, necesitarás instalar la extensión TimescaleDB para poder crear y gestionar hypertables. Este proyecto espera que existan las tablas `video_metadata` y `youtube_video_data` con las siguientes estructuras:

```sql
CREATE TABLE video_metadata (
    video_id TEXT,
    title TEXT,
    duration INTERVAL,
    published_at TIMESTAMPTZ,
    version INT DEFAULT 1,
    PRIMARY KEY (video_id, version)
);

CREATE TABLE youtube_video_data (
    id SERIAL PRIMARY KEY,
    video_id TEXT NOT NULL,
    views BIGINT,
    timestamp TIMESTAMPTZ NOT NULL DEFAULT now(),
    metadata_version INT NOT NULL DEFAULT 1,
    FOREIGN KEY (video_id, metadata_version) REFERENCES video_metadata (video_id, version) ON DELETE CASCADE
);
```
Para aprovechar las ventajas del particionamiento temporal que ofrece TimescaleDB, convierte la tabla `youtube_video_data` en una hypertable, indexándola por la columna timestamp:

```sql
SELECT create_hypertable('youtube_video_data', 'timestamp'); 
```

## Uso

### Ejecutar el proyecto principal:
```bash
python main.py
```

Este script realizará lo siguiente:

Llamará a la API de YouTube para obtener los metadatos de los videos más recientes del canal especificado.
Transformará los datos (como convertir las duraciones y fechas a formatos adecuados).
Conectará a la base de datos PostgreSQL e insertará los datos transformados en las tablas correspondientes.

### Análisis de Datos

Si deseas realizar un análisis visual de los datos, puedes abrir el archivo [Notebook.ipynb](https://github.com/garjona/etl-youtube-timeseries/blob/master/notebooks/Notebook.ipynb) en Jupyter Notebook o en cualquier entorno compatible con notebooks de Python. En este notebook, puedes cargar y visualizar los datos almacenados en la base de datos utilizando herramientas como pandas, matplotlib, plotly y dash.

## Contribuciones

Si deseas contribuir a este proyecto, siéntete libre de hacer un fork, crear un pull request o abrir un issue con tus sugerencias.
