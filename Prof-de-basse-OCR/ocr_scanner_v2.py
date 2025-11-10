#!/usr/bin/env python3
"""
OCR Scanner v2 - Prof de Basse
Détection intelligente : titres, compositeurs, techniques, tonalités
"""

import os
import re
import json
from pathlib import Path
from PIL import Image
import pytesseract

# ============================================================================
# CONFIGURATION
# ============================================================================

REPO_PATH = "/Users/christophebonnet/Documents/GitHub/Prof-de-basse"  # À MODIFIER
OUTPUT_JSON = "search_index_ocr.json"

# Dossiers à scanner
SCAN_DIRECTORIES = [
    "Methodes",
    "Partitions", 
    "Real_Books",
    "Exercises"
]

# Extensions d'images supportées
IMAGE_EXTENSIONS = {'.png', '.jpg', '.jpeg', '.pdf'}

# ============================================================================
# PATTERNS DE DÉTECTION MUSICALE
# ============================================================================

# Patterns pour titres de morceaux/exercices
TITLE_PATTERNS = [
    r'(?i)^(exercise|exercice|track|pattern|étude|study)\s*[#\d]+',
    r'(?i)^[\d]+[\.:\-\s]',  # Numéro au début
    r'(?i)(walking|slap|funk|jazz|blues|rock|disco|latin)',
    r'(?i)^\s*[A-Z][a-z]+(?:\s+[A-Z][a-z]+){0,4}\s*$',  # Titre propre
]

# Patterns pour compositeurs
COMPOSER_PATTERNS = [
    r'(?i)by\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+){0,2})',
    r'(?i)composed?\s+by\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+){0,2})',
    r'(?i)arr\.?\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+){0,2})',
    r'(?i)music\s+by\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+){0,2})',
]

# Compositeurs célèbres (reconnaissance directe)
KNOWN_COMPOSERS = {
    'james brown', 'stevie wonder', 'herbie hancock', 'miles davis',
    'john coltrane', 'charlie parker', 'dizzy gillespie', 'thelonious monk',
    'bill evans', 'oscar peterson', 'ray brown', 'paul chambers',
    'jaco pastorius', 'marcus miller', 'victor wooten', 'james jamerson',
    'bootsy collins', 'larry graham', 'bernard edwards', 'carol kaye',
    'george benson', 'wes montgomery', 'joe pass', 'pat metheny'
}

# Patterns pour techniques de basse
TECHNIQUE_PATTERNS = {
    'walking': [r'(?i)walking\s+bass', r'(?i)walking', r'(?i)walk'],
    'slap': [r'(?i)slap(?:ping)?', r'(?i)thumb', r'(?i)pop'],
    'funk': [r'(?i)funk(?:y)?', r'(?i)groove'],
    'ghost_notes': [r'(?i)ghost\s+notes?', r'(?i)muted\s+notes?', r'(?i)×'],
    'fingerstyle': [r'(?i)finger(?:style)?', r'(?i)pizzicato'],
    'pick': [r'(?i)pick(?:ing)?', r'(?i)plectrum'],
    'tapping': [r'(?i)tapp?ing', r'(?i)two\s+hand'],
    'harmonics': [r'(?i)harmonic', r'(?i)overtone'],
    'slide': [r'(?i)slide', r'(?i)glissando'],
}

# Patterns pour tonalités
KEY_PATTERNS = [
    r'\b([A-G][b#]?)\s*(?:maj(?:or)?|min(?:or)?|m(?!\w)|M(?!\w))?\b',
    r'(?i)in\s+([A-G][b#]?)',
    r'(?i)key\s+of\s+([A-G][b#]?)',
]

# Patterns pour tempo
TEMPO_PATTERNS = [
    r'♩\s*=\s*(\d+)',
    r'(?i)tempo:?\s*(\d+)',
    r'(?i)bpm:?\s*(\d+)',
    r'(?i)(\d+)\s*bpm',
]

# Patterns pour numéros de page/track
PAGE_PATTERNS = [
    r'(?i)page?\s*[:\-]?\s*(\d+)',
    r'(?i)p\.?\s*(\d+)',
    r'(?i)track\s+(\d+)',
]

