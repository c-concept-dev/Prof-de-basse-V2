#!/usr/bin/env python3
"""
🎸 MegaSearch Generator - Prof de Basse
Script simple et robuste pour créer megasearch.json
"""

import json
import sys
from datetime import datetime
from pathlib import Path
import urllib.parse

def main():
    print("🎸 GÉNÉRATION MEGASEARCH.JSON")
    print("=" * 50)
    
    # Chercher tous les songs_index.json dans Base de connaissances
    base_dir = Path('Base de connaissances')
    
    if not base_dir.exists():
        print("❌ Dossier 'Base de connaissances' introuvable")
        return
    
    # Trouver tous les fichiers songs_index.json
    songs_files = list(base_dir.rglob('songs_index.json'))
    
    print(f"📁 Trouvé {len(songs_files)} fichiers songs_index.json")
    
    if not songs_files:
        print("❌ Aucun fichier trouvé")
        return
    
    resources = []
    base_url = 'https://11drumboy11.github.io/Prof-de-basse-V2/'
    
    for json_file in songs_files:
        print(f"\n📄 Traitement: {json_file.relative_to(base_dir)}")
        
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            metadata = data.get('metadata', {})
            content = data.get('content', {})
            
            book_title = metadata.get('bookTitle', json_file.parent.name)
            category = str(json_file.parent.parent.name)  # Methodes, Partitions, Theorie
            
            # Traiter les songs
            songs = content.get('songs', [])
            for song in songs:
                page = song.get('page')
                if page:
                    title = song.get('title', f'Page {page}')
                    composer = song.get('composer', '')
                    key = song.get('key', '')
                    
                    # URL vers l'image
                    path = f"Base de connaissances/{category}/{book_title}/assets/page_{page:03d}.png"
                    url = base_url + urllib.parse.quote(path, safe='/:.-_')
                    
                    # Texte de recherche
                    search_text = f"{title} {composer} {key} {book_title}".lower()
                    
                    resource = {
                        'id': f"{book_title}_{page}_{title}",
                        'type': 'song',
                        'title': title,
                        'page': page,
                        'url': url,
                        'metadata': {
                            'book': book_title,
                            'category': category,
                            'composer': composer,
                            'key': key
                        },
                        'searchText': search_text
                    }
                    resources.append(resource)
            
            # Traiter les exercises
            exercises = content.get('exercises', [])
            for exercise in exercises:
                page = exercise.get('page')
                if page:
                    title = exercise.get('title', f'Exercise Page {page}')
                    difficulty = exercise.get('difficulty', '')
                    technique = exercise.get('technique', '')
                    
                    path = f"Base de connaissances/{category}/{book_title}/assets/page_{page:03d}.png"
                    url = base_url + urllib.parse.quote(path, safe='/:.-_')
                    
                    search_text = f"{title} {difficulty} {technique} {book_title}".lower()
                    
                    resource = {
                        'id': f"{book_title}_{page}_{title}",
                        'type': 'exercise',
                        'title': title,
                        'page': page,
                        'url': url,
                        'metadata': {
                            'book': book_title,
                            'category': category,
                            'difficulty': difficulty,
                            'technique': technique
                        },
                        'searchText': search_text
                    }
                    resources.append(resource)
            
            # Traiter les concepts
            concepts = content.get('concepts', [])
            for concept in concepts:
                page = concept.get('page')
                if page:
                    concept_name = concept.get('concept', f'Concept Page {page}')
                    description = concept.get('description', '')
                    
                    path = f"Base de connaissances/{category}/{book_title}/assets/page_{page:03d}.png"
                    url = base_url + urllib.parse.quote(path, safe='/:.-_')
                    
                    search_text = f"{concept_name} {description} {book_title}".lower()
                    
                    resource = {
                        'id': f"{book_title}_{page}_{concept_name}",
                        'type': 'concept',
                        'title': concept_name,
                        'page': page,
                        'url': url,
                        'metadata': {
                            'book': book_title,
                            'category': category,
                            'description': description[:200]  # Limiter la description
                        },
                        'searchText': search_text
                    }
                    resources.append(resource)
            
            print(f"   ✅ {len(songs)} songs, {len(exercises)} exercises, {len(concepts)} concepts")
            
        except Exception as e:
            print(f"   ❌ Erreur: {e}")
    
    # Créer le megasearch.json final
    megasearch_data = {
        'metadata': {
            'version': '4.0.0',
            'generated_at': datetime.now().isoformat(),
            'total_resources': len(resources)
        },
        'resources': resources
    }
    
    # Sauvegarder
    with open('megasearch.json', 'w', encoding='utf-8') as f:
        json.dump(megasearch_data, f, ensure_ascii=False, indent=2)
    
    print(f"\n✅ MEGASEARCH.JSON CRÉÉ !")
    print(f"📊 Total ressources: {len(resources)}")
    print(f"📦 Fichier: megasearch.json")
    
    # Exemples d'URLs
    if resources:
        print(f"\n🔗 Exemples d'URLs:")
        for i, resource in enumerate(resources[:3], 1):
            print(f"   [{i}] {resource['title'][:50]}")
            print(f"       {resource['url']}")

if __name__ == '__main__':
    main()
