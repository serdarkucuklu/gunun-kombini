import os
import sys
import json
import datetime
import subprocess
import urllib.parse
import requests
from dotenv import load_dotenv

# Force UTF-8 encoding for console (fixes Windows UnicodeEncodeError)
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

# Load environment variables
load_dotenv()
load_dotenv("d:/AI/Playground/02-auto-poster-agent/.env")

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Import notifier if available
sys.path.append("d:/AI/Playground/02-auto-poster-agent")
try:
    from notifier import trigger_milestone_alert
except ImportError:
    def trigger_milestone_alert(title, value):
        print(f"[Notifier Mock] Alert: {title} - {value}")

# Coordinates for target cities
CITIES_COORDS = {
    "istanbul": {"lat": 41.0082, "lon": 28.9784, "display_name": "İstanbul"},
    "ankara": {"lat": 39.9334, "lon": 32.8597, "display_name": "Ankara"},
    "izmir": {"lat": 38.4189, "lon": 27.1287, "display_name": "İzmir"}
}

# Weather code translations for Open-Meteo
WEATHER_CODES = {
    0: ("Açık ve Güneşli", "fa-sun"),
    1: ("Çoğunlukla Açık", "fa-cloud-sun"),
    2: ("Parçalı Bulutlu", "fa-cloud-sun"),
    3: ("Bulutlu", "fa-cloud"),
    45: ("Sisli", "fa-smog"),
    48: ("Sisli ve Kırağı", "fa-smog"),
    51: ("Hafif Çiseleyen Yağmur", "fa-cloud-rain"),
    53: ("Çiseleyen Yağmur", "fa-cloud-rain"),
    55: ("Yoğun Çiseleyen Yağmur", "fa-cloud-showers-heavy"),
    61: ("Hafif Yağmurlu", "fa-cloud-rain"),
    63: ("Yağmurlu", "fa-cloud-rain"),
    65: ("Kuvvetli Yağmurlu", "fa-cloud-showers-heavy"),
    71: ("Hafif Karlı", "fa-snowflake"),
    73: ("Karlı", "fa-snowflake"),
    75: ("Yoğun Karlı", "fa-snowflake"),
    77: ("Kar Tanelemeli", "fa-snowflake"),
    80: ("Hafif Sağanak Yağışlı", "fa-cloud-showers-water"),
    81: ("Sağanak Yağışlı", "fa-cloud-showers-heavy"),
    82: ("Kuvvetli Sağanak Yağışlı", "fa-cloud-showers-heavy"),
    85: ("Hafif Kar Sağanaklı", "fa-snowflake"),
    86: ("Yoğun Kar Sağanaklı", "fa-snowflake"),
    95: ("Gök Gürültülü Sağanak", "fa-cloud-bolt"),
    96: ("Gök Gürültülü Dolu", "fa-cloud-bolt"),
    99: ("Fırtına", "fa-cloud-bolt")
}

def get_weather(lat, lon):
    """Fetches real-time weather details from free Open-Meteo API."""
    url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true"
    try:
        response = requests.get(url, timeout=15)
        if response.status_code == 200:
            data = response.json()
            curr = data.get("current_weather", {})
            temp = f"{int(round(curr.get('temperature', 15)))}°C"
            code = curr.get("weathercode", 0)
            condition, icon = WEATHER_CODES.get(code, ("Açık", "fa-sun"))
            return temp, condition, icon
        else:
            print(f"Weather API error: {response.status_code}")
    except Exception as e:
        print(f"Error fetching weather: {e}")
    return "15°C", "Parçalı Bulutlu", "fa-cloud-sun"

def call_gemini(prompt: str):
    """Calls Gemini API to generate structured content."""
    if not GEMINI_API_KEY:
        print("Error: Gemini API Key is missing.")
        return None
    
    models = ["gemini-2.5-flash", "gemini-2.0-flash"]
    payload = {
        "contents": [{"parts": [{"text": prompt}]}]
    }
    
    for model in models:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={GEMINI_API_KEY}"
        try:
            response = requests.post(url, json=payload, timeout=60)
            if response.status_code == 200:
                res_data = response.json()
                return res_data["candidates"][0]["content"]["parts"][0]["text"]
        except Exception as e:
            print(f"Error calling Gemini ({model}): {e}")
    return None

