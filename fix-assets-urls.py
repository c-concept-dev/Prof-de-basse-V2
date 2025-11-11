#!/usr/bin/env python3
"""
Corrige les URLs /assets/ dans mega-search-index.json
en les associant à leur dossier source _v4.0 correct
"""
import json
import re
from pathlib import Path

def fix_assets_urls():
    print("="*70)
    print("🔧 CORRECTION DES URLs /assets/")
    print("="*70 + "\n")
    
    # Charger le mega-search-index
    with open('mega-search-index.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    resources = data.get('resources', [])
    print(f"📊 Total ressources: {len(resources)}\n")
    
    # Compter les assets à corriger
    assets_count = sum(1 for r in resources if r.get('url', '').startswith('https://11drumboy11.github.io/Prof-de-basse-V2/assets/'))
    print(f"⚠️  URLs /assets/ à corriger: {assets_count}\n")
    
    if assets_count == 0:
        print("✅ Aucune correction nécessaire")
        return
    
    # Pour chaque ressource assets, on va essayer de retrouver son dossier source
    # en utilisant les métadonnées ou le source field
    
    fixed = 0
    errors = []
    
    for resource in resources:
        url = resource.get('url', '')
        
        if url.startswith('https://11drumboy11.github.io/Prof-de-basse-V2/assets/'):
            # Cette URL est invalide, il faut la reconstruire
            
            # Le ID contient souvent le chemin complet
            resource_id = resource.get('id', '')
            source = resource.get('source', '')
            
            # Essayer d'extraire le chemin depuis l'ID
            # Format typique: "Base%20de%20connaissances/Partitions/Realbook Bass F_v4.0/assets/pages/page_001.png"
            
            if resource_id:
                # L'ID est probablement le chemin complet
                # On reconstruit l'URL à partir de l'ID
                new_url = f"https://11drumboy11.github.io/Prof-de-basse-V2/{resource_id}"
                resource['url'] = new_url
                fixed += 1
            else:
                # Impossible de reconstruire
                errors.append({
                    'title': resource.get('title', 'N/A'),
                    'url': url,
                    'source': source
                })
    
    print(f"✅ URLs corrigées: {fixed}")
    
    if errors:
        print(f"\n⚠️  Erreurs ({len(errors)} ressources non corrigées):")
        for err in errors[:5]:
            print(f"   • {err['title']} (source: {err['source']})")
        if len(errors) > 5:
            print(f"   ... et {len(errors)-5} autres")
    
    # Sauvegarder
    with open('mega-search-index.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    print(f"\n💾 Fichier sauvegardé!\n")
    
    # Vérifier
    remaining = sum(1 for r in resources if r.get('url', '').startswith('https://11drumboy11.github.io/Prof-de-basse-V2/assets/'))
    
    print("="*70)
    if remaining == 0:
        print("✅ TOUTES LES URLs ASSETS CORRIGÉES")
    else:
        print(f"⚠️  {remaining} URLs /assets/ restantes")
    print("="*70)
    print()

if __name__ == '__main__':
    fix_assets_urls()
