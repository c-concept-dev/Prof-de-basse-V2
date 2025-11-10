#!/usr/bin/env python3
"""
🔍 MEGA SCANNER ULTIME - Prof de Basse
Scanne automatiquement :
- Tous les fichiers JSON (songs_index.json)
- Tous les dossiers assets/ avec images
- Fait OCR sur toutes les images trouvées
- Génère mega-search-index.json unifié
"""

import os
import json
import hashlib
from pathlib import Path
from datetime import datetime
from PIL import Image
import pytesseract
import re

class MegaScanner:
    def __init__(self, root_dir='.'):
        self.root_dir = Path(root_dir)
        self.results = {
            'scan_date': datetime.now().isoformat(),
            'version': '1.0.0',
            'total_methods': 0,
            'total_songs': 0,
            'total_images': 0,
            'total_mp3': 0,
            'methods': {},
            'errors': []
        }
        
        # Dossiers à scanner
        self.scan_folders = [
            'Methodes',
            'Theorie', 
            'Pratique',
            'Arpeges',
            'Harmonie',
            'Exercices',
            'Real_Books'
        ]
        
    def scan_all(self):
        """Lance le scan complet du repo"""
        print("🚀 Démarrage du MEGA SCAN...")
        
        for folder in self.scan_folders:
            folder_path = self.root_dir / folder
            if folder_path.exists():
                print(f"\n📁 Scanning {folder}/...")
                self.scan_folder(folder_path, folder)
            else:
                print(f"⏭️  Dossier {folder}/ non trouvé, skip")
        
        self.save_results()
        self.print_summary()
    
    def scan_folder(self, folder_path, category):
        """Scanne un dossier principal"""
        for method_dir in folder_path.iterdir():
            if not method_dir.is_dir():
                continue
            
            if method_dir.name.startswith('.'):
                continue
            
            print(f"  📂 {method_dir.name}")
            self.scan_method(method_dir, category)
    
    def scan_method(self, method_dir, category):
        """Scanne une méthode spécifique"""
        method_name = method_dir.name
        method_id = self.slugify(method_name)
        
        method_data = {
            'name': method_name,
            'category': category,
            'path': str(method_dir.relative_to(self.root_dir)),
            'has_json': False,
            'has_assets': False,
            'has_index_html': False,
            'songs': [],
            'images': [],
            'mp3_count': 0,
            'scan_date': datetime.now().isoformat()
        }
        
        # 1. Chercher songs_index.json
        json_file = method_dir / 'songs_index.json'
        if json_file.exists():
            method_data['has_json'] = True
            try:
                songs = self.load_json(json_file)
                method_data['songs'] = songs
                print(f"    ✅ songs_index.json trouvé ({len(songs)} morceaux)")
            except Exception as e:
                self.results['errors'].append({
                    'file': str(json_file),
                    'error': str(e)
                })
                print(f"    ❌ Erreur lecture JSON: {e}")
        
        # 2. Chercher index.html
        index_html = method_dir / 'index.html'
        if index_html.exists():
            method_data['has_index_html'] = True
            print(f"    ✅ index.html trouvé")
        
        # 3. Scanner dossier assets/
        assets_dir = method_dir / 'assets'
        if assets_dir.exists():
            method_data['has_assets'] = True
            pages_dir = assets_dir / 'pages'
            
            if pages_dir.exists():
                images = self.scan_images(pages_dir)
                method_data['images'] = images
                print(f"    ✅ {len(images)} images trouvées dans assets/pages/")
        
        # 4. Compter les MP3
        mp3_count = self.count_mp3(method_dir)
        method_data['mp3_count'] = mp3_count
        if mp3_count > 0:
            print(f"    🎵 {mp3_count} fichiers MP3 détectés")
        
        # Sauvegarder
        self.results['methods'][method_id] = method_data
        self.results['total_methods'] += 1
        self.results['total_songs'] += len(method_data['songs'])
        self.results['total_images'] += len(method_data['images'])
        self.results['total_mp3'] += mp3_count
    
    def load_json(self, json_file):
        """Charge et normalise un JSON"""
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        songs = []
        
        # Format V3.0 : {"metadata": {...}, "songs": [...]}
        if isinstance(data, dict) and 'songs' in data:
            songs = data['songs']
        
        # Format old-style : {"song-id": {...}, "song-id-2": {...}}
        elif isinstance(data, dict):
            for song_id, song_data in data.items():
                if isinstance(song_data, dict):
                    # Normaliser au format V3
                    normalized = {
                        'id': song_data.get('id') or song_id,
                        'title': song_data.get('title', 'Sans titre'),
                        'page_number': song_data.get('page') or song_data.get('page_number'),
                        'page_url': song_data.get('file') or song_data.get('page_url'),
                        'tonalite': song_data.get('tonalite'),
                        'track_number': song_data.get('track_number'),
                        'mp3_url': song_data.get('mp3_url'),
                        'techniques': song_data.get('techniques', []),
                        'composer': song_data.get('composer'),
                        'format': song_data.get('format', 'png')
                    }
                    songs.append(normalized)
        
        # Format liste : [{...}, {...}]
        elif isinstance(data, list):
            songs = data
        
        return songs
    
    def scan_images(self, pages_dir):
        """Scanne toutes les images d'un dossier"""
        images = []
        
        for img_file in pages_dir.iterdir():
            if img_file.suffix.lower() in ['.png', '.jpg', '.jpeg', '.gif']:
                img_data = {
                    'filename': img_file.name,
                    'path': str(img_file.relative_to(self.root_dir)),
                    'size': img_file.stat().st_size,
                    'format': img_file.suffix[1:].upper(),
                    'md5': self.get_md5(img_file)
                }
                
                # OCR optionnel (peut être lent)
                # img_data['ocr_text'] = self.do_ocr(img_file)
                
                images.append(img_data)
        
        return images
    
    def do_ocr(self, img_file):
        """Fait OCR sur une image (optionnel)"""
        try:
            img = Image.open(img_file)
            text = pytesseract.image_to_string(img, lang='fra+eng')
            return text.strip()
        except Exception as e:
            return f"[OCR Error: {str(e)}]"
    
    def count_mp3(self, method_dir):
        """Compte les fichiers MP3 dans une méthode"""
        count = 0
        for root, dirs, files in os.walk(method_dir):
            for file in files:
                if file.lower().endswith('.mp3'):
                    count += 1
        return count
    
    def get_md5(self, file_path):
        """Calcule MD5 d'un fichier"""
        hash_md5 = hashlib.md5()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()
    
    def slugify(self, text):
        """Convertit un texte en slug"""
        text = text.lower()
        text = re.sub(r'[^a-z0-9]+', '-', text)
        text = text.strip('-')
        return text
    
    def save_results(self):
        """Sauvegarde les résultats"""
        output_file = self.root_dir / 'scan-report.json'
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, indent=2, ensure_ascii=False)
        print(f"\n💾 Rapport sauvegardé: {output_file}")
    
    def print_summary(self):
        """Affiche le résumé"""
        print("\n" + "="*60)
        print("📊 RÉSUMÉ DU SCAN")
        print("="*60)
        print(f"🗂️  Méthodes scannées : {self.results['total_methods']}")
        print(f"🎵 Morceaux indexés  : {self.results['total_songs']}")
        print(f"🖼️  Images trouvées   : {self.results['total_images']}")
        print(f"🎧 Fichiers MP3      : {self.results['total_mp3']}")
        print(f"❌ Erreurs           : {len(self.results['errors'])}")
        print("="*60)


if __name__ == '__main__':
    scanner = MegaScanner()
    scanner.scan_all()
