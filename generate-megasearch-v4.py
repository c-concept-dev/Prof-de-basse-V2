#!/usr/bin/env python3
"""
🎸 Generate MegaSearch.json V4.0 - Prof de Basse
Fusion COMPLÈTE de tous les songs_index_X.json + megasearch existant
Création d'un index unifié avec URLs directes et recherche optimisée
"""

import json
import sys
import re
from datetime import datetime
from pathlib import Path
import urllib.parse
from typing import Dict, List, Set

class MegaSearchGenerator:
    def __init__(self):
        self.BASE_URL = 'https://11drumboy11.github.io/Prof-de-basse-V2/'
        self.resources = []
        self.stats = {
            'total_resources': 0,
            'songs': 0,
            'exercises': 0,
            'concepts': 0,
            'by_category': {},
            'by_style': {},
            'unique_methods': set(),
            'source_files': []
        }
    
    def clean_text(self, text):
        """Nettoie un texte pour la recherche"""
        if not text:
            return ''
        # Enlever caractères de contrôle
        text = ''.join(char for char in str(text) if ord(char) >= 32 or char in '\n\r\t')
        # Normaliser espaces
        text = re.sub(r'\s+', ' ', text).strip()
        return text
    
    def build_url(self, category, book_title, page):
        """Construit une URL complète vers une page"""
        # Nettoyer le titre du livre (enlever _v4.0 suffix)
        clean_title = re.sub(r'_v\d+\.\d+$', '_v4.0', book_title)
        
        # Construire le chemin
        path = f"Base de connaissances/{category}/{clean_title}/assets/page_{page:03d}.png"
        
        # Encoder pour URL
        encoded_path = urllib.parse.quote(path, safe='/:.-_')
        
        return f"{self.BASE_URL}{encoded_path}"
    
    def extract_method_from_title(self, book_title):
        """Extrait le nom de la méthode du titre"""
        # Enlever suffixes de version
        clean_title = re.sub(r'_v\d+\.\d+$', '', book_title)
        return clean_title
    
    def process_songs_index(self, file_path):
        """Traite un fichier songs_index_X.json"""
        print(f"   📄 {file_path.name}")
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            metadata = data.get('metadata', {})
            content = data.get('content', {})
            
            book_title = metadata.get('bookTitle', file_path.stem)
            category = metadata.get('category', 'unknown')
            style = metadata.get('style', 'various')
            
            # Mapper la catégorie aux dossiers
            category_mapping = {
                'method': 'Methodes',
                'songbook': 'Partitions', 
                'theory': 'Theorie',
                'realbook': 'Partitions'
            }
            folder_category = category_mapping.get(category, 'Partitions')
            
            # Ajouter aux stats
            self.stats['source_files'].append(file_path.name)
            self.stats['unique_methods'].add(book_title)
            self.stats['by_category'][category] = self.stats['by_category'].get(category, 0)
            self.stats['by_style'][style] = self.stats['by_style'].get(style, 0)
            
            # Traiter les songs
            songs = content.get('songs', [])
            for song in songs:
                resource = self.create_resource_from_song(song, folder_category, book_title, metadata)
                if resource:
                    self.resources.append(resource)
                    self.stats['songs'] += 1
                    self.stats['by_category'][category] += 1
            
            # Traiter les exercises 
            exercises = content.get('exercises', [])
            for exercise in exercises:
                resource = self.create_resource_from_exercise(exercise, folder_category, book_title, metadata)
                if resource:
                    self.resources.append(resource)
                    self.stats['exercises'] += 1
                    self.stats['by_category'][category] += 1
            
            # Traiter les concepts
            concepts = content.get('concepts', [])
            for concept in concepts:
                resource = self.create_resource_from_concept(concept, folder_category, book_title, metadata)
                if resource:
                    self.resources.append(resource)
                    self.stats['concepts'] += 1
                    self.stats['by_category'][category] += 1
            
            print(f"      ✅ {len(songs)} songs, {len(exercises)} exercises, {len(concepts)} concepts")
            
        except Exception as e:
            print(f"      ❌ Erreur: {e}")
    
    def create_resource_from_song(self, song, category, book_title, metadata):
        """Crée une ressource à partir d'un song"""
        page = song.get('page')
        if not page:
            return None
        
        title = self.clean_text(song.get('title', ''))
        composer = self.clean_text(song.get('composer', ''))
        key = self.clean_text(song.get('key', ''))
        style = self.clean_text(song.get('style', metadata.get('style', '')))
        
        # Construire URL
        url = self.build_url(category, book_title, page)
        
        # Texte de recherche enrichi
        search_parts = [title, composer, key, style, book_title]
        search_text = ' '.join(filter(None, search_parts)).lower()
        
        return {
            'id': f"{book_title}_{page}_{title.replace(' ', '_')}",
            'type': 'song',
            'title': title or f'Page {page}',
            'page': page,
            'url': url,
            'metadata': {
                'book': book_title,
                'category': category,
                'composer': composer,
                'key': key,
                'style': style,
                'type': 'song'
            },
            'searchText': self.clean_text(search_text)
        }
    
    def create_resource_from_exercise(self, exercise, category, book_title, metadata):
        """Crée une ressource à partir d'un exercise"""
        page = exercise.get('page')
        if not page:
            return None
        
        title = self.clean_text(exercise.get('title', ''))
        difficulty = self.clean_text(exercise.get('difficulty', ''))
        technique = self.clean_text(exercise.get('technique', ''))
        
        # Construire URL
        url = self.build_url(category, book_title, page)
        
        # Texte de recherche enrichi
        search_parts = [title, difficulty, technique, book_title]
        search_text = ' '.join(filter(None, search_parts)).lower()
        
        return {
            'id': f"{book_title}_{page}_{title.replace(' ', '_')}",
            'type': 'exercise',
            'title': title or f'Exercise Page {page}',
            'page': page,
            'url': url,
            'metadata': {
                'book': book_title,
                'category': category,
                'difficulty': difficulty,
                'technique': technique,
                'type': 'exercise'
            },
            'searchText': self.clean_text(search_text)
        }
    
    def create_resource_from_concept(self, concept, category, book_title, metadata):
        """Crée une ressource à partir d'un concept"""
        page = concept.get('page')
        if not page:
            return None
        
        concept_name = self.clean_text(concept.get('concept', ''))
        description = self.clean_text(concept.get('description', ''))
        
        # Construire URL
        url = self.build_url(category, book_title, page)
        
        # Texte de recherche enrichi
        search_parts = [concept_name, description, book_title, 'theory', 'concept']
        search_text = ' '.join(filter(None, search_parts)).lower()
        
        return {
            'id': f"{book_title}_{page}_{concept_name.replace(' ', '_')}",
            'type': 'concept',
            'title': concept_name or f'Concept Page {page}',
            'page': page,
            'url': url,
            'metadata': {
                'book': book_title,
                'category': category,
                'description': description,
                'type': 'concept'
            },
            'searchText': self.clean_text(search_text)
        }
    
    def scan_songs_index_files(self):
        """Scanne tous les fichiers songs_index*.json"""
        print("🔍 Scan des fichiers songs_index...")
        
        # Chercher dans le répertoire courant et uploads
        current_dir = Path('.')
        uploads_dir = Path('/mnt/user-data/uploads')
        
        songs_files = []
        
        # Chercher dans le répertoire courant
        songs_files.extend(list(current_dir.glob('songs_index*.json')))
        
        # Chercher dans uploads
        if uploads_dir.exists():
            songs_files.extend(list(uploads_dir.glob('songs_index*.json')))
        
        if not songs_files:
            print("   ⚠️ Aucun fichier songs_index*.json trouvé")
            return
        
        print(f"   📁 Trouvé {len(songs_files)} fichiers songs_index")
        
        for songs_file in sorted(songs_files):
            self.process_songs_index(songs_file)
    
    def deduplicate_resources(self):
        """Supprime les doublons basés sur l'URL"""
        print("🔄 Suppression des doublons...")
        
        seen_urls = set()
        unique_resources = []
        duplicates = 0
        
        for resource in self.resources:
            url = resource.get('url', '')
            if url not in seen_urls:
                seen_urls.add(url)
                unique_resources.append(resource)
            else:
                duplicates += 1
        
        self.resources = unique_resources
        if duplicates > 0:
            print(f"   🗑️ {duplicates} doublons supprimés")
        
        self.stats['total_resources'] = len(self.resources)
    
    def generate_megasearch(self, output_file='megasearch.json'):
        """Génère le fichier megasearch.json final"""
        print("\n🎸 GÉNÉRATION MEGASEARCH.JSON V4.0")
        print("=" * 60)
        
        # Scanner tous les fichiers
        self.scan_songs_index_files()
        
        if not self.resources:
            print("❌ Aucune ressource trouvée !")
            return False
        
        # Supprimer doublons
        self.deduplicate_resources()
        
        # Finaliser les stats
        self.stats['unique_methods'] = len(self.stats['unique_methods'])
        
        # Créer la structure finale
        megasearch_data = {
            'metadata': {
                'version': '4.0.0',
                'generated_at': datetime.now().isoformat(),
                'description': 'Prof de Basse - Index unifié de toutes les ressources',
                'base_url': self.BASE_URL,
                'stats': {
                    'total_resources': self.stats['total_resources'],
                    'songs': self.stats['songs'],
                    'exercises': self.stats['exercises'], 
                    'concepts': self.stats['concepts'],
                    'unique_methods': self.stats['unique_methods'],
                    'source_files_count': len(self.stats['source_files']),
                    'by_category': dict(self.stats['by_category']),
                    'by_style': dict(self.stats['by_style'])
                },
                'source_files': self.stats['source_files']
            },
            'resources': self.resources
        }
        
        # Sauvegarder
        print(f"💾 Sauvegarde dans {output_file}...")
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(megasearch_data, f, ensure_ascii=False, indent=2)
        
        # Statistiques finales
        file_size = Path(output_file).stat().st_size / 1024
        
        print(f"\n✅ MEGASEARCH.JSON V4.0 CRÉÉ !")
        print("=" * 60)
        print(f"📊 STATISTIQUES COMPLÈTES:")
        print(f"   📚 Total ressources   : {self.stats['total_resources']}")
        print(f"   🎵 Songs             : {self.stats['songs']}")
        print(f"   🎸 Exercises         : {self.stats['exercises']}")
        print(f"   📖 Concepts          : {self.stats['concepts']}")
        print(f"   📁 Méthodes uniques  : {self.stats['unique_methods']}")
        print(f"   📄 Fichiers source   : {len(self.stats['source_files'])}")
        
        print(f"\n📈 Par catégorie:")
        for cat, count in sorted(self.stats['by_category'].items()):
            print(f"   {cat}: {count}")
        
        print(f"\n🎶 Par style:")
        for style, count in sorted(self.stats['by_style'].items()):
            if count > 0:
                print(f"   {style}: {count}")
        
        print(f"\n📦 Fichier généré : {output_file}")
        print(f"💾 Taille : {file_size:.1f} KB")
        
        # Exemples d'URLs
        print(f"\n🔗 Exemples d'URLs générées:")
        for i, resource in enumerate(self.resources[:3], 1):
            title = resource['title'][:50]
            url = resource['url']
            print(f"   [{i}] {title}")
            print(f"       {url}")
        
        return True

def main():
    """Point d'entrée principal"""
    generator = MegaSearchGenerator()
    
    try:
        success = generator.generate_megasearch('megasearch.json')
        if success:
            print(f"\n🎯 COMMANDES SUIVANTES:")
            print(f"   git add megasearch.json")
            print(f"   git commit -m '🎸 New: MegaSearch V4.0 - Index unifié complet'")
            print(f"   git push origin main")
            print(f"\n🌐 Teste sur: https://11drumboy11.github.io/Prof-de-basse-V2/")
        else:
            sys.exit(1)
    except Exception as e:
        print(f"\n❌ ERREUR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    main()
