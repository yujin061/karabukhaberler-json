```python
import json
import re
import os

def clean_json_content(content):
    """JSON içeriğini temizler, 'var data =' önekini kaldırır ve UTF-8 karakterleri korur."""
    # 'var data =' önekini kaldır
    content = re.sub(r'^var data =', '', content).strip()
    return content

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
    output_file = 'json_response.txt'
    
    # Hata günlüğünü sıfırla
    if os.path.exists('error_log.txt'):
        os.remove('error_log.txt')

    # Ham JSON dosyasını oku
    if not os.path.exists(input_file):
        write_error_log(f"Giriş dosyası {input_file} bulunamadı.")
        raise FileNotFoundError(f"{input_file} bulunamadı.")

    with open(input_file, 'r', encoding='utf-8') as file:
        raw_content = file.read()

    # JSON içeriğini temizle
    cleaned_content = clean_json_content(raw_content)

    # JSON'u ayrıştır ve doğrula
    try:
        json_data = json.loads(cleaned_content)
        print("JSON başarıyla ayrıştırıldı!")

        # Geçerli JSON'u dosyaya kaydet
        with open(output_file, 'w', encoding='utf-8') as outfile:
            json.dump(json_data, outfile, ensure_ascii=False, indent=2)
        print(f"JSON {output_file} dosyasına kaydedildi.")

    except json.JSONDecodeError as e:
        error_message = f"JSON ayrıştırma hatası: {e.msg} (Satır: {e.lineno}, Sütun: {e.colno})"
        problematic_content = e.doc[max(0, e.pos-20):e.pos+20]
        write_error_log(error_message, problematic_content)
        raise

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        write_error_log(str(e))
        raise
```
