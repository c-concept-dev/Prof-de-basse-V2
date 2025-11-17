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
    
    # Créer un index des mappings par method + page
    print("🔍 Création index par méthode + page...\n")
    mp3_by_method_page = {}
    
    for mapping in mp3_mapping['mappings']:
        method = mapping['method']
        page = mapping.get('exercise_page')
        title = mapping.get('exercise_title', '').lower()
        
        # Index par méthode + page
        key = f"{method}_{page}"
        if key not in mp3_by_method_page:
            mp3_by_method_page[key] = []
        
        mp3_by_method_page[key].append({
            'mp3_url': mapping['mp3_url'],
            'mp3_filename': mapping['mp3_filename'],
            'mp3_match_confidence': mapping['confidence'],
            'title': title
        })
    
    print(f"✅ Index créé : {len(mp3_by_method_page)} clés\n")
    
    # Mettre à jour les ressources
    updated_count = 0
    matched_examples = []
    
    for resource in megasearch['resources']:
        # Extraire méthode du metadata.book
        book = resource.get('metadata', {}).get('book', '')
        page = resource.get('page')
        resource_title = resource.get('title', '').lower()
        
        if not book or not page:
            continue
        
        # Chercher dans l'index
        key = f"{book}_{page}"
        
        if key in mp3_by_method_page:
            mp3_candidates = mp3_by_method_page[key]
            
            # Si plusieurs candidats, prendre le meilleur match par titre
            best_match = mp3_candidates[0]
            if len(mp3_candidates) > 1:
                for candidate in mp3_candidates:
                    if candidate['title'] and candidate['title'] in resource_title:
                        best_match = candidate
                        break
            
            # Créer/mettre à jour metadata
            if 'metadata' not in resource:
                resource['metadata'] = {}
            
            resource['metadata']['has_mp3'] = True
            resource['metadata']['mp3_url'] = best_match['mp3_url']
            resource['metadata']['mp3_filename'] = best_match['mp3_filename']
            resource['metadata']['mp3_match_confidence'] = best_match['mp3_match_confidence']
            
            updated_count += 1
            
            if updated_count <= 5:
                matched_examples.append({
                    'title': resource.get('title', 'Sans titre')[:60],
                    'book': book,
                    'page': page,
                    'mp3': best_match['mp3_filename']
                })
    
    # Afficher exemples
    if matched_examples:
        print("✅ EXEMPLES DE CORRESPONDANCES:\n")
        for ex in matched_examples:
            print(f"   {ex['title']}")
            print(f"   📚 {ex['book']} - Page {ex['page']}")
            print(f"   🎵 {ex['mp3']}\n")
    
    # Mettre à jour métadonnées globales
    if 'metadata' not in megasearch:
        megasearch['metadata'] = {}
    
    megasearch['metadata']['has_mp3_integration'] = True
    megasearch['metadata']['mp3_resources_count'] = updated_count
    megasearch['metadata']['mp3_match_rate'] = f"{(updated_count / len(megasearch['resources']) * 100):.1f}%"
    
    print(f"✅ {updated_count} ressources mises à jour avec MP3\n")
    
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
