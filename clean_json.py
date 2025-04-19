import json
import re
import os
import requests
from bs4 import BeautifulSoup

def fetch_raw_data(url, retries=3):
    """Web sitesinden ham JSON verisini çeker, BOM'u temizler."""
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    for attempt in range(retries):
        try:
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            # UTF-8 BOM'u temizlemek için utf-8-sig kullanıyoruz
            return response.content.decode('utf-8-sig')
        except requests.RequestException as e:
            write_error_log(f"Veri çekme hatası (Deneme {attempt+1}/{retries}): {str(e)}")
    raise Exception("Veri çekme başarısız.")

def clean_json_content(content):
    """JSON içeriğini temizler, 'var data =' önekini kaldırır."""
    content = re.sub(r'^var data =', '', content).strip()
    return content

def html_to_text(html_content):
    """HTML içeriğini sade metne çevirir."""
    if not html_content:
        return ""
    soup = BeautifulSoup(html_content, 'html.parser')
    # Script ve style etiketlerini kaldır
    for script in soup(["script", "style"]):
        script.decompose()
    # Metni al, fazla boşlukları temizle
    text = ' '.join(soup.stripped_strings)
    return text.strip()

def write_error_log(message, problematic_content=None):
    """Hata mesajını error_log.txt dosyasına yazar."""
    with open('error_log.txt', 'a', encoding='utf-8') as log_file:
        log_file.write(f"Hata: {message}\n")
        if problematic_content:
            log_file.write(f"Sorunlu içerik: {problematic_content}\n")
        log_file.write("-" * 50 + "\n")

def main():
    # Giriş ve çıkış dosyaları
    input_file = 'raw_response.txt'
    output_file = 'data-haberler.json'
    url = 'https://services.karabuk.bel.tr/jsons-karabukbeltr/data/data-haberler.json'

    # Hata günlüğünü sıfırla
    if os.path.exists('error_log.txt'):
        os.remove('error_log.txt')

    # Veriyi çek ve raw_response.txt dosyasına kaydet
    try:
        raw_content = fetch_raw_data(url)
        with open(input_file, 'w', encoding='utf-8') as file:
            file.write(raw_content)
    except Exception as e:
        write_error_log(f"Veri çekme veya kaydetme hatası: {str(e)}")
        raise

    # JSON içeriğini temizle
    cleaned_content = clean_json_content(raw_content)

    # JSON'u ayrıştır
    try:
        json_data = json.loads(cleaned_content)
        print("JSON başarıyla ayrıştırıldı!")
    except json.JSONDecodeError as e:
        error_message = f"JSON ayrıştırma hatası: {e.msg} (Satır: {e.lineno}, Sütun: {e.colno})"
        problematic_content = e.doc[max(0, e.pos-20):e.pos+20]
        write_error_log(error_message, problematic_content)
        raise

    # Haberleri filtrele ve dönüştür
    filtered_news = []
    for news in json_data.get('haberler', []):
        # haberkisa boşsa atla
        if not news.get('haberkisa'):
            continue
        # haberdetay'ı metne çevir
        detay_text = html_to_text(news.get('haberdetay', ''))
        # Yeni haber yapısı
        filtered_news.append({
            'kategoriadi': news.get('kategoriadi', ''),
            'haberresim': news.get('haberresim', ''),
            'haberbaslik': news.get('haberbaslik', ''),
            'haberkisa': news.get('haberkisa', ''),
            'tarih': news.get('tarih', ''),
            'detay_url': detay_text
        })

    # Filtrelenmiş JSON'u data-haberler.json dosyasına kaydet
    try:
        with open(output_file, 'w', encoding='utf-8') as outfile:
            json.dump(filtered_news, outfile, ensure_ascii=False, indent=2)
        print(f"JSON {output_file} dosyasına kaydedildi.")
    except Exception as e:
        write_error_log(f"JSON kaydetme hatası: {str(e)}")
        raise

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        write_error_log(str(e))
        raise
```
