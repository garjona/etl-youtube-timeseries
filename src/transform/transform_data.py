import re
from datetime import datetime
import pytz
from datetime import timedelta

def convert_duration(duration):
    """
    Convierte la duración en formato ISO 8601 (PT1H2M35S) a un formato estándar "hh:mm:ss".

    Args:
        duration (str): Duración en formato ISO 8601 (por ejemplo, PT1H2M35S).

    Returns:
        str: Duración en formato "hh:mm:ss".
    """
    # Expresión regular para capturar horas, minutos y segundos
    time_pattern = re.compile(r"PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?")
    match = time_pattern.match(duration)

    if match:
        hours = int(match.group(1) or 0)  # Si no hay horas, asignamos 0
        minutes = int(match.group(2) or 0)  # Si no hay minutos, asignamos 0
        seconds = int(match.group(3) or 0)  # Si no hay segundos, asignamos 0

        # Formateamos como hh:mm:ss
        return timedelta(hours=hours, minutes=minutes, seconds=seconds)
        #return f"{hours:02}:{minutes:02}:{seconds:02}"
    return "00:00:00"  # Si no se puede parsear, devolvemos "00:00:00"

def convert_published_date(published_at):
    """
    Convierte la fecha de publicación en formato ISO 8601 a un objeto datetime de Python en UTC.

    Args:
        published_at (str): Fecha de publicación en formato ISO 8601 (ej. "2024-12-09T10:30:00Z").

    Returns:
        datetime: Objeto datetime en formato adecuado para PostgreSQL, en UTC.
    """
    # Convertir la fecha en formato ISO 8601 a datetime con la zona horaria incluida
    dt = datetime.strptime(published_at, '%Y-%m-%dT%H:%M:%SZ')
    dt = pytz.utc.localize(dt)  # Asegura que el objeto datetime esté en UTC

    # Si ya tiene zona horaria (por ejemplo, UTC), se asegura de que esté en UTC
    if dt.tzinfo:
        return dt.astimezone(pytz.utc)  # Convertir a UTC, en caso que la zona horaria no sea UTC
    else:
        return dt  # Si ya está en UTC, no se hace ninguna conversión


def convert_views(views):
    """
    Convierte las vistas de YouTube a un número entero, asegurándose de que el valor no sea None o vacío.

    Args:
        views (str): Número de vistas como cadena.

    Returns:
        int: Número de vistas como entero.
    """
    try:
        return int(views)
    except (ValueError, TypeError):
        return 0  # Si el valor no es válido, se asigna 0


def clean_title(title, max_length=255):
    """
    Limpia el título del video para evitar caracteres problemáticos y lo trunca si es necesario.

    Args:
        title (str): Título del video.
        max_length (int): Longitud máxima del título en la base de datos.

    Returns:
        str: Título limpio y truncado.
    """
    # Eliminar caracteres problemáticos, si los hubiera
    title = title.replace("'", "''")  # Escapa comillas simples
    return title[:max_length]  # Trunca a la longitud máxima


def transform_video_data(video_data):
    """
    Aplica las transformaciones necesarias a los metadatos de los videos obtenidos de YouTube.

    Args:
        video_data (list): Lista de diccionarios con los metadatos de los videos.

    Returns:
        list: Lista de diccionarios con los metadatos transformados.
    """
    transformed_data = []

    for video in video_data:
        # Transformar cada campo de acuerdo con las funciones específicas
        video['title'] = clean_title(video['title'])
        video['views'] = convert_views(video['views'])
        video['duration'] = convert_duration(video['duration'])
        video['publishedAt'] = convert_published_date(video['publishedAt'])

        # Agregar el video transformado a la lista
        transformed_data.append(video)

    return transformed_data