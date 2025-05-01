import requests

scene_data = {
    "Audio.source": "https://creatomate.com/files/assets/b5dc815e-dcc9-4c62-9405-f94913936bf5",
    "Image.source": "https://creatomate.com/files/assets/4a7903f0-37bc-48df-9d83-5eb52afd5d07",
    "Text.text": "Did you know you can automate TikTok, Instagram, and YouTube videos? 🔥",
}


url = "https://api.creatomate.com/v1/renders"
api_key = "cc88fd64563747ab9471aa06b4fec49e62d411e506dd924854588eabcc9a22bfcb82c42ea9c48c31366291b5d010f262"

data = {
    "template_id": "67e6b0f9-57fe-48d4-8470-8e3e6d0a5f03",
    "modifications": scene_data,
}

headers = {"Content-Type": "application/json", "Authorization": f"Bearer {api_key}"}

response = requests.post(url, json=data, headers=headers)
print(response.text)