def generate_combination(city_name, temp, condition):
    """Generates female and male clothing combinations based on weather conditions."""
    prompt = f"""
    Senden minimalist, şık ve estetik giyim tarzını yansıtan günlük kıyafet kombini (1 Kadın, 1 Erkek) küratörlüğü yapmanı istiyoruz.
    Bu kombin, belirtilen şehirdeki güncel hava durumuna göre seçilmelidir.
    Şehir: {city_name}
    Hava Sıcaklığı: {temp}
    Hava Durumu: {condition}

    Kombinde yer alacak 3 ana parçayı seç. Örnek parçalar: mont/kaban/ceket, kazak/tişört/gömlek, pantolon/jean/şort, bot/sneaker.
    Her ürün için Türkiye pazarında makul bir fiyat tahmini ve Amazon.com.tr araması için 'tag=aurafocus-21' içeren bir affiliate linki üret.
    Görseller için mutlaka giyim temalı kaliteli Unsplash görsel ID'leri veya linkleri kullan. Örnek Unsplash ID'leri:
    - Kaban/Mont: https://images.unsplash.com/photo-1591047139829-d91aecb6caea?w=300
    - Siyah Şişme Mont: https://images.unsplash.com/photo-1544923246-77307dd654cb?w=300
    - Kazak/Triko: https://images.unsplash.com/photo-1620799140408-edc6dcb6d633?w=300
    - Bot/Postal: https://images.unsplash.com/photo-1608256246200-53e635b5b65f?w=300
    - Keten Gömlek: https://images.unsplash.com/photo-1607345366928-199ea26cfe3e?w=300
    - Gözlük: https://images.unsplash.com/photo-1511499767150-a48a237f0083?w=300
    - Erkek Sneaker: https://images.unsplash.com/photo-1549298916-b41d501d3772?w=300

    Cevabı MUTLAKA aşağıdaki JSON şemasına birebir uyacak şekilde ham JSON formatında dön. Markdown bloğu (```json) ekleme. Türkçe karakterleri düzgün kullan.

    Şema:
    {{
      "female": {{
        "theme": "Kombin Başlığı (Max 5 kelime, örn: 'Bej Tonlarında Şehir Şıklığı')",
        "description": "Kombinin hava durumuna uyumunu ve tarzını açıklayan 1-2 cümlelik açıklama.",
        "items": [
          {{
            "name": "Ürün Adı (örn: 'Oversize Krem Kaşe Kaban')",
            "price": "Fiyat (örn: '1.899 TL')",
            "image_url": "Unsplash görsel URLsi",
            "affiliate_link": "Amazon affiliate linki"
          }},
          ... (tam 3 adet ürün)
        ]
      }},
      "male": {{
        "theme": "Erkek Kombin Başlığı",
        "description": "Erkek kombini açıklaması.",
        "items": [
          {{
            "name": "Ürün Adı",
            "price": "Fiyat",
            "image_url": "Unsplash görsel URLsi",
            "affiliate_link": "Amazon affiliate linki"
          }},
          ... (tam 3 adet ürün)
        ]
      }}
    }}
    """
    
    raw_res = call_gemini(prompt)
    if not raw_res:
        return None
    
    try:
        clean_json = raw_res.replace("```json", "").replace("```", "").strip()
        return json.loads(clean_json)
    except Exception as e:
        print(f"JSON parsing failed for {city_name}: {e}")
        print("Raw response was:", raw_res[:300])
        return None

