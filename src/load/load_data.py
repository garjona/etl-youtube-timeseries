import psycopg2
from psycopg2 import sql
from datetime import datetime

def connect_db(host,database,user,password,port):
    """
    Establece la conexión con la base de datos PostgreSQL.

    Returns:
        conn: Objeto de conexión a la base de datos.
        cursor: Cursor para ejecutar las consultas SQL.
    """
    try:
        # Conexión a la base de datos PostgreSQL
        conn = psycopg2.connect(
            host=host,      # Cambia esto según tu configuración
            database=database,  # Nombre de tu base de datos
            user=user,     # Tu nombre de usuario en PostgreSQL
            password=password,  # Tu contraseña de PostgreSQL
            port=port,
            options = "-c client_encoding=utf8"
        )
        cursor = conn.cursor()
        print("Conexión exitosa a la base de datos PostgreSQL.")
        return conn, cursor
    except Exception as e:
        print(f"Error al conectar a la base de datos: {e}")
        return None, None

def insert_video_data(conn, cursor, videos, process_start_time):
    """
    Inserta los datos de los videos en las tablas 'video_metadata' y 'youtube_video_data' en la base de datos PostgreSQL.
    Si los metadatos de un video cambian, se crea una nueva versión en video_metadata.

    Args:
        conn: Conexión a la base de datos.
        cursor: Cursor para ejecutar las consultas.
        videos (list): Lista de diccionarios con los metadatos de los videos.
    """
    try:
        # Definimos las consultas de inserción SQL
        insert_metadata_query = """
        INSERT INTO video_metadata (video_id, title, duration, published_at, version)
        VALUES (%s, %s, %s, %s, %s)
        ON CONFLICT (video_id, version) DO NOTHING;  -- Evita duplicados si ya existe un video con el mismo ID y versión
        """

        insert_video_data_query = """
        INSERT INTO youtube_video_data (video_id, views, timestamp, metadata_version)
        VALUES (%s, %s, %s, %s)
        ON CONFLICT (timestamp, id) DO NOTHING;  -- Evita duplicados si ya existe un video con el mismo timestamp e id
        """

        # Iteramos sobre la lista de videos
        for video in videos:
            # Preparamos los datos para la inserción
            video_id = video['id']
            title = video['title']
            duration = video['duration']
            published_at = video['publishedAt']  # Fecha y hora de la publicación del video

            # Verificar si el video ya existe en video_metadata
            cursor.execute("""
            SELECT title, duration, published_at, version FROM video_metadata WHERE video_id = %s ORDER BY version DESC LIMIT 1
            """, (video_id,))
            existing_video = cursor.fetchone()

            if existing_video:
                # Si el video existe, comparamos los datos
                existing_title, existing_duration, existing_published_at, existing_version = existing_video

                # Verificamos si los datos han cambiado
                if title != existing_title or duration != existing_duration or published_at != existing_published_at:
                    # Si los datos han cambiado, incrementamos la versión
                    new_version = existing_version + 1
                    cursor.execute(insert_metadata_query, (video_id, title, duration, published_at, new_version))
                else:
                    # Si los datos no han cambiado, usamos la versión existente
                    new_version = existing_version
            else:
                # Si el video no existe, insertamos como la primera versión (versión 1)
                new_version = 1
                cursor.execute(insert_metadata_query, (video_id, title, duration, published_at, new_version))

            # Preparamos los datos para la inserción en youtube_video_data
            views = video['views']
            timestamp = process_start_time  # Usamos la hora en que se inicio el proceso

            # Insertamos los datos en youtube_video_data con la versión correspondiente
            cursor.execute(insert_video_data_query, (video_id, views, timestamp, new_version))

        # Hacemos commit para guardar los cambios
        conn.commit()
        print(f"{len(videos)} videos insertados correctamente.")
    except Exception as e:
        print(f"Error al insertar los datos: {e}")
        conn.rollback()  # Si ocurre un error, deshacemos la transacción


def close_db(conn, cursor):
    """
    Cierra la conexión a la base de datos PostgreSQL.

    Args:
        conn: Conexión a la base de datos.
        cursor: Cursor para ejecutar las consultas.
    """
    try:
        cursor.close()
        conn.close()
        print("Conexión cerrada correctamente.")
    except Exception as e:
        print(f"Error al cerrar la conexión: {e}")