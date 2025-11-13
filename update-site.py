#!/usr/bin/env python3
"""
🎸 Prof de Basse - Site Update Automation
Version 1.5.0 - ULTIMATE FIX
Mise à jour automatique du site GitHub Pages
- Support des formats JSON v1.0 et v4.0
- Normalisation page_number → page
- Dédoublonnage automatique des morceaux
- Encodage URL correct avec urllib.parse.quote
- Dédoublonnage global par URL (supprime TOUS les doublons)
"""

import os
import json
import re
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any

# ==========================================
# CONFIGURATION
# ==========================================

REPO_ROOT = Path.cwd()  # Racine du repo GitHub
BASE_DE_CONNAISSANCES = REPO_ROOT / "Base de connaissances"
OUTPUT_JSON = REPO_ROOT / "megasearch.json"
OUTPUT_HTML = REPO_ROOT / "index.html"

GITHUB_BASE_URL = "https://11drumboy11.github.io/Prof-de-basse-V2/"

# Fichiers à supprimer (obsolètes)
DEPRECATED_FILES = [
    "mega-search-index-v2.json",
    "search-index-compatible.json",
    "assets_ocr_index.json"
]

# ==========================================
# CLASSE PRINCIPALE
# ==========================================

class SiteUpdater:
    def __init__(self):
        self.all_resources = []
        self.stats = {
            'total_resources': 0,
            'total_pages': 0,
            'total_songs': 0,
            'total_exercises': 0,
            'total_methods': 0,
            'methods': set()
        }
    
    def run(self):
        """Processus complet de mise à jour"""
        print("🎸 Prof de Basse - Mise à jour du site")
        print("=" * 50)
        
        # Étape 1 : Scanner les dossiers
        print("\n📂 Étape 1/5 : Scan des dossiers...")
        self.scan_base_de_connaissances()
        
        # Étape 2 : Fusionner les données
        print("\n🔀 Étape 2/5 : Fusion des données...")
        self.merge_all_indexes()
        
        # Étape 3 : Générer megasearch.json
        print("\n📝 Étape 3/5 : Génération de megasearch.json...")
        self.generate_megasearch_json()
        
        # Étape 4 : Mettre à jour index.html
        print("\n🌐 Étape 4/5 : Mise à jour de index.html...")
        self.update_index_html()
        
        # Étape 5 : Nettoyer les anciens fichiers
        print("\n🧹 Étape 5/5 : Nettoyage des fichiers obsolètes...")
        self.cleanup_deprecated_files()
        
        # Résumé final
        print("\n" + "=" * 50)
        print("✅ MISE À JOUR TERMINÉE !")
        print(f"📊 Statistiques :")
        print(f"   - Ressources totales : {self.stats['total_resources']}")
        print(f"   - Pages totales : {self.stats['total_pages']}")
        print(f"   - Morceaux/Songs : {self.stats['total_songs']}")
        print(f"   - Exercices : {self.stats['total_exercises']}")
        print(f"   - Méthodes scannées : {self.stats['total_methods']}")
        print(f"\n📁 Fichiers générés :")
        print(f"   - {OUTPUT_JSON}")
        print(f"   - {OUTPUT_HTML}")
    
    # ==========================================
    # SCAN DES DOSSIERS
    # ==========================================
    
    def scan_base_de_connaissances(self):
        """Scanner tous les sous-dossiers pour trouver les songs_index.json"""
        if not BASE_DE_CONNAISSANCES.exists():
            print(f"⚠️  Dossier introuvable : {BASE_DE_CONNAISSANCES}")
            return
        
        for root, dirs, files in os.walk(BASE_DE_CONNAISSANCES):
            root_path = Path(root)
            
            # Chercher songs_index.json
            if 'songs_index.json' in files:
                json_path = root_path / 'songs_index.json'
                method_name = root_path.name
                
                print(f"   ✓ Trouvé : {method_name}")
                
                self.stats['methods'].add(method_name)
                self.stats['total_methods'] += 1
    
    # ==========================================
    # FUSION DES INDEXES
    # ==========================================
    
    def merge_all_indexes(self):
        """Fusionner tous les songs_index.json en une seule structure"""
        
        for root, dirs, files in os.walk(BASE_DE_CONNAISSANCES):
            root_path = Path(root)
            
            if 'songs_index.json' in files:
                json_path = root_path / 'songs_index.json'
                
                try:
                    with open(json_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    
                    # NORMALISATION : Supporter les 2 formats
                    normalized_data = self.normalize_json_format(data, root_path)
                    
                    metadata = normalized_data['metadata']
                    method_name = metadata['method_name']
                    
                    # Traiter les songs (avec dédoublonnage)
                    songs = normalized_data['songs']
                    songs_dedup = self.deduplicate_songs(songs)
                    self.stats['total_songs'] += len(songs_dedup)
                    
                    for song in songs_dedup:
                        resource = self.create_resource_from_song(song, method_name, root_path)
                        self.all_resources.append(resource)
                    
                    # Traiter les exercises
                    exercises = normalized_data['exercises']
                    self.stats['total_exercises'] += len(exercises)
                    
                    for exercise in exercises:
                        resource = self.create_resource_from_exercise(exercise, method_name, root_path)
                        self.all_resources.append(resource)
                    
                    # NE PAS ajouter toutes les images (crée des doublons)
                    # Les images sont déjà référencées via songs et exercises
                    # On compte juste le nombre de pages pour les stats
                    assets_dir = root_path / 'assets' / 'pages'
                    if assets_dir.exists():
                        page_count = len(list(assets_dir.glob('*.png')))
                        self.stats['total_pages'] += page_count
                    
                    # Afficher warning si doublons détectés
                    if len(songs) != len(songs_dedup):
                        print(f"   ✓ {method_name} : {len(songs_dedup)} songs ({len(songs) - len(songs_dedup)} doublons supprimés), {len(exercises)} exercises")
                    else:
                        print(f"   ✓ {method_name} : {len(songs_dedup)} songs, {len(exercises)} exercises")
                    
                except Exception as e:
                    print(f"   ⚠️  Erreur lecture {json_path} : {e}")
        
        # DÉDOUBLONNAGE GLOBAL : Supprimer les ressources avec URL identique
        self.all_resources = self.deduplicate_resources_by_url(self.all_resources)
        
        self.stats['total_resources'] = len(self.all_resources)
    
    def normalize_json_format(self, data: Dict, root_path: Path) -> Dict:
        """Normaliser les différents formats JSON en un format unifié"""
        
        # FORMAT 1 : OCR Batch Converter v1.0 (nouveau)
        # Structure : { "metadata": {...}, "content": { "songs": [], "exercises": [] } }
        if 'content' in data:
            content = data['content']
            metadata = data.get('metadata', {})
            
            # Normaliser les songs
            songs = content.get('songs', [])
            normalized_songs = []
            for song in songs:
                # Normaliser page_number → page
                if 'page_number' in song and 'page' not in song:
                    song['page'] = song['page_number']
                normalized_songs.append(song)
            
            return {
                'metadata': {
                    'method_name': metadata.get('bookTitle', root_path.name),
                    'category': metadata.get('category', ''),
                    'style': metadata.get('style', ''),
                    'total_pages': metadata.get('totalPages', 0),
                    'version': '1.0.0'
                },
                'songs': normalized_songs,
                'exercises': content.get('exercises', []),
                'concepts': content.get('concepts', [])
            }
        
        # FORMAT 2 : V4.0 (ancien)
        # Structure : { "metadata": {...}, "songs": [], "exercises": [] }
        elif 'metadata' in data and 'songs' in data:
            metadata = data['metadata']
            
            # Normaliser les songs
            songs = data.get('songs', [])
            normalized_songs = []
            for song in songs:
                # Normaliser page_number → page
                if 'page_number' in song and 'page' not in song:
                    song['page'] = song['page_number']
                normalized_songs.append(song)
            
            return {
                'metadata': {
                    'method_name': metadata.get('method_name', root_path.name),
                    'category': metadata.get('category', ''),
                    'style': metadata.get('style', ''),
                    'total_pages': metadata.get('total_pages', 0),
                    'version': metadata.get('version', '4.0.0')
                },
                'songs': normalized_songs,
                'exercises': data.get('exercises', []),
                'concepts': data.get('concepts', [])
            }
        
        # FORMAT INCONNU : Retourner structure vide
        else:
            print(f"   ⚠️  Format JSON inconnu dans {root_path.name}")
            return {
                'metadata': {'method_name': root_path.name},
                'songs': [],
                'exercises': [],
                'concepts': []
            }
    
    def deduplicate_songs(self, songs: List[Dict]) -> List[Dict]:
        """Supprimer les doublons de morceaux (même titre + même page)"""
        seen = set()
        unique_songs = []
        
        for song in songs:
            # Clé unique : titre + page
            key = (song.get('title', ''), song.get('page', 0))
            
            if key not in seen:
                seen.add(key)
                unique_songs.append(song)
        
        return unique_songs
    
    def deduplicate_resources_by_url(self, resources: List[Dict]) -> List[Dict]:
        """Supprimer les ressources avec URL identique (dédoublonnage global)"""
        seen_urls = set()
        unique_resources = []
        duplicates_count = 0
        
        for resource in resources:
            url = resource.get('url', '')
            
            if url not in seen_urls:
                seen_urls.add(url)
                unique_resources.append(resource)
            else:
                duplicates_count += 1
        
        if duplicates_count > 0:
            print(f"\n   🧹 Dédoublonnage global : {duplicates_count} doublons d'URL supprimés")
        
        return unique_resources
        
        self.stats['total_resources'] = len(self.all_resources)
    
    def create_resource_from_song(self, song: Dict, method_name: str, root_path: Path) -> Dict:
        """Créer une ressource à partir d'un morceau"""
        page_num = song.get('page', 0)
        title = song.get('title', 'Untitled')
        
        # Construire le path relatif
        rel_path = root_path.relative_to(REPO_ROOT)
        img_path = rel_path / 'assets' / 'pages' / f'page_{page_num:03d}.png'
        
        # URL complète avec encodage correct
        from urllib.parse import quote
        path_str = str(img_path).replace('\\', '/')
        url = GITHUB_BASE_URL + quote(path_str, safe='/:.-_')
        
        return {
            'id': str(img_path).replace('\\', '/'),
            'path': str(img_path).replace('\\', '/'),
            'url': url,
            'type': 'image',
            'title': title,
            'filename': f'page_{page_num:03d}.png',
            'metadata': {
                'method': method_name,
                'page': page_num,
                'composer': song.get('composer', ''),
                'key': song.get('key', ''),
                'style': song.get('style', ''),
                'techniques': song.get('techniques', []),
                'ocr_text': song.get('ocr_text', ''),
                'resource_type': 'song'
            }
        }
    
    def create_resource_from_exercise(self, exercise: Dict, method_name: str, root_path: Path) -> Dict:
        """Créer une ressource à partir d'un exercice"""
        page_num = exercise.get('page', 0)
        title = exercise.get('title', 'Exercise')
        
        rel_path = root_path.relative_to(REPO_ROOT)
        img_path = rel_path / 'assets' / 'pages' / f'page_{page_num:03d}.png'
        
        # URL complète avec encodage correct
        from urllib.parse import quote
        path_str = str(img_path).replace('\\', '/')
        url = GITHUB_BASE_URL + quote(path_str, safe='/:.-_')
        
        return {
            'id': str(img_path).replace('\\', '/'),
            'path': str(img_path).replace('\\', '/'),
            'url': url,
            'type': 'image',
            'title': title,
            'filename': f'page_{page_num:03d}.png',
            'metadata': {
                'method': method_name,
                'page': page_num,
                'difficulty': exercise.get('difficulty', ''),
                'techniques': exercise.get('techniques', []),
                'ocr_text': exercise.get('ocr_text', ''),
                'resource_type': 'exercise'
            }
        }
    
    def create_resource_from_image(self, img_file: Path, method_name: str, root_path: Path) -> Dict:
        """Créer une ressource à partir d'une image de page"""
        rel_path = img_file.relative_to(REPO_ROOT)
        
        # URL complète avec encodage correct
        from urllib.parse import quote
        path_str = str(rel_path).replace('\\', '/')
        url = GITHUB_BASE_URL + quote(path_str, safe='/:.-_')
        
        # Extraire le numéro de page
        page_match = re.search(r'page_(\d+)', img_file.name)
        page_num = int(page_match.group(1)) if page_match else 0
        
        return {
            'id': str(rel_path).replace('\\', '/'),
            'path': str(rel_path).replace('\\', '/'),
            'url': url,
            'type': 'image',
            'title': img_file.stem,
            'filename': img_file.name,
            'size': img_file.stat().st_size,
            'modified': datetime.fromtimestamp(img_file.stat().st_mtime).isoformat(),
            'metadata': {
                'method': method_name,
                'page': page_num
            }
        }
    
    # ==========================================
    # GÉNÉRATION megasearch.json
    # ==========================================
    
    def generate_megasearch_json(self):
        """Générer le fichier megasearch.json unifié"""
        
        output_data = {
            'version': '3.0.0',
            'generated_at': datetime.now().isoformat(),
            'total': len(self.all_resources),
            'stats': {
                'total_pages': self.stats['total_pages'],
                'total_songs': self.stats['total_songs'],
                'total_exercises': self.stats['total_exercises'],
                'total_methods': self.stats['total_methods'],
                'methods': sorted(list(self.stats['methods']))
            },
            'resources': self.all_resources
        }
        
        with open(OUTPUT_JSON, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, indent=2, ensure_ascii=False)
        
        file_size = OUTPUT_JSON.stat().st_size / (1024 * 1024)
        print(f"   ✓ megasearch.json généré : {file_size:.2f} MB")
        print(f"   ✓ {len(self.all_resources)} ressources indexées")
    
    # ==========================================
    # MISE À JOUR index.html
    # ==========================================
    
    def update_index_html(self):
        """Mettre à jour les stats dans index.html"""
        
        if not OUTPUT_HTML.exists():
            print(f"   ⚠️  {OUTPUT_HTML} introuvable, création d'un nouveau fichier...")
            self.create_new_index_html()
            return
        
        # Lire le fichier existant
        with open(OUTPUT_HTML, 'r', encoding='utf-8') as f:
            html_content = f.read()
        
        # Remplacer les stats dans le header
        # Chercher les patterns comme <div class="stat-number" id="statTotal">XXXX</div>
        
        # Pattern pour statTotal (ligne ~621)
        html_content = re.sub(
            r'(<div class="stat-number" id="statTotal">)\d+(</div>)',
            rf'\g<1>{self.stats["total_resources"]}\g<2>',
            html_content
        )
        
        # Pattern pour statImages
        html_content = re.sub(
            r'(<div class="stat-number" id="statImages">)\d+(</div>)',
            rf'\g<1>{self.stats["total_pages"]}\g<2>',
            html_content
        )
        
        # Pattern pour statMethods
        html_content = re.sub(
            r'(<div class="stat-number" id="statMethods">)\d+(</div>)',
            rf'\g<1>{self.stats["total_methods"]}\g<2>',
            html_content
        )
        
        # Pattern pour footerTotal
        html_content = re.sub(
            r'(<span id="footerTotal">)\d+(</span>)',
            rf'\g<1>{self.stats["total_resources"]}\g<2>',
            html_content
        )
        
        # Ajouter un commentaire de mise à jour
        update_comment = f'\n<!-- Mis à jour automatiquement le {datetime.now().strftime("%Y-%m-%d %H:%M:%S")} par update-site.py -->\n'
        
        if '<!-- Mis à jour automatiquement' in html_content:
            # Remplacer l'ancien commentaire
            html_content = re.sub(
                r'<!-- Mis à jour automatiquement.*?-->',
                update_comment.strip(),
                html_content
            )
        else:
            # Ajouter le commentaire avant </head>
            html_content = html_content.replace('</head>', update_comment + '</head>')
        
        # Écrire le fichier
        with open(OUTPUT_HTML, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        print(f"   ✓ index.html mis à jour")
        print(f"   ✓ Stats actualisées : {self.stats['total_resources']} ressources")
    
    def create_new_index_html(self):
        """Créer un nouveau index.html si absent"""
        # Template HTML basique (optionnel, à développer si besoin)
        print("   ⚠️  Création de index.html non implémentée")
        print("   ℹ️  Veuillez créer index.html manuellement")
    
    # ==========================================
    # NETTOYAGE
    # ==========================================
    
    def cleanup_deprecated_files(self):
        """Supprimer les anciens fichiers JSON obsolètes"""
        
        for filename in DEPRECATED_FILES:
            file_path = REPO_ROOT / filename
            
            if file_path.exists():
                try:
                    file_path.unlink()
                    print(f"   ✓ Supprimé : {filename}")
                except Exception as e:
                    print(f"   ⚠️  Erreur suppression {filename} : {e}")
            else:
                print(f"   ℹ️  Déjà absent : {filename}")

# ==========================================
# MAIN
# ==========================================

if __name__ == '__main__':
    try:
        updater = SiteUpdater()
        updater.run()
    except KeyboardInterrupt:
        print("\n\n⚠️  Interruption par l'utilisateur")
    except Exception as e:
        print(f"\n\n❌ ERREUR : {e}")
        import traceback
        traceback.print_exc()