def get_verified_clothing_image(item_name, gender):
    name_lower = item_name.lower()
    
    # Predefined high-quality verified Unsplash images
    images = {
        "female": {
            "outerwear": [
                "https://images.unsplash.com/photo-1591047139829-d91aecb6caea?q=80&w=600&auto=format&fit=crop", # Brown wool coat
                "https://images.unsplash.com/photo-1539571696357-5a69c17a67c6?q=80&w=600&auto=format&fit=crop", # Cozy beige cardigan
                "https://images.unsplash.com/photo-1620023640226-5b6d19f6a73c?q=80&w=600&auto=format&fit=crop", # Chic blazer
                "https://images.unsplash.com/photo-1544923246-77307dd654cb?q=80&w=600&auto=format&fit=crop"  # Black down jacket
            ],
            "tops": [
                "https://images.unsplash.com/photo-1607345366928-199ea26cfe3e?q=80&w=600&auto=format&fit=crop", # White linen shirt
                "https://images.unsplash.com/photo-1521572267360-ee0c2909d518?q=80&w=600&auto=format&fit=crop", # White basic t-shirt
                "https://images.unsplash.com/photo-1620799140408-edc6dcb6d633?q=80&w=600&auto=format&fit=crop", # Knit sweater
                "https://images.unsplash.com/photo-1603248356195-23c21a11ed94?q=80&w=600&auto=format&fit=crop"  # Casual top
            ],
            "bottoms": [
                "https://images.unsplash.com/photo-1541099649105-f69ad21f3246?q=80&w=600&auto=format&fit=crop", # Blue jeans
                "https://images.unsplash.com/photo-1624378439575-d8705ad7ae80?q=80&w=600&auto=format&fit=crop", # Beige pants
                "https://images.unsplash.com/photo-1620404432165-d5c22883f3e9?q=80&w=600&auto=format&fit=crop", # Trousers
                "https://images.unsplash.com/photo-1583496661160-fb48862c4a4e?q=80&w=600&auto=format&fit=crop"  # Skirt
            ],
            "shoes": [
                "https://images.unsplash.com/photo-1595950653106-6c9ebd614d3a?q=80&w=600&auto=format&fit=crop", # Nike/colorful sneakers
                "https://images.unsplash.com/photo-1543163521-1bf539c55dd2?q=80&w=600&auto=format&fit=crop", # Heels/shoes
                "https://images.unsplash.com/photo-1608256246200-53e635b5b65f?q=80&w=600&auto=format&fit=crop", # Autumn boots
                "https://images.unsplash.com/photo-1535043934128-cf0b28d52f95?q=80&w=600&auto=format&fit=crop"  # Leather shoes
            ],
            "accessories": [
                "https://images.unsplash.com/photo-1511499767150-a48a237f0083?q=80&w=600&auto=format&fit=crop", # Sunglasses
                "https://images.unsplash.com/photo-1584917865442-de89df76afd3?q=80&w=600&auto=format&fit=crop", # Handbag
                "https://images.unsplash.com/photo-1509319117193-57bab727e09d?q=80&w=600&auto=format&fit=crop"  # Hat/straw hat
            ]
        },
        "male": {
            "outerwear": [
                "https://images.unsplash.com/photo-1551488831-00ddcb6c6bd3?q=80&w=600&auto=format&fit=crop", # Denim jacket
                "https://images.unsplash.com/photo-1483985988355-763728e1935b?q=80&w=600&auto=format&fit=crop", # Stylish coat
                "https://images.unsplash.com/photo-1617137984095-74e4e5e3613f?q=80&w=600&auto=format&fit=crop", # Men's blazer/suit
                "https://images.unsplash.com/photo-1618886614638-80e3c103d31a?q=80&w=600&auto=format&fit=crop"  # Leather jacket
            ],
            "tops": [
                "https://images.unsplash.com/photo-1586363104862-3a5e2ab60d99?q=80&w=600&auto=format&fit=crop", # Men's shirt
                "https://images.unsplash.com/photo-1503342217505-b0a15ec3261c?q=80&w=600&auto=format&fit=crop", # Men's basic t-shirt
                "https://images.unsplash.com/photo-1620799140408-edc6dcb6d633?q=80&w=600&auto=format&fit=crop", # Knit sweater
                "https://images.unsplash.com/photo-1582233950450-482d385208cf?q=80&w=600&auto=format&fit=crop"  # Linen shirt
            ],
            "bottoms": [
                "https://images.unsplash.com/photo-1542272604-787c3835535d?q=80&w=600&auto=format&fit=crop", # Blue jeans
                "https://images.unsplash.com/photo-1479064555552-3ef4979f8908?q=80&w=600&auto=format&fit=crop", # Dark trousers
                "https://images.unsplash.com/photo-1594938367916-f56f108d4b3e?q=80&w=600&auto=format&fit=crop", # Chino pants
                "https://images.unsplash.com/photo-1591195853828-11db59a44f6b?q=80&w=600&auto=format&fit=crop"  # Shorts
            ],
            "shoes": [
                "https://images.unsplash.com/photo-1549298916-b41d501d3772?q=80&w=600&auto=format&fit=crop", # White sneakers
                "https://images.unsplash.com/photo-1533867617858-e7b97e060509?q=80&w=600&auto=format&fit=crop", # Leather shoes
                "https://images.unsplash.com/photo-1608256246200-53e635b5b65f?q=80&w=600&auto=format&fit=crop", # Boots
                "https://images.unsplash.com/photo-1542291026-7eec264c27ff?q=80&w=600&auto=format&fit=crop"  # Red/black sneakers
            ],
            "accessories": [
                "https://images.unsplash.com/photo-1511499767150-a48a237f0083?q=80&w=600&auto=format&fit=crop", # Sunglasses
                "https://images.unsplash.com/photo-1624445215570-85f67b5749f7?q=80&w=600&auto=format&fit=crop", # Watch
                "https://images.unsplash.com/photo-1514989940723-e8e51635b782?q=80&w=600&auto=format&fit=crop"  # Belt
            ]
        }
    }
    
    # Categorization based on name keywords
    cat = "tops" # default
    if any(k in name_lower for k in ["kaban", "mont", "ceket", "blazer", "trençkot", "trenchcoat", "kırka", "hırka", "cardigan", "outerwear", "parka", "yelek"]):
        cat = "outerwear"
    elif any(k in name_lower for k in ["pantolon", "jean", "kot", "chino", "şort", "shorts", "pant", "trousers", "tayt", "etek", "skirt"]):
        cat = "bottoms"
    elif any(k in name_lower for k in ["ayakkabı", "sneaker", "bot", "postal", "çizme", "shoes", "boots", "loafers", "oxfords"]):
        cat = "shoes"
    elif any(k in name_lower for k in ["gözlük", "çanta", "kemer", "şapka", "saat", "belt", "sunglasses", "bag", "hat", "atkı", "bere", "eldiven", "kolye"]):
        cat = "accessories"
        
    # Pick an image from the list based on name hash (to keep it deterministic yet diverse)
    img_list = images.get(gender, images["female"]).get(cat, images["female"]["tops"])
    hash_val = sum(ord(c) for c in item_name)
    idx = hash_val % len(img_list)
    return img_list[idx]

