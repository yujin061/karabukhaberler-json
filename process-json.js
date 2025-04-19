const fs = require('fs');
const iconv = require('iconv-lite');
const cheerio = require('cheerio');
const axios = require('axios');

// Türkçe karakter eşleme tablosu
const characterMap = {
  'Ç': 'Ç', 'ç': 'ç',
  'Ö': 'Ö', 'ö': 'ö',
  'Ü': 'Ü', 'ü': 'ü',
  '&Guml;': 'Ğ', '&guml;': 'ğ',
  'Ï': 'İ', 'ï': 'ı',
  'Ş': 'Ş', 'ş': 'ş',
  '’': "'", ' ': ' ',
  '"': '"', '&': '&',
  '<': '<', '>': '>',
};

// HTML'den metni çıkar ve karakterleri düzelt
function cleanHtml(html) {
  try {
    const $ = cheerio.load(html);
    let text = $('body').text().replace(/\s+/g, ' ').trim();
    for (const [entity, char] of Object.entries(characterMap)) {
      text = text.replace(new RegExp(entity, 'g'), char);
    }
    // Diğer HTML varlıklarını kaldır
    text = text.replace(/&[^;]*;/g, '');
    return text;
  } catch (error) {
    console.error('HTML temizleme hatası:', error.message);
    return '';
  }
}

// Ana işlem
async function processJson() {
  try {
    // Ham veriyi oku
    const rawData = fs.readFileSync('raw.json');
    let jsonStr = iconv.decode(rawData, 'win1254'); // WINDOWS-1254 varsayımı

    // "var data =" ve sonundaki ";" temizle
    jsonStr = jsonStr.replace(/^var data =\s*/, '').replace(/;\s*$/, '');

    // JSON'a parse et
    let data;
    try {
      data = JSON.parse(jsonStr);
    } catch (error) {
      console.error('JSON parse hatası:', error.message);
      throw error;
    }

    // Temizlenmiş JSON'u kaydet (debug için)
    fs.writeFileSync('cleaned.json', JSON.stringify(data, null, 2), 'utf8');

    // Haberleri filtrele ve dönüştür
    const filteredNews = data.haberler
      .filter(item => item.haberkisa && item.haberkisa.trim() !== '')
      .map(item => ({
        kategoriadi: item.kategoriadi,
        haberresim: item.haberresim,
        haberbaslik: item.haberbaslik,
        haberkisa: item.haberkisa,
        tarih: item.tarih,
        detay_url: cleanHtml(item.haberdetay),
      }));

    // Son JSON'u kaydet
    fs.writeFileSync('data-haberler.json', JSON.stringify(filteredNews, null, 2), 'utf8');
    console.log('JSON başarıyla işlendi ve data-haberler.json oluşturuldu.');
  } catch (error) {
    console.error('Hata:', error.message);
    process.exit(1);
  }
}

processJson();