# ============================================================================
# PRÉTRAITEMENT IMAGE (pour meilleur OCR)
# ============================================================================

def preprocess_image_for_ocr(image_path):
    """
    Améliore la qualité de l'image avant OCR :
    - Conversion grayscale
    - Augmentation contraste
    - Réduction bruit
    """
    try:
        img = Image.open(image_path)
        
        # Conversion grayscale
        img = img.convert('L')
        
        # Resize si trop petite (meilleur OCR sur images >300 DPI)
        width, height = img.size
        if width < 2000:
            scale = 2000 / width
            new_size = (int(width * scale), int(height * scale))
            img = img.resize(new_size, Image.Resampling.LANCZOS)
        
        return img
    except Exception as e:
        print(f"⚠️ Erreur prétraitement {image_path}: {e}")
        return Image.open(image_path)

# ============================================================================
# EXTRACTION OCR INTELLIGENTE
# ============================================================================

def extract_text_from_image(image_path, region='full'):
    """
    Extrait le texte d'une image avec OCR
    
    Args:
        image_path: Chemin vers l'image
        region: 'full' (toute l'image) ou 'top' (200px du haut pour titres)
    """
    try:
        img = preprocess_image_for_ocr(image_path)
        
        # Extraction selon région
        if region == 'top':
            width, height = img.size
            # Crop top 200px (zone titres)
            img = img.crop((0, 0, width, min(200, height)))
        
        # OCR avec Tesseract
        text = pytesseract.image_to_string(
            img,
            lang='eng+fra',  # Anglais + Français
            config='--psm 6'  # Assume uniform block of text
        )
        
        return text.strip()
    
    except Exception as e:
        print(f"⚠️ Erreur OCR {image_path}: {e}")
        return ""

# ============================================================================
# DÉTECTION DE PATTERNS
# ============================================================================

def detect_title(text):
    """Détecte le titre probable dans le texte OCR"""
    lines = [l.strip() for l in text.split('\n') if l.strip()]
    
    # Chercher dans les 3 premières lignes
    for line in lines[:3]:
        for pattern in TITLE_PATTERNS:
            if re.search(pattern, line):
                return line
    
    # Fallback : première ligne non-vide
    return lines[0] if lines else "Unknown"

def detect_composer(text):
    """Détecte le compositeur dans le texte"""
    text_lower = text.lower()
    
    # Chercher compositeurs connus
    for composer in KNOWN_COMPOSERS:
        if composer in text_lower:
            return composer.title()
    
    # Chercher patterns "by ..."
    for pattern in COMPOSER_PATTERNS:
        match = re.search(pattern, text)
        if match:
            return match.group(1).strip()
    
    return None

def detect_techniques(text):
    """Détecte les techniques de basse mentionnées"""
    detected = []
    text_lower = text.lower()
    
    for technique, patterns in TECHNIQUE_PATTERNS.items():
        for pattern in patterns:
            if re.search(pattern, text_lower):
                detected.append(technique)
                break
    
    return detected

def detect_key(text):
    """Détecte la tonalité"""
    for pattern in KEY_PATTERNS:
        match = re.search(pattern, text)
        if match:
            key = match.group(1)
            # Validation (A-G avec b ou #)
            if re.match(r'^[A-G][b#]?$', key):
                return key
    return None

def detect_tempo(text):
    """Détecte le tempo (BPM)"""
    for pattern in TEMPO_PATTERNS:
        match = re.search(pattern, text)
        if match:
            try:
                bpm = int(match.group(1))
                if 40 <= bpm <= 240:  # Validation tempo réaliste
                    return bpm
            except:
                pass
    return None

def detect_page_track(text, filename):
    """Détecte numéro de page/track"""
    # D'abord essayer depuis le nom de fichier
    filename_match = re.search(r'(?:track|page|p)[-_\s]*(\d+)', filename, re.I)
    if filename_match:
        return int(filename_match.group(1))
    
    # Sinon chercher dans le texte
    for pattern in PAGE_PATTERNS:
        match = re.search(pattern, text)
        if match:
            return int(match.group(1))
    
    return None

