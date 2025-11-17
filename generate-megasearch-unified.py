#!/usr/bin/env python3
"""
🎸 Prof de Basse - Génération Megasearch Unifié
Fusionne TOUS les JSON en un seul megasearch.json optimisé
"""

import json
import sys
from pathlib import Path
from datetime import datetime
from typing import List, Dict

class MegasearchGenerator:
    def __init__(self):
        self.all_resources = []
        self.stats = {
            'total_resources': 0,
            'total_methods': 0,
            'total_mp3': 0,
            'by_category': {},
            'by_level': {},
            'by_style': {}
        }
    
    def process_v4_json(self, json_file: Path):
        """Traite un JSON format v4.0"""
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            metadata = data.get('metadata', {})
            resources = data.get('resources', [])
            
            book_name = metadata.get('book_name', json_file.stem)
            category = metadata.get('category', 'Unknown')
            
            print(f"  📚 {book_name}: {len(resources)} ressources")
            
            # Ajouter ressources
            for resource in resources:
                # Enrichir avec métadonnées du livre
                if 'metadata' not in resource:
                    resource['metadata'] = {}
                
                resource['metadata']['book'] = book_name
                resource['metadata']['category'] = category
                
                # Construire searchText
                searchText = f"{resource.get('title', '')} {book_name} {category}"
                if 'metadata' in resource:
                    searchText += f" {resource['metadata'].get('style', '')} {resource['metadata'].get('level', '')}"
                
                resource['searchText'] = searchText.lower()
                
                self.all_resources.append(resource)
                
                # Stats
                self.stats['total_resources'] += 1
                
                if resource.get('metadata', {}).get('has_mp3'):
                    self.stats['total_mp3'] += 1
                
                # Par catégorie
                self.stats['by_category'][category] = self.stats['by_category'].get(category, 0) + 1
            
            self.stats['total_methods'] += 1
            
        except Exception as e:
            print(f"  ❌ Erreur: {e}")
    
    def process_songs_json(self, json_file: Path):
        """Traite un JSON format songs_index.json"""
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            songs = data.get('songs', [])
            book_name = json_file.parent.name
            
            print(f"  📚 {book_name}: {len(songs)} morceaux")
            
            # Convertir au format unifié
            for song in songs:
                resource = {
                    'id': song.get('id'),
                    'type': 'song',
                    'title': song.get('title'),
                    'page': song.get('page'),
                    'url': song.get('url'),
                    'metadata': {
                        'book': book_name,
                        'category': 'Partitions',
                        'has_mp3': False
                    },
                    'searchText': f"{song.get('title', '')} {book_name}".lower()
                }
                
                self.all_resources.append(resource)
                self.stats['total_resources'] += 1
            
            self.stats['total_methods'] += 1
            
        except Exception as e:
            print(f"  ❌ Erreur: {e}")
    
    def generate(self, base_path: Path = Path('.'), output_file: str = 'megasearch.json'):
        """Génère le megasearch.json unifié"""
        print("="*60)
        print("🔄 GÉNÉRATION MEGASEARCH UNIFIÉ")
        print("="*60)
        print()
        
        # Trouver tous les JSON
        json_files_v4 = list(base_path.glob('Base de connaissances/**/*_v4.0/*.json'))
        json_files_songs = list(base_path.glob('Base de connaissances/**/songs_index.json'))
        
        # Aussi chercher Pratique.json
        json_files_pratique = list(base_path.glob('Base de connaissances/**/Pratique.json'))
        
        json_files_v4 = [f for f in json_files_v4 if '.git' not in str(f)]
        json_files_songs = [f for f in json_files_songs if '.git' not in str(f)]
        json_files_pratique = [f for f in json_files_pratique if '.git' not in str(f)]
        
        print(f"📊 Fichiers trouvés:")
        print(f"  - Format v4.0: {len(json_files_v4)}")
        print(f"  - Format Pratique: {len(json_files_pratique)}")
        print(f"  - Format songs: {len(json_files_songs)}")
        print()
        
        # Traiter v4.0
        if json_files_v4:
            print("🔄 Traitement v4.0...")
            for json_file in sorted(json_files_v4):
                self.process_v4_json(json_file)
        
        # Traiter Pratique.json
        if json_files_pratique:
            print("\n🔄 Traitement Pratique.json...")
            for json_file in sorted(json_files_pratique):
                self.process_v4_json(json_file)
        
        # Traiter songs
        if json_files_songs:
            print("\n🔄 Traitement songs...")
            for json_file in sorted(json_files_songs):
                self.process_songs_json(json_file)
        
        # Créer megasearch
        megasearch = {
            'metadata': {
                'version': '4.0',
                'generated_at': datetime.now().isoformat(),
                'total_resources': self.stats['total_resources'],
                'total_methods': self.stats['total_methods'],
                'total_mp3': self.stats['total_mp3'],
                'stats': self.stats
            },
            'resources': self.all_resources
        }
        
        # Sauvegarder
        output_path = Path(output_file)
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(megasearch, f, ensure_ascii=False, indent=2)
        
        # Résumé
        print()
        print("="*60)
        print("✅ GÉNÉRATION TERMINÉE")
        print("="*60)
        print(f"📁 Fichier: {output_path}")
        print(f"📊 Ressources: {self.stats['total_resources']}")
        print(f"📚 Méthodes: {self.stats['total_methods']}")
        print(f"🎵 MP3: {self.stats['total_mp3']}")
        print(f"💾 Taille: {output_path.stat().st_size / 1024:.1f} KB")
        print("="*60)
        print()
        
        return True

def main():
    generator = MegasearchGenerator()
    success = generator.generate()
    sys.exit(0 if success else 1)

if __name__ == '__main__':
    main()
