#!/usr/bin/env python3
"""
🎸 MegaSearch Generator FINAL - Prof de Basse
Script final avec chemins corrects vers assets/pages/
"""

import json
import sys
from datetime import datetime
from pathlib import Path
import urllib.parse

def main():
    print("🎸 GÉNÉRATION MEGASEARCH.JSON - VERSION FINALE")
    print("=" * 60)
    
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
            
            # Utiliser le nom exact du dossier
            book_title = json_file.parent.name  # Ex: "Realbook Bass F_v4.0"
            category = json_file.parent.parent.name  # Ex: "Partitions"
            
            print(f"   📁 Catégorie: {category}")
            print(f"   📚 Livre: {book_title}")
            
            # Traiter les songs
            songs = content.get('songs', [])
            for song in songs:
                page = song.get('page')
                if page:
                    title = song.get('title', f'Page {page}')
                    composer = song.get('composer', '') or ''
                    key = song.get('key', '') or ''
                    
                    # CORRECTION FINALE : assets/pages/ au lieu de assets/
                    path = f"Base de connaissances/{category}/{book_title}/assets/pages/page_{page:03d}.png"
                    encoded_path = path.replace(' ', '%20')
                    url = base_url + encoded_path
                    
                    # Texte de recherche enrichi
                    search_parts = [title, composer, key, book_title, category]
                    search_text = ' '.join(filter(None, search_parts)).lower()
                    
                    resource = {
                        'id': f"{book_title}_{page}_{len(resources)}",
                        'type': 'song',
                        'title': title,
                        'page': page,
                        'url': url,
                        'metadata': {
                            'book': book_title,
                            'category': category,
                            'composer': composer,
                            'key': key,
                            'type': 'song'
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
                    difficulty = exercise.get('difficulty', '') or ''
                    technique = exercise.get('technique', '') or ''
                    
                    path = f"Base de connaissances/{category}/{book_title}/assets/pages/page_{page:03d}.png"
                    encoded_path = path.replace(' ', '%20')
                    url = base_url + encoded_path
                    
                    search_parts = [title, difficulty, technique, book_title, category]
                    search_text = ' '.join(filter(None, search_parts)).lower()
                    
                    resource = {
                        'id': f"{book_title}_{page}_{len(resources)}",
                        'type': 'exercise',
                        'title': title,
                        'page': page,
                        'url': url,
                        'metadata': {
                            'book': book_title,
                            'category': category,
                            'difficulty': difficulty,
                            'technique': technique,
                            'type': 'exercise'
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
                    description = concept.get('description', '') or ''
                    
                    path = f"Base de connaissances/{category}/{book_title}/assets/pages/page_{page:03d}.png"
                    encoded_path = path.replace(' ', '%20')
                    url = base_url + encoded_path
                    
                    search_parts = [concept_name, description[:100], book_title, category, 'theory']
                    search_text = ' '.join(filter(None, search_parts)).lower()
                    
                    resource = {
                        'id': f"{book_title}_{page}_{len(resources)}",
                        'type': 'concept',
                        'title': concept_name,
                        'page': page,
                        'url': url,
                        'metadata': {
                            'book': book_title,
                            'category': category,
                            'description': description[:200],
                            'type': 'concept'
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
            'version': '4.0.2',
            'generated_at': datetime.now().isoformat(),
            'description': 'Prof de Basse - Index complet avec assets/pages/',
            'total_resources': len(resources),
            'base_url': base_url
        },
        'resources': resources
    }
    
    # Sauvegarder
    with open('megasearch.json', 'w', encoding='utf-8') as f:
        json.dump(megasearch_data, f, ensure_ascii=False, indent=2)
    
    print(f"\n✅ MEGASEARCH.JSON FINAL CRÉÉ !")
    print(f"📊 Total ressources: {len(resources)}")
    
    # TEST D'URL FINALE
    if resources:
        print(f"\n🔗 EXEMPLES D'URLs FINALES CORRIGÉES:")
        for i, resource in enumerate(resources[:3], 1):
            title = resource['title'][:50]
            url = resource['url']
            print(f"   [{i}] {title}")
            print(f"       {url}")
            print()
            
        print(f"🧪 TESTE CETTE URL DIRECTEMENT DANS TON NAVIGATEUR:")
        test_url = resources[0]['url']
        print(f"   {test_url}")

if __name__ == '__main__':
    main()
