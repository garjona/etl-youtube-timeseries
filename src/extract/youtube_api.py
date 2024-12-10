from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

def extract_video_metadata(video_response):
    """
    Extrae los metadatos relevantes de los videos proporcionados en la respuesta de la API de YouTube.

    Args:
        video_response (dict): Respuesta obtenida de la API de YouTube que contiene los datos de los videos.

    Returns:
        list: Una lista de diccionarios con los metadatos de cada video extraído.
    """
    videos = [] # Lista que almacenará los metadatos de cada video

    try:
        # Iteramos sobre cada video en la respuesta de la API
        for video in video_response['items']:
            # Extraemos los metadatos específicos de cada video
            title = video['snippet']['title'] # Título del video
            video_id = video['id'] # ID único del video
            duration = video['contentDetails']['duration']  # Duración del video en formato ISO 8601 (ejemplo: PT1H2M3S)
            views = video['statistics'].get('viewCount', 'No disponible')  # Número de vistas, si está disponible
            published_at = video['snippet']['publishedAt']  # Fecha de publicación del video

            # Guardamos los metadatos extraídos en la lista 'videos'
            videos.append({
                'title': title,
                'id': video_id,
                'duration': duration,
                'views': views,
                'publishedAt': published_at
            })
    except KeyError as e:
        print(f"Error al acceder a una clave de la respuesta de la API: {e}")
    except Exception as e:
        print(f"Ocurrió un error inesperado al procesar los metadatos: {e}")

    # Devolvemos la lista de videos con sus metadatos
    return videos

def fetch_video_data(api_key, channel_id, max_results=10):
    """
    Obtiene los metadatos de los videos más recientes de un canal de YouTube específico.

    Conecta con la API de YouTube y obtiene los datos básicos de los videos, tales como
    título, ID, duración y número de vistas.

    Args:
        api_key (str): Clave de API de YouTube, proporcionada por Google.
        channel_id (str): ID del canal de YouTube del cual se desean obtener los videos.
        max_results (int, opcional): Número máximo de videos que se desean obtener. Por defecto es 10.

    Returns:
        list: Una lista de diccionarios con los metadatos de los videos obtenidos del canal.
    """

    videos = []  # Lista para almacenar los metadatos de los videos

    try:
        # Establecemos la conexión a la API de YouTube utilizando la clave de API proporcionada
        youtube = build('youtube', 'v3', developerKey=api_key)

        # Hacemos una llamada a la API para obtener los videos más recientes del canal
        request = youtube.search().list(
            part="snippet",  # Solo necesitamos el snippet de cada video (título, descripción, etc.)
            channelId=channel_id,  # ID del canal de YouTube
            maxResults=max_results,  # Número máximo de resultados (videos) que deseamos obtener
            order="date"  # Ordenamos los videos por fecha (puede cambiarse a 'relevance' para por relevancia)
        )
        # Ejecutamos la solicitud y obtenemos la respuesta de la API
        response = request.execute()

        # Extraemos los IDs de los videos de la respuesta de la API
        video_ids = [item['id']['videoId'] for item in response['items'] if item['id']['kind'] == 'youtube#video']

        # Iteramos sobre los IDs de los videos y obtenemos los metadatos detallados de cada uno
        for video_id in video_ids:
            # Hacemos una solicitud para obtener más detalles sobre cada video
            video_request = youtube.videos().list(
                part="snippet,contentDetails,statistics",
                id=video_id
            )
            # Ejecutamos la solicitud y obtenemos la respuesta de la API
            video_response = video_request.execute()

            # Extraemos los metadatos del video usando la función 'extraer_metadatos' definida anteriormente
            videos.extend(extract_video_metadata(video_response))

    except HttpError as e:
        # Manejo de errores específicos de la API de YouTube (errores HTTP)
        print(f"Error al hacer la solicitud a la API de YouTube: {e}")
    except Exception as e:
        # Captura de cualquier otro error inesperado
        print(f"Ocurrió un error inesperado al obtener los videos: {e}")

    # Devolvemos la lista de metadatos de los videos obtenidos
    return videos