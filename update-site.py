#!/usr/bin/env python3
"""
🎸 Prof de Basse - Site Update Automation
Version 2.0.0 - REWRITE COMPLET
Mise à jour automatique du site GitHub Pages

CHANGEMENTS MAJEURS :
- Code réécrit from scratch
- Logique simplifiée et robuste
- Dédoublonnage garanti par Set
- Support complet formats v1.0 et v4.0
"""

import os
import json
from pathlib import Path
from datetime import datetime
from urllib.parse import quote
from typing import Dict, List, Set

# ==========================================
# CONFIGURATION
# ==========================================

REPO_ROOT = Path.cwd()
BASE_DE_CONNAISSANCES = REPO_ROOT / "Base de connaissances"
OUTPUT_JSON = REPO_ROOT / "megasearch.json"
OUTPUT_HTML = REPO_ROOT / "index.html"
GITHUB_BASE_URL = "https://11drumboy11.github.io/Prof-de-basse-V2/"

# ==========================================
# CLASSE PRINCIPALE
# ==========================================

class SiteUpdater:
    def __init__(self):
        # Utiliser un SET pour garantir l'unicité par URL
        self.resources_by_url: Dict[str, Dict] = {}
        self.stats = {
            'total_methods': 0,
            'total_songs': 0,
            'total_exercises': 0,
            'total_pages': 0,
            'methods': []
        }
    
    def run(self):
        """Processus complet de mise à jour"""
        print("🎸 Prof de Basse - Mise à jour du site v2.0")
        print("=" * 60)
        
        # Étape 1 : Scanner et fusionner
        print("\n📂 Scan et fusion des données...")
        self.scan_and_merge()
        
        # Étape 2 : Générer megasearch.json
        print("\n📝 Génération megasearch.json...")
        self.generate_megasearch()
        
        # Étape 3 : Mettre à jour index.html
        print("\n🌐 Mise à jour index.html...")
        self.update_index_html()
        
        # Résumé
        print("\n" + "=" * 60)
        print("✅ MISE À JOUR TERMINÉE !")
        self.print_stats()
    
    def scan_and_merge(self):
        """Scanner tous les songs_index.json et fusionner"""
        
        if not BASE_DE_CONNAISSANCES.exists():
            print(f"⚠️  Dossier introuvable : {BASE_DE_CONNAISSANCES}")
            return
        
        # Parcourir tous les dossiers
        for songs_index_path in BASE_DE_CONNAISSANCES.rglob('songs_index.json'):
            method_dir = songs_index_path.parent
            method_name = method_dir.name
            
            print(f"   ✓ {method_name}")
            
            try:
                # Lire le JSON
                with open(songs_index_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                # Extraire les songs selon le format
                songs = self.extract_songs(data, method_name, method_dir)
                
                # Ajouter aux ressources (le Set garantit l'unicité)
                for song in songs:
                    url = song['url']
                    # Si l'URL existe déjà, on garde la première occurrence
                    if url not in self.resources_by_url:
                        self.resources_by_url[url] = song
                        self.stats['total_songs'] += 1
                
                # Compter les pages
                assets_dir = method_dir / 'assets' / 'pages'
                if assets_dir.exists():
                    page_count = len(list(assets_dir.glob('*.png')))
                    self.stats['total_pages'] += page_count
                
                # Ajouter à la liste des méthodes
                if method_name not in self.stats['methods']:
                    self.stats['methods'].append(method_name)
                    self.stats['total_methods'] += 1
                
            except Exception as e:
                print(f"   ⚠️  Erreur : {e}")
    
    def extract_songs(self, data: Dict, method_name: str, method_dir: Path) -> List[Dict]:
        """Extraire les songs en gérant tous les formats"""
        songs = []
        
        # Détecter le format
        if 'content' in data:
            # Format v1.0 : { "content": { "songs": [...] } }
            raw_songs = data.get('content', {}).get('songs', [])
            metadata = data.get('metadata', {})
            category = metadata.get('category', '')
            style = metadata.get('style', '')
        elif 'songs' in data:
            # Format v4.0 : { "songs": [...] }
            raw_songs = data.get('songs', [])
            metadata = data.get('metadata', {})
            category = metadata.get('category', '')
            style = metadata.get('style', '')
        else:
            return []
        
        # Traiter chaque song
        for song in raw_songs:
            # Extraire le numéro de page (gérer les 2 formats)
            page = song.get('page') or song.get('page_number', 0)
            
            # Skip si pas de page valide
            if not page or page == 0:
                continue
            
            # Construire l'URL
            rel_path = method_dir.relative_to(REPO_ROOT)
            img_path = rel_path / 'assets' / 'pages' / f'page_{page:03d}.png'
            path_str = str(img_path).replace('\\', '/')
            url = GITHUB_BASE_URL + quote(path_str, safe='/:.-_')
            
            # Créer la ressource
            resource = {
                'id': path_str,
                'path': path_str,
                'url': url,
                'type': 'image',
                'title': song.get('title', f'Page {page}'),
                'filename': f'page_{page:03d}.png',
                'metadata': {
                    'method': method_name,
                    'page': page,
                    'composer': song.get('composer', ''),
                    'key': song.get('key') or song.get('tonalite', ''),
                    'style': song.get('style') or style,
                    'category': song.get('category') or category,
                    'techniques': song.get('techniques', []),
                    'resource_type': 'song'
                }
            }
            
            songs.append(resource)
        
        return songs
    
    def generate_megasearch(self):
        """Générer le fichier megasearch.json"""
        
        # Convertir le dict en liste
        resources_list = list(self.resources_by_url.values())
        
        output_data = {
            'version': '2.0.0',
            'generated_at': datetime.now().isoformat(),
            'total': len(resources_list),
            'stats': {
                'total_pages': self.stats['total_pages'],
                'total_songs': self.stats['total_songs'],
                'total_methods': self.stats['total_methods'],
                'methods': sorted(self.stats['methods'])
            },
            'resources': resources_list
        }
        
        with open(OUTPUT_JSON, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, indent=2, ensure_ascii=False)
        
        file_size = OUTPUT_JSON.stat().st_size / (1024 * 1024)
        print(f"   ✓ {len(resources_list)} ressources indexées")
        print(f"   ✓ Taille : {file_size:.2f} MB")
    
    def update_index_html(self):
        """Mettre à jour les stats dans index.html"""
        
        if not OUTPUT_HTML.exists():
            print(f"   ⚠️  {OUTPUT_HTML} introuvable")
            return
        
        import re
        
        with open(OUTPUT_HTML, 'r', encoding='utf-8') as f:
            html = f.read()
        
        # Remplacer les stats (simplifié - match n'importe quel nombre)
        html = re.sub(r'(id="statTotal"[^>]*>)\d+', 
                     rf'\g<1>{self.stats["total_songs"]}', html)
        html = re.sub(r'(id="statImages"[^>]*>)\d+',
                     rf'\g<1>{self.stats["total_pages"]}', html)
        html = re.sub(r'(id="statMethods"[^>]*>)\d+',
                     rf'\g<1>{self.stats["total_methods"]}', html)
        html = re.sub(r'(id="footerTotal"[^>]*>)\d+',
                     rf'\g<1>{self.stats["total_songs"]}', html)
        
        with open(OUTPUT_HTML, 'w', encoding='utf-8') as f:
            f.write(html)
        
        print(f"   ✓ Stats actualisées")
    
    def print_stats(self):
        """Afficher les statistiques finales"""
        print(f"📊 Statistiques :")
        print(f"   - Ressources totales : {self.stats['total_songs']}")
        print(f"   - Pages totales : {self.stats['total_pages']}")
        print(f"   - Morceaux/Songs : {self.stats['total_songs']}")
        print(f"   - Méthodes : {self.stats['total_methods']}")
        print(f"\n📁 Fichiers générés :")
        print(f"   - {OUTPUT_JSON}")
        print(f"   - {OUTPUT_HTML}")

# ==========================================
# MAIN
# ==========================================

if __name__ == '__main__':
    try:
        updater = SiteUpdater()
        updater.run()
    except KeyboardInterrupt:
        print("\n\n⚠️  Interruption")
    except Exception as e:
        print(f"\n\n❌ ERREUR : {e}")
        import traceback
        traceback.print_exc()
