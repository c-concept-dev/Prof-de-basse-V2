#!/usr/bin/env python3
"""
Correction COMPLÈTE de tous les chemins du repo
Ancienne structure → Nouvelle structure (Base de connaissances/)
"""
import json
import os
import re
from pathlib import Path

# Mappings complets de correction
PATH_MAPPINGS = {
    # MP3
    'Methodes/70%20Funk%20%26%20Disco%20bass%20MP3': 'Base%20de%20connaissances/MP3/70%20Funk%20%26%20Disco%20bass%20MP3',
    'Methodes/John%20Liebman%20Funk%20Fusion%20Mp3': 'Base%20de%20connaissances/MP3/John%20Liebman%20Funk%20Fusion%20Mp3',
    'Methodes/Paul%20westwood%20MP3': 'Base%20de%20connaissances/MP3/Paul%20westwood%20MP3',
    
    # Versions non-encodées (pour fichiers texte)
    'Methodes/70 Funk & Disco bass MP3': 'Base de connaissances/MP3/70 Funk & Disco bass MP3',
    'Methodes/John Liebman Funk Fusion Mp3': 'Base de connaissances/MP3/John Liebman Funk Fusion Mp3',
    'Methodes/Paul westwood MP3': 'Base de connaissances/MP3/Paul westwood MP3',
    
    # Méthodes PDF (si elles existent)
    'Methodes/': 'Base%20de%20connaissances/Methodes/',
    
    # Partitions
    'Partitions/': 'Base%20de%20connaissances/Partitions/',
    
    # Théorie
    'Theorie/': 'Base%20de%20connaissances/Theorie/',
}

def fix_json_file(filepath):
    """Corrige les chemins dans un fichier JSON"""
    print(f"\n🔧 {filepath}")
    
    if not os.path.exists(filepath):
        print(f"   ⚠️  Fichier non trouvé")
        return False
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        changes = 0
        
        # Appliquer tous les mappings
        for old_path, new_path in PATH_MAPPINGS.items():
            if old_path in content:
                occurrences = content.count(old_path)
                content = content.replace(old_path, new_path)
                changes += occurrences
                if occurrences > 0:
                    print(f"   ✅ {occurrences}× {old_path[:50]}...")
        
        if content != original_content:
            # Valider le JSON
            try:
                json.loads(content)
            except json.JSONDecodeError as e:
                print(f"   ❌ JSON invalide après modification : {e}")
                return False
            
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"   💾 Sauvegardé ({changes} modifications)")
            return True
        else:
            print(f"   ℹ️  Aucune modification")
            return False
            
    except Exception as e:
        print(f"   ❌ Erreur : {e}")
        return False

def fix_text_file(filepath):
    """Corrige les chemins dans un fichier texte/markdown/HTML"""
    print(f"\n🔧 {filepath}")
    
    if not os.path.exists(filepath):
        print(f"   ⚠️  Fichier non trouvé")
        return False
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        changes = 0
        
        # Appliquer tous les mappings (versions décodées pour texte)
        text_mappings = {
            'Methodes/70 Funk & Disco bass MP3': 'Base de connaissances/MP3/70 Funk & Disco bass MP3',
            'Methodes/John Liebman Funk Fusion Mp3': 'Base de connaissances/MP3/John Liebman Funk Fusion Mp3',
            'Methodes/Paul westwood MP3': 'Base de connaissances/MP3/Paul westwood MP3',
            '/Methodes/': '/Base de connaissances/Methodes/',
            '/Partitions/': '/Base de connaissances/Partitions/',
            '/Theorie/': '/Base de connaissances/Theorie/',
        }
        
        for old_path, new_path in text_mappings.items():
            if old_path in content:
                occurrences = content.count(old_path)
                content = content.replace(old_path, new_path)
                changes += occurrences
                if occurrences > 0:
                    print(f"   ✅ {occurrences}× {old_path[:50]}...")
        
        if content != original_content:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"   💾 Sauvegardé ({changes} modifications)")
            return True
        else:
            print(f"   ℹ️  Aucune modification")
            return False
            
    except Exception as e:
        print(f"   ❌ Erreur : {e}")
        return False

def main():
    print("="*70)
    print("🔧 CORRECTION COMPLÈTE DES CHEMINS")
    print("   Ancienne structure → Base de connaissances/")
    print("="*70)
    
    # Fichiers à corriger
    files_to_fix = [
        # JSON
        ('mega-search-index.json', 'json'),
        ('resources/complete-resource-map.json', 'json'),
        ('assets_ocr_index.json', 'json'),
        
        # Documentation
        ('README.md', 'text'),
        ('README-SYSTEM.md', 'text'),
        ('README-SEARCH-SYSTEM.md', 'text'),
        ('README-AUTO-OCR.md', 'text'),
        
        # HTML d'instructions
        ('prof-de-basse-core-system-v3-FINAL.html', 'text'),
        ('github-resources-complete-map-v3-CORRECTED.html', 'text'),
        ('mp3-inline-integration.html', 'text'),
        ('structure-pedagogique-5-parties-v2.html', 'text'),
        
        # Scripts Python
        ('fix-urls.py', 'text'),
        ('fix-repo-paths.py', 'text'),
        ('fusion-all-indexes.py', 'text'),
    ]
    
    fixed_count = 0
    for filepath, file_type in files_to_fix:
        if file_type == 'json':
            if fix_json_file(filepath):
                fixed_count += 1
        else:
            if fix_text_file(filepath):
                fixed_count += 1
    
    print("\n" + "="*70)
    print(f"✅ CORRECTION TERMINÉE : {fixed_count} fichiers modifiés")
    print("="*70)
    
    if fixed_count > 0:
        print("\n📝 PROCHAINES ÉTAPES :")
        print("\n1. Vérifier les modifications :")
        print("   git diff mega-search-index.json | head -50")
        
        print("\n2. Tester un MP3 :")
        print('   curl -I "https://11drumboy11.github.io/Prof-de-basse-V2/Base%20de%20connaissances/MP3/70%20Funk%20%26%20Disco%20bass%20MP3/Track%2001.mp3"')
        
        print("\n3. Commiter et pusher :")
        print("   git add .")
        print('   git commit -m "Fix: Correction COMPLÈTE des chemins vers Base de connaissances/"')
        print("   git push origin main")
        
        print("\n4. Re-vérifier le système :")
        print("   python3 verify-prof-basse.py")
    
    print()

if __name__ == '__main__':
    main()
