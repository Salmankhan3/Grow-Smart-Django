import requests
from django.conf import settings

class RAGError(Exception):
    pass

def query_rag(stage, crop_name=None, land_size=None, soil_type=None, 
              water_source=None,soil_moisture=None,last_ai_advice=None,Soil_pH=None,location=None,
              Agroecological_zone=None,
              humidity=None,pressure=None,wind_speed=None,temperature=None,last_rain=None,next_rain=None):

    url = settings.RAG_API_URL
    headers = {"X-API-Key": settings.RAG_API_KEY, "Content-Type": "application/json"}

    payload = {
        "crop_name": crop_name,
        "land_size": land_size,
        "soil_type": soil_type,
        "water_source": water_source,
        "soil_moisture": soil_moisture,
        "stage": int(stage),
        "last_ai_advice":last_ai_advice,
        "Soil_pH" : Soil_pH,
        "location":location,
        "Agroecological_zone":Agroecological_zone,
        "humidity":humidity,
        "pressure":pressure,
        "wind_speed":wind_speed,
        "temperature":str(temperature),
        "last_rain":last_rain,
        "next_rain":next_rain
    }
    print("Sending payload:", payload)
    try:
        r = requests.post(url, headers=headers, json=payload, timeout=60)
        if r.status_code != 200:
            raise RAGError(f"Bad response {r.status_code}: {r.text}")
        return r.json()
    except Exception as e:
        raise RAGError(f"Failed to contact RAG: {e}")
