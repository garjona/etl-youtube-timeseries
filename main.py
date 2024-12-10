from dotenv import dotenv_values
from src.extract.youtube_api import fetch_video_data
from src.transform.transform_data import transform_video_data


# Cargar variables de entorno desde .env
config = dotenv_values(".env")

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

    except Exception as e:
        print(f"Error al obtener datos de YouTube: {e}")

if __name__ == "__main__":
    main()