# ============================================================================
# SCANNER PRINCIPAL
# ============================================================================

def scan_directory(base_path):
    """
    Scanne récursivement un répertoire pour extraire métadonnées musicales
    """
    base_path = Path(base_path)
    results = []
    
    print(f"\n🔍 Scanning {base_path}...")
    
    for scan_dir in SCAN_DIRECTORIES:
        dir_path = base_path / scan_dir
        if not dir_path.exists():
            print(f"⚠️ Dossier non trouvé: {dir_path}")
            continue
        
        print(f"\n📂 Processing {scan_dir}...")
        
        # Récupérer tous les fichiers images
        for ext in IMAGE_EXTENSIONS:
            for image_file in dir_path.rglob(f'*{ext}'):
                print(f"  📄 {image_file.name}")
                
                # Extraction OCR (focus sur top pour titres)
                text_full = extract_text_from_image(str(image_file), region='full')
                text_top = extract_text_from_image(str(image_file), region='top')
                
                if not text_full:
                    continue
                
                # Détection métadonnées
                metadata = {
                    'file': str(image_file.relative_to(base_path)),
                    'filename': image_file.name,
                    'title': detect_title(text_top),
                    'composer': detect_composer(text_full),
                    'techniques': detect_techniques(text_full),
                    'key': detect_key(text_full),
                    'tempo': detect_tempo(text_full),
                    'page_track': detect_page_track(text_full, image_file.name),
                    'directory': scan_dir,
                    'ocr_confidence': 'high' if len(text_full) > 100 else 'low'
                }
                
                results.append(metadata)
                
                # Affichage résumé
                print(f"    ✅ Title: {metadata['title']}")
                if metadata['composer']:
                    print(f"    🎵 Composer: {metadata['composer']}")
                if metadata['techniques']:
                    print(f"    🎸 Techniques: {', '.join(metadata['techniques'])}")
                if metadata['key']:
                    print(f"    🔑 Key: {metadata['key']}")
                if metadata['tempo']:
                    print(f"    ⏱️ Tempo: {metadata['tempo']} BPM")
    
    return results

# ============================================================================
# SAUVEGARDE JSON
# ============================================================================

def save_to_json(results, output_file):
    """Sauvegarde les résultats en JSON propre"""
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    print(f"\n💾 Sauvegardé : {output_file}")
    print(f"📊 Total ressources : {len(results)}")

# ============================================================================
# STATISTIQUES
# ============================================================================

def print_statistics(results):
    """Affiche statistiques de qualité OCR"""
    total = len(results)
    with_composer = sum(1 for r in results if r['composer'])
    with_techniques = sum(1 for r in results if r['techniques'])
    with_key = sum(1 for r in results if r['key'])
    with_tempo = sum(1 for r in results if r['tempo'])
    
    print("\n" + "="*60)
    print("📊 STATISTIQUES OCR")
    print("="*60)
    print(f"Total ressources scannées : {total}")
    print(f"Avec compositeur détecté  : {with_composer} ({with_composer/total*100:.1f}%)")
    print(f"Avec techniques détectées : {with_techniques} ({with_techniques/total*100:.1f}%)")
    print(f"Avec tonalité détectée    : {with_key} ({with_key/total*100:.1f}%)")
    print(f"Avec tempo détecté        : {with_tempo} ({with_tempo/total*100:.1f}%)")
    print("="*60)

# ============================================================================
# MAIN
# ============================================================================

def main():
    print("🎸 Prof de Basse - OCR Scanner v2")
    print("="*60)
    
    # Scanner
    results = scan_directory(REPO_PATH)
    
    # Sauvegarder
    save_to_json(results, OUTPUT_JSON)
    
    # Statistiques
    print_statistics(results)
    
    print("\n✅ Scan terminé !")
    print(f"👉 Fichier généré : {OUTPUT_JSON}")

if __name__ == "__main__":
    main()
