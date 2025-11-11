#!/usr/bin/env python3
"""
Fix Empty URLs - Prof de Basse V3.0.2
Répare les URLs vides dans search-index-compatible.json
"""

import json
import urllib.parse
from pathlib import Path

BASE_URL = 'https://11drumboy11.github.io/Prof-de-basse-V2/'
BASE_PATH = 'Base de connaissances/Base de connaissances/'

def build_url(path):
    """Construit une URL complète et valide"""
    if not path:
        return ''
    
    # Construire le chemin complet
    full_path = BASE_PATH + path
    
    # Encoder chaque partie du chemin
    parts = full_path.split('/')
    encoded_parts = [urllib.parse.quote(part, safe='') for part in parts]
    
    # Construire l'URL finale
    url = BASE_URL + '/'.join(encoded_parts)
    
    return url

def fix_urls(input_file='search-index-compatible.json', output_file='megasearch.json'):
    """Répare les URLs dans le fichier JSON"""
    
    print("🔧 Réparation des URLs vides...")
    print(f"📂 Lecture de {input_file}...")
    
    # Charger le fichier
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"❌ Fichier {input_file} introuvable")
        return False
    except json.JSONDecodeError as e:
        print(f"❌ Erreur JSON: {e}")
        return False
    
    # Extraire les ressources
    resources = data.get('resources', [])
    print(f"📊 {len(resources)} ressources trouvées")
    
    # Compteurs
    fixed = 0
    already_ok = 0
    no_path = 0
    
    # Réparer chaque ressource
    print("\n🔄 Réparation en cours...")
    for resource in resources:
        url = resource.get('url', '')
        path = resource.get('path', '') or resource.get('filename', '')
        
        if not path:
            no_path += 1
            continue
        
        if url and url.strip():
            already_ok += 1
            continue
        
        # Générer l'URL
        new_url = build_url(path)
        resource['url'] = new_url
        fixed += 1
        
        if fixed <= 3:
            print(f"   ✅ [{fixed}] {resource.get('title', 'Sans titre')[:40]}")
            print(f"       Path: {path}")
            print(f"       URL:  {new_url[:80]}...")
    
    print(f"\n📊 Résultats:")
    print(f"   ✅ Réparées    : {fixed}")
    print(f"   ℹ️  Déjà OK     : {already_ok}")
    print(f"   ⚠️  Sans path  : {no_path}")
    
    # Sauvegarder
    print(f"\n💾 Sauvegarde dans {output_file}...")
    
    if 'metadata' not in data:
        data['metadata'] = {}
    
    if 'stats' not in data['metadata']:
        data['metadata']['stats'] = {}
    
    data['metadata']['stats']['total_resources'] = len(resources)
    data['metadata']['stats']['urls_fixed'] = fixed
    data['metadata']['version'] = '3.0.2'
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    file_size = Path(output_file).stat().st_size / 1024
    print(f"✅ Fichier sauvegardé: {file_size:.1f} KB")
    
    print(f"\n🔍 Vérification échantillon:")
    for i in range(min(3, len(resources))):
        resource = resources[i]
        url = resource.get('url', '')
        title = resource.get('title', 'Sans titre')[:40]
        
        if url.startswith('https://'):
            print(f"   ✅ [{i+1}] URL valide - {title}")
        else:
            print(f"   ❌ [{i+1}] URL invalide - {title}")
    
    print("\n🎉 RÉPARATION TERMINÉE !")
    return True

if __name__ == '__main__':
    import sys
    
    input_file = sys.argv[1] if len(sys.argv) > 1 else 'search-index-compatible.json'
    output_file = sys.argv[2] if len(sys.argv) > 2 else 'megasearch.json'
    
    success = fix_urls(input_file, output_file)
    sys.exit(0 if success else 1)
