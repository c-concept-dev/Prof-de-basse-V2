#!/usr/bin/env python3
"""
Diagnostic complet de la structure du repo Prof de Basse V2
Compare la structure réelle vs la structure attendue dans les URLs
"""
import os
import json
import re
from pathlib import Path

def scan_directory_structure():
    """Scan la structure réelle du repo"""
    print("🔍 SCAN DE LA STRUCTURE RÉELLE DU REPO")
    print("="*70 + "\n")
    
    base_paths = [
        "Base de connaissances",
        "Methodes",
        "resources",
        "assets"
    ]
    
    structure = {}
    
    for base in base_paths:
        if os.path.exists(base):
            print(f"📁 {base}/")
            structure[base] = []
            
            for root, dirs, files in os.walk(base):
                level = root.replace(base, '').count(os.sep)
                indent = ' ' * 2 * level
                folder_name = os.path.basename(root)
                
                if level < 3:  # Limiter la profondeur d'affichage
                    print(f'{indent}├── {folder_name}/')
                    structure[base].append(root)
                    
                    # Afficher quelques fichiers d'exemple
                    if files and level < 2:
                        for file in files[:3]:
                            print(f'{indent}│   └── {file}')
                        if len(files) > 3:
                            print(f'{indent}│   └── ... (+{len(files)-3} fichiers)')
            print()
    
    return structure

def analyze_mega_search_index():
    """Analyse les chemins dans mega-search-index.json"""
    print("\n" + "="*70)
    print("🔍 ANALYSE DES CHEMINS DANS mega-search-index.json")
    print("="*70 + "\n")
    
    try:
        with open('mega-search-index.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        resources = data.get('resources', [])
        
        # Extraire tous les chemins uniques
        url_patterns = {}
        for resource in resources:
            url = resource.get('url', '')
            if url:
                # Extraire le début du chemin (jusqu'au 3ème /)
                match = re.search(r'Prof-de-basse-V2/(.*?)/', url)
                if match:
                    base_path = match.group(1)
                    url_patterns[base_path] = url_patterns.get(base_path, 0) + 1
        
        print("📊 Chemins trouvés dans les URLs :")
        for path, count in sorted(url_patterns.items(), key=lambda x: x[1], reverse=True):
            print(f"   • {path}: {count} occurrences")
        
        return url_patterns
        
    except FileNotFoundError:
        print("⚠️  mega-search-index.json non trouvé")
        return {}
    except Exception as e:
        print(f"❌ Erreur : {e}")
        return {}

def compare_structures():
    """Compare structure réelle vs URLs"""
    print("\n" + "="*70)
    print("🔍 COMPARAISON STRUCTURE RÉELLE VS URLs")
    print("="*70 + "\n")
    
    # Structures attendues dans les URLs (anciennes)
    expected = {
        "Methodes": [
            "70 Funk & Disco bass MP3",
            "John Liebman Funk Fusion Mp3",
            "Paul westwood MP3"
        ],
        "Partitions": [
            "Real Books",
            "Fake Books"
        ],
        "Theorie": []
    }
    
    # Structure réelle
    actual = {
        "Base de connaissances/MP3": [
            "70 Funk & Disco bass MP3",
            "John Liebman Funk Fusion Mp3",
            "Paul westwood MP3"
        ],
        "Base de connaissances/Methodes": [],
        "Base de connaissances/Partitions": [],
        "Base de connaissances/Theorie": []
    }
    
    print("❌ STRUCTURE ATTENDUE (dans les URLs actuelles) :")
    for base, items in expected.items():
        print(f"\n   {base}/")
        if items:
            for item in items:
                print(f"      └── {item}/")
    
    print("\n\n✅ STRUCTURE RÉELLE (dans le repo) :")
    for base, items in actual.items():
        print(f"\n   {base}/")
        if items:
            for item in items:
                print(f"      └── {item}/")

def generate_correction_mappings():
    """Génère les mappings de correction"""
    print("\n" + "="*70)
    print("🔧 MAPPINGS DE CORRECTION À APPLIQUER")
    print("="*70 + "\n")
    
    mappings = [
        ("Methodes/70%20Funk%20%26%20Disco%20bass%20MP3", 
         "Base%20de%20connaissances/MP3/70%20Funk%20%26%20Disco%20bass%20MP3"),
        ("Methodes/John%20Liebman%20Funk%20Fusion%20Mp3", 
         "Base%20de%20connaissances/MP3/John%20Liebman%20Funk%20Fusion%20Mp3"),
        ("Methodes/Paul%20westwood%20MP3", 
         "Base%20de%20connaissances/MP3/Paul%20westwood%20MP3"),
    ]
    
    print("URLs à corriger :\n")
    for old, new in mappings:
        print(f"❌ {old}")
        print(f"✅ {new}\n")
    
    return mappings

def main():
    print("\n" + "="*70)
    print("🎸 DIAGNOSTIC COMPLET - STRUCTURE REPO")
    print("="*70 + "\n")
    
    # 1. Scanner la structure réelle
    structure = scan_directory_structure()
    
    # 2. Analyser mega-search-index
    url_patterns = analyze_mega_search_index()
    
    # 3. Comparer
    compare_structures()
    
    # 4. Générer les mappings
    mappings = generate_correction_mappings()
    
    print("\n" + "="*70)
    print("📝 RÉSUMÉ")
    print("="*70 + "\n")
    print("Le repo utilise la structure 'Base de connaissances/' mais les URLs")
    print("dans mega-search-index.json et les fichiers d'instructions pointent")
    print("vers l'ancienne structure 'Methodes/', 'Partitions/', etc.")
    print("\n✅ Solution : Exécuter fix-mp3-paths.py (version étendue)")
    print()

if __name__ == '__main__':
    main()
