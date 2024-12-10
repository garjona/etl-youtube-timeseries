from dotenv import dotenv_values
from src.extract.youtube_api import fetch_video_data
from src.transform.transform_data import transform_video_data
from src.load.load_data import connect_db, insert_video_data, close_db
from datetime import datetime
import pytz


# Cargar variables de entorno desde .env
config = dotenv_values(".env")

# Cargar la fecha del inicio del proceso
process_start_time = datetime.now(pytz.utc)

def main():
    # Llamar a la función del script youtube_api
    try:
        video_data = fetch_video_data(
            config["YOUTUBE_API_KEY"],
            config["YOUTUBE_CHANNEL_ID"],
            config["YOUTUBE_MAX_RESULTS"]
        )
        print("Datos obtenidos de YouTube")
        print(video_data)

        transformed_data = transform_video_data(video_data)

        print("Datos transformados")
        print(transformed_data)

        # Establecemos la conexión con la base de datos
        conn, cursor = connect_db(
            config["DB_HOST"],
            config["DB_DATABASE"],
            config["DB_USER"],
            config["DB_PASSWORD"],
            int(config["DB_PORT"])
        )
        print("Conectado a la base de datos")

        # Se insertan los datos transformados a las tablas correspondientes
        insert_video_data(conn, cursor, transformed_data, process_start_time)

        # Se cierra la conexion a la base de datos
        close_db(conn,cursor)


    except Exception as e:
        print(f"Error al obtener datos de YouTube: {e}")

if __name__ == "__main__":
    main()