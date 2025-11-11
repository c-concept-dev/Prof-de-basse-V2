#!/usr/bin/env python3
"""
Script pour fusionner automatiquement les conflits dans mega-search-index.json
Usage: python3 merge-json-conflict.py
"""

import json
import subprocess
import sys

def get_file_content(ref, filename):
    """Récupère le contenu d'un fichier depuis une ref Git"""
    try:
        result = subprocess.run(
            ['git', 'show', f'{ref}:{filename}'],
            capture_output=True,
            text=True,
            check=True
        )
        return json.loads(result.stdout)
    except Exception as e:
        print(f"❌ Erreur lors de la lecture de {ref}:{filename}: {e}")
        return None

def merge_search_indexes(ours, theirs):
    """Fusionne deux versions du mega-search-index.json"""
    
    # Créer un dict pour faciliter la fusion
    merged = {}
    
    # Ajouter toutes les entrées de 'ours'
    if 'resources' in ours:
        for resource in ours['resources']:
            key = resource.get('file_path', resource.get('title', ''))
            merged[key] = resource
    
    # Ajouter/mettre à jour avec les entrées de 'theirs'
    if 'resources' in theirs:
        for resource in theirs['resources']:
            key = resource.get('file_path', resource.get('title', ''))
            if key in merged:
                # Fusionner les métadonnées
                merged[key].update(resource)
            else:
                merged[key] = resource
    
    # Reconstruire le format final
    result = {
        'metadata': theirs.get('metadata', ours.get('metadata', {})),
        'resources': list(merged.values())
    }
    
    # Mettre à jour les stats
    result['metadata']['total_resources'] = len(result['resources'])
    
    return result

def main():
    filename = 'mega-search-index.json'
    
    print("🔧 Fusion automatique de mega-search-index.json")
    print()
    
    # Récupérer les deux versions
    print("📥 Récupération de la version locale (ours)...")
    ours = get_file_content('HEAD', filename)
    
    print("📥 Récupération de la version distante (theirs)...")
    theirs = get_file_content('origin/main', filename)
    
    if not ours or not theirs:
        print("❌ Impossible de récupérer les deux versions")
        sys.exit(1)
    
    print()
    print(f"📊 Version locale: {len(ours.get('resources', []))} ressources")
    print(f"📊 Version distante: {len(theirs.get('resources', []))} ressources")
    print()
    
    # Fusionner
    print("🔀 Fusion en cours...")
    merged = merge_search_indexes(ours, theirs)
    
    print(f"✅ Fusion réussie: {len(merged['resources'])} ressources")
    print()
    
    # Sauvegarder
    print(f"💾 Sauvegarde dans {filename}...")
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(merged, f, indent=2, ensure_ascii=False)
    
    print()
    print("✅ Fichier fusionné avec succès !")
    print()
    print("🔧 Commandes à exécuter maintenant:")
    print("   git add mega-search-index.json")
    print("   git rebase --continue")
    print("   git push origin main")

if __name__ == '__main__':
    main()