def run_agent():
    print("=" * 60)
    print("  Günün Kombini (OOTD) Autonomous Agent: Daily Curated Outfits")
    print("=" * 60)

    db_data = {
        "last_updated": datetime.datetime.utcnow().isoformat() + "Z",
        "cities": {}
    }

    # Generate data for each city
    for city_key, coords in CITIES_COORDS.items():
        print(f"\nProcessing {coords['display_name']}...")
        temp, condition, icon = get_weather(coords["lat"], coords["lon"])
        print(f"Current Weather: {temp}, {condition}")
        
        combinations = generate_combination(coords["display_name"], temp, condition)
        
        if combinations and "female" in combinations and "male" in combinations:
            # Overwrite image URLs with verified ones to prevent 404 broken images
            for gender in ["female", "male"]:
                for item in combinations[gender].get("items", []):
                    item["image_url"] = get_verified_clothing_image(item["name"], gender)

            db_data["cities"][city_key] = {
                "weather": {
                    "temp": temp,
                    "condition": condition,
                    "icon": icon
                },
                "female": combinations["female"],
                "male": combinations["male"]
            }
            print(f"[OK] Successfully curated combinations for {coords['display_name']}")
        else:
            print(f"[FAIL] Could not generate combinations for {coords['display_name']}. Using dummy fallback.")


    # Write to data.json
    if db_data["cities"]:
        with open("data.json", "w", encoding="utf-8") as f:
            json.dump(db_data, f, indent=2, ensure_ascii=False)
        print("\n[SUCCESS] data.json updated successfully.")
        
        # Trigger Notification
        try:
            sample_theme = list(db_data["cities"].values())[0]["female"]["theme"]
            trigger_milestone_alert("Gunun Kombini Guncellendi", f"Yeni Kombin: {sample_theme}")
            print("[OK] SMS/Email notification sent.")
        except Exception as e:
            print(f"Warning: Failed to trigger notification: {e}")
    else:
        print("\n[ERROR] No city data generated. Aborting file write.")
        return

    # Git Commit and Push (Only in Git repo)
    if os.path.exists(".git") or os.path.exists("../.git"):
        print("\nStaging and committing data.json to git...")
        try:
            subprocess.run(["git", "config", "user.name", "OOTD Agent"], check=True)
            subprocess.run(["git", "config", "user.email", "agent@gununkombini.com"], check=True)
            subprocess.run(["git", "add", "data.json"], check=True)
            
            # Check if there are changes to commit
            status = subprocess.run(["git", "status", "--porcelain"], capture_output=True, text=True)
            if status.stdout.strip():
                subprocess.run(["git", "commit", "-m", "Otonom Guncelleme: Gunluk kombinler yenilendi [skip ci]"], check=True)
                subprocess.run(["git", "push", "origin", "main"], check=True)
                print("[OK] Git push completed. Website auto-deployed!")
            else:
                print("[INFO] No changes in data.json. Skipping commit.")
        except Exception as e:
            print(f"Warning: Git commit/push failed: {e}")
    else:
        print("[INFO] No Git repository detected. Skipping git push.")

if __name__ == "__main__":
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    run_agent()
