#!/usr/bin/env python3
"""
Auto Update Index - Prof de Basse
Scan incrémental : détecte nouveaux fichiers et met à jour search_index.json
"""

import os
import json
import hashlib
from pathlib import Path
from datetime import datetime
from ocr_scanner_v2 import (
    extract_text_from_image, 
    detect_title, detect_composer, detect_techniques,
    detect_key, detect_tempo, detect_page_track,
    IMAGE_EXTENSIONS, SCAN_DIRECTORIES
)

# ============================================================================
# CONFIGURATION
# ============================================================================

REPO_PATH = "/Users/christophebonnet/Documents/GitHub/Prof-de-basse"  # À MODIFIER
INDEX_FILE = "search_index.json"
CACHE_FILE = "ocr_cache.json"  # Mémoriser fichiers déjà scannés

# ============================================================================
# GESTION CACHE
# ============================================================================

def load_cache():
    """Charge le cache des fichiers déjà scannés"""
    if os.path.exists(CACHE_FILE):
        with open(CACHE_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_cache(cache):
    """Sauvegarde le cache"""
    with open(CACHE_FILE, 'w') as f:
        json.dump(cache, f, indent=2)

def file_hash(filepath):
    """Calcule hash MD5 d'un fichier (pour détecter modifications)"""
    hasher = hashlib.md5()
    with open(filepath, 'rb') as f:
        buf = f.read(65536)  # 64kb chunks
        while len(buf) > 0:
            hasher.update(buf)
            buf = f.read(65536)
    return hasher.hexdigest()

# ============================================================================
# DÉTECTION NOUVEAUX FICHIERS
# ============================================================================

def find_new_files(base_path, cache):
    """
    Compare fichiers actuels avec cache
    Retourne : (nouveaux_fichiers, fichiers_modifiés)
    """
    base_path = Path(base_path)
    current_files = {}
    new_files = []
    modified_files = []
    
    print("🔍 Détection des nouveaux fichiers...")
    
    for scan_dir in SCAN_DIRECTORIES:
        dir_path = base_path / scan_dir
        if not dir_path.exists():
            continue
        
        # Scanner tous les fichiers images
        for ext in IMAGE_EXTENSIONS:
            for image_file in dir_path.rglob(f'*{ext}'):
                rel_path = str(image_file.relative_to(base_path))
                current_files[rel_path] = str(image_file)
                
                # Fichier nouveau ?
                if rel_path not in cache:
                    new_files.append(str(image_file))
                    print(f"  🆕 Nouveau : {image_file.name}")
                
                # Fichier modifié ?
                elif file_hash(image_file) != cache[rel_path].get('hash'):
                    modified_files.append(str(image_file))
                    print(f"  🔄 Modifié : {image_file.name}")
    
    return new_files, modified_files, current_files

# ============================================================================
# SCAN INCRÉMENTAL
# ============================================================================

def scan_file(image_path, base_path):
    """Scanne un seul fichier et retourne ses métadonnées"""
    image_path = Path(image_path)
    base_path = Path(base_path)
    
    print(f"  📄 Scanning {image_path.name}...")
    
    # Extraction OCR
    text_full = extract_text_from_image(str(image_path), region='full')
    text_top = extract_text_from_image(str(image_path), region='top')
    
    if not text_full:
        return None
    
    # Détection métadonnées
    metadata = {
        'file': str(image_path.relative_to(base_path)),
        'filename': image_path.name,
        'title': detect_title(text_top),
        'composer': detect_composer(text_full),
        'techniques': detect_techniques(text_full),
        'key': detect_key(text_full),
        'tempo': detect_tempo(text_full),
        'page_track': detect_page_track(text_full, image_path.name),
        'directory': image_path.parent.name,
        'ocr_confidence': 'high' if len(text_full) > 100 else 'low',
        'scanned_at': datetime.now().isoformat(),
        'hash': file_hash(image_path)
    }
    
    return metadata

def update_index_incremental(base_path):
    """
    Mise à jour incrémentale de l'index :
    1. Charge cache + index existant
    2. Détecte nouveaux/modifiés
    3. Scanne uniquement ces fichiers
    4. Fusionne avec index existant
    """
    base_path = Path(base_path)
    
    # Charger cache et index existant
    cache = load_cache()
    
    if os.path.exists(INDEX_FILE):
        with open(INDEX_FILE, 'r') as f:
            existing_index = json.load(f)
        print(f"📚 Index existant : {len(existing_index)} ressources")
    else:
        existing_index = []
        print("📚 Pas d'index existant, création nouveau")
    
    # Détecter nouveaux/modifiés
    new_files, modified_files, current_files = find_new_files(base_path, cache)
    
    total_to_scan = len(new_files) + len(modified_files)
    
    if total_to_scan == 0:
        print("\n✅ Aucun nouveau fichier détecté")
        return existing_index
    
    print(f"\n🔄 {total_to_scan} fichiers à scanner")
    print(f"  🆕 Nouveaux : {len(new_files)}")
    print(f"  🔄 Modifiés : {len(modified_files)}")
    
    # Scanner nouveaux fichiers
    new_metadata = []
    for filepath in new_files + modified_files:
        metadata = scan_file(filepath, base_path)
        if metadata:
            new_metadata.append(metadata)
    
    # Fusion avec index existant
    # Créer dict par file path pour faciliter update
    index_dict = {item['file']: item for item in existing_index}
    
    # Ajouter/remplacer nouvelles métadonnées
    for metadata in new_metadata:
        index_dict[metadata['file']] = metadata
    
    # Convertir back to list
    updated_index = list(index_dict.values())
    
    # Sauvegarder index mis à jour
    with open(INDEX_FILE, 'w', encoding='utf-8') as f:
        json.dump(updated_index, f, indent=2, ensure_ascii=False)
    
    # Mettre à jour cache
    new_cache = {}
    for file_path, abs_path in current_files.items():
        new_cache[file_path] = {
            'hash': file_hash(abs_path),
            'scanned_at': datetime.now().isoformat()
        }
    save_cache(new_cache)
    
    print(f"\n✅ Index mis à jour : {len(updated_index)} ressources")
    print(f"  📊 Ajoutées : {len(new_metadata)}")
    print(f"  💾 Fichier : {INDEX_FILE}")
    
    return updated_index

# ============================================================================
# STATISTIQUES
# ============================================================================

def print_statistics(index):
    """Affiche statistiques de l'index"""
    total = len(index)
    with_composer = sum(1 for r in index if r.get('composer'))
    with_techniques = sum(1 for r in index if r.get('techniques'))
    with_key = sum(1 for r in index if r.get('key'))
    with_tempo = sum(1 for r in index if r.get('tempo'))
    
    print("\n" + "="*60)
    print("📊 STATISTIQUES INDEX")
    print("="*60)
    print(f"Total ressources          : {total}")
    print(f"Avec compositeur détecté  : {with_composer} ({with_composer/total*100:.1f}%)")
    print(f"Avec techniques détectées : {with_techniques} ({with_techniques/total*100:.1f}%)")
    print(f"Avec tonalité détectée    : {with_key} ({with_key/total*100:.1f}%)")
    print(f"Avec tempo détecté        : {with_tempo} ({with_tempo/total*100:.1f}%)")
    print("="*60)

# ============================================================================
# MAIN
# ============================================================================

def main():
    print("🎸 Prof de Basse - Auto Update Index")
    print("="*60)
    print(f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Update incrémental
    updated_index = update_index_incremental(REPO_PATH)
    
    # Statistiques
    print_statistics(updated_index)
    
    print("\n✅ Mise à jour terminée !")

if __name__ == "__main__":
    main()
