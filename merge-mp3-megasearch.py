#!/usr/bin/env python3
"""
🎵 Fusion MP3 Mapping dans Megasearch
Injecte les métadonnées MP3 du mp3_mapping.json dans megasearch.json
"""

import json
from pathlib import Path

def merge_mp3_into_megasearch():
    print("🔗 FUSION MP3 MAPPING → MEGASEARCH\n")
    
    # Charger les fichiers
    print("📂 Chargement des fichiers...")
    
    with open('megasearch.json', 'r', encoding='utf-8') as f:
        megasearch = json.load(f)
    
    with open('mp3_mapping.json', 'r', encoding='utf-8') as f:
        mp3_mapping = json.load(f)
    
    print(f"✅ Megasearch : {len(megasearch['resources'])} ressources")
    print(f"✅ MP3 Mapping : {len(mp3_mapping['mappings'])} mappings\n")
    
    # Créer un index des mappings par exercise_id
    mp3_by_id = {}
    for mapping in mp3_mapping['mappings']:
        exercise_id = mapping['exercise_id']
        mp3_by_id[exercise_id] = {
            'mp3_url': mapping['mp3_url'],
            'mp3_filename': mapping['mp3_filename'],
            'mp3_match_confidence': mapping['confidence']
        }
    
    # Mettre à jour les ressources
    updated_count = 0
    for resource in megasearch['resources']:
        resource_id = resource.get('id')
        
        if resource_id in mp3_by_id:
            mp3_info = mp3_by_id[resource_id]
            
            # Créer/mettre à jour metadata
            if 'metadata' not in resource:
                resource['metadata'] = {}
            
            resource['metadata']['has_mp3'] = True
            resource['metadata']['mp3_url'] = mp3_info['mp3_url']
            resource['metadata']['mp3_filename'] = mp3_info['mp3_filename']
            resource['metadata']['mp3_match_confidence'] = mp3_info['mp3_match_confidence']
            
            updated_count += 1
            
            if updated_count <= 5:
                print(f"✅ {resource.get('title', 'Sans titre')[:50]}")
                print(f"   → {mp3_info['mp3_filename']}")
    
    # Mettre à jour métadonnées globales
    if 'metadata' not in megasearch:
        megasearch['metadata'] = {}
    
    megasearch['metadata']['has_mp3_integration'] = True
    megasearch['metadata']['mp3_resources_count'] = updated_count
    megasearch['metadata']['mp3_match_rate'] = f"{(updated_count / len(megasearch['resources']) * 100):.1f}%"
    
    print(f"\n✅ {updated_count} ressources mises à jour avec MP3\n")
    
    # Sauvegarder
    with open('megasearch.json', 'w', encoding='utf-8') as f:
        json.dump(megasearch, f, indent=2, ensure_ascii=False)
    
    print("💾 megasearch.json sauvegardé\n")
    
    # Stats finales
    print("="*60)
    print("📊 RÉSUMÉ")
    print("="*60)
    print(f"📚 Total ressources      : {len(megasearch['resources'])}")
    print(f"🎵 Ressources avec MP3   : {updated_count}")
    print(f"📈 Taux de couverture    : {(updated_count / len(megasearch['resources']) * 100):.1f}%")
    print("="*60)

if __name__ == '__main__':
    merge_mp3_into_megasearch()
    print("\n✅ TERMINÉ !")
