#!/usr/bin/env python3
"""
🎸 Prof de Basse - Génération Megasearch Unifié v2
Fusionne TOUS les JSON en un seul megasearch.json optimisé
ADAPTÉ pour format content.songs et content.exercises
"""

import json
import sys
from pathlib import Path
from datetime import datetime

class MegasearchGenerator:
    def __init__(self):
        self.all_resources = []
        self.stats = {
            'total_resources': 0,
            'total_methods': 0,
            'total_mp3': 0,
            'by_category': {},
            'by_type': {}
        }
    
    def process_json_file(self, json_file: Path):
        """Traite un fichier JSON (format unifié)"""
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            metadata = data.get('metadata', {})
            content = data.get('content', {})
            
            book_name = metadata.get('bookTitle', json_file.parent.name)
            category = metadata.get('category', 'unknown')
            style = metadata.get('style', 'unknown')
            
            # Traiter songs
            songs = content.get('songs', [])
            # Traiter exercises
            exercises = content.get('exercises', [])
            
            total_items = len(songs) + len(exercises)
            
            if total_items > 0:
                print(f"  📚 {book_name}: {len(songs)} songs + {len(exercises)} exercises")
            
            # Convertir songs
            for i, song in enumerate(songs):
                resource = {
                    'id': f"{book_name.replace(' ', '_').lower()}_song_{i+1}",
                    'type': 'song',
                    'title': song.get('title', f'Song {i+1}'),
                    'page': song.get('page', i+1),
                    'url': self.build_url(json_file.parent, song.get('page', i+1)),
                    'metadata': {
                        'book': book_name,
                        'category': category,
                        'style': style,
                        'key': song.get('key', ''),
                        'has_mp3': False
                    },
                    'searchText': f"{song.get('title', '')} {book_name} {style}".lower()
                }
                
                self.all_resources.append(resource)
                self.stats['total_resources'] += 1
                self.stats['by_type']['song'] = self.stats['by_type'].get('song', 0) + 1
            
            # Convertir exercises
            for i, exercise in enumerate(exercises):
                resource = {
                    'id': f"{book_name.replace(' ', '_').lower()}_ex_{i+1}",
                    'type': 'exercise',
                    'title': exercise.get('title', f'Exercise {i+1}'),
                    'page': exercise.get('page', i+1),
                    'url': self.build_url(json_file.parent, exercise.get('page', i+1)),
                    'metadata': {
                        'book': book_name,
                        'category': category,
                        'style': style,
                        'difficulty': exercise.get('difficulty', 'unknown'),
                        'technique': exercise.get('technique', ''),
                        'has_mp3': False
                    },
                    'searchText': f"{exercise.get('title', '')} {book_name} {style} {exercise.get('technique', '')}".lower()
                }
                
                self.all_resources.append(resource)
                self.stats['total_resources'] += 1
                self.stats['by_type']['exercise'] = self.stats['by_type'].get('exercise', 0) + 1
            
            if total_items > 0:
                self.stats['total_methods'] += 1
                self.stats['by_category'][category] = self.stats['by_category'].get(category, 0) + total_items
            
        except Exception as e:
            print(f"  ❌ Erreur {json_file.name}: {e}")
    
    def build_url(self, parent_dir: Path, page: int) -> str:
        """Construit l'URL GitHub Pages pour une page"""
        # Format: https://11drumboy11.github.io/Prof-de-basse-V2/Base%20de%20connaissances/.../assets/pages/page_XXX.png
        
        # Trouver le chemin relatif depuis "Base de connaissances"
        parts = parent_dir.parts
        try:
            base_idx = parts.index('Base de connaissances')
            rel_path = '/'.join(parts[base_idx:])
            
            # Encoder espaces
            rel_path_encoded = rel_path.replace(' ', '%20')
            
            # Construire URL
            page_str = f"{page:03d}"  # page_001, page_002, etc.
            url = f"https://11drumboy11.github.io/Prof-de-basse-V2/{rel_path_encoded}/assets/pages/page_{page_str}.png"
            
            return url
        except ValueError:
            return ""
    
    def generate(self, base_path: Path = Path('.'), output_file: str = 'megasearch.json'):
        """Génère le megasearch.json unifié"""
        print("="*60)
        print("🔄 GÉNÉRATION MEGASEARCH UNIFIÉ v2")
        print("="*60)
        print()
        
        # Trouver tous les songs_index.json
        json_files = list(base_path.glob('Base de connaissances/**/songs_index.json'))
        json_files = [f for f in json_files if '.git' not in str(f)]
        
        print(f"📊 {len(json_files)} fichiers JSON trouvés\n")
        
        if not json_files:
            print("⚠️  Aucun fichier trouvé")
            return False
        
        print("🔄 Traitement des fichiers...\n")
        
        # Traiter chaque fichier
        for json_file in sorted(json_files):
            self.process_json_file(json_file)
        
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
        print(f"🎵 Songs: {self.stats['by_type'].get('song', 0)}")
        print(f"💪 Exercises: {self.stats['by_type'].get('exercise', 0)}")
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
