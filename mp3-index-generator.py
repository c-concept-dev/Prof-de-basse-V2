#!/usr/bin/env python3
"""
🎵 MP3 Index Generator - Prof de Basse
Crée un index structuré de tous les MP3 disponibles

Génère :
- mp3_index.json : Index complet de tous les MP3
- Un fichier par méthode pour faciliter le matching
"""

import os
import re
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional

class MP3IndexGenerator:
    def __init__(self, repo_root: Path = Path('.')):
        self.repo_root = repo_root
        self.mp3_base = repo_root / 'Base de connaissances' / 'MP3'
        
        self.mp3_index = {
            'metadata': {
                'version': '1.0.0',
                'generated_at': datetime.now().isoformat(),
                'total_mp3': 0
            },
            'methods': {}
        }
    
    def detect_patterns(self, filename: str) -> Dict:
        """Détecte patterns dans nom de fichier MP3"""
        patterns = {}
        
        # Pattern 1 : Track XX (ex: "Track 02", "Track 125")
        track_match = re.search(r'[Tt]rack\s*(\d+)', filename)
        if track_match:
            patterns['track'] = int(track_match.group(1))
        
        # Pattern 2 : Page XX (ex: "Pg.67", "Page 67")
        page_match = re.search(r'(?:Pg\.?|Page)\s*(\d+)', filename, re.IGNORECASE)
        if page_match:
            patterns['page'] = int(page_match.group(1))
        
        # Pattern 3 : Exercise XXX (ex: "123 Pg.67")
        exercise_match = re.search(r'(\d{2,3})\s+(?:Pg|Page)', filename)
        if exercise_match:
            patterns['exercise'] = int(exercise_match.group(1))
        
        # Pattern 4 : Disc-Track (ex: "1-01", "2-05")
        disc_track_match = re.search(r'^(\d+)-(\d+)', filename)
        if disc_track_match:
            patterns['disc'] = int(disc_track_match.group(1))
            patterns['disc_track'] = int(disc_track_match.group(2))
        
        # Pattern 5 : Style/Genre dans le nom
        style_patterns = {
            'funk': r'funk',
            'blues': r'blues',
            'jazz': r'jazz',
            'latin': r'latin',
            'rock': r'rock',
            'slap': r'slap',
            'walking': r'walking'
        }
        
        for style, pattern in style_patterns.items():
            if re.search(pattern, filename, re.IGNORECASE):
                patterns['style'] = style
                break
        
        return patterns
    
    def build_github_url(self, relative_path: Path) -> str:
        """Construit URL GitHub Pages pour MP3"""
        base_url = "https://11drumboy11.github.io/Prof-de-basse-V2/"
        # Encoder les espaces et caractères spéciaux
        path_str = str(relative_path).replace(' ', '%20').replace('&', '%26')
        return base_url + path_str
    
    def scan_method_folder(self, method_path: Path) -> Dict:
        """Scanne un dossier de méthode"""
        method_name = method_path.name
        
        print(f"  📁 {method_name}")
        
        mp3_files = []
        for mp3_path in method_path.rglob('*.mp3'):
            relative_path = mp3_path.relative_to(self.repo_root)
            filename = mp3_path.stem
            
            patterns = self.detect_patterns(filename)
            
            mp3_info = {
                'id': f"mp3_{len(mp3_files) + 1:03d}",
                'filename': mp3_path.name,
                'stem': filename,
                'path': str(relative_path),
                'url': self.build_github_url(relative_path),
                'size_bytes': mp3_path.stat().st_size,
                'patterns': patterns
            }
            
            mp3_files.append(mp3_info)
        
        print(f"     ✅ {len(mp3_files)} fichiers MP3")
        
        return {
            'method_name': method_name,
            'total_mp3': len(mp3_files),
            'mp3_files': mp3_files
        }
    
    def generate_index(self):
        """Génère l'index complet"""
        print("🎵 GÉNÉRATION INDEX MP3\n")
        print(f"📂 Dossier source : {self.mp3_base}\n")
        
        if not self.mp3_base.exists():
            print(f"❌ Dossier MP3 introuvable : {self.mp3_base}")
            return
        
        total_mp3 = 0
        
        # Scanner chaque sous-dossier
        for method_folder in sorted(self.mp3_base.iterdir()):
            if not method_folder.is_dir() or method_folder.name.startswith('.'):
                continue
            
            method_data = self.scan_method_folder(method_folder)
            
            if method_data['total_mp3'] > 0:
                self.mp3_index['methods'][method_folder.name] = method_data
                total_mp3 += method_data['total_mp3']
        
        self.mp3_index['metadata']['total_mp3'] = total_mp3
        
        print(f"\n✅ Total : {total_mp3} fichiers MP3 indexés")
        print(f"✅ {len(self.mp3_index['methods'])} méthodes trouvées\n")
    
    def save_index(self):
        """Sauvegarde l'index"""
        output_file = self.repo_root / 'mp3_index.json'
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(self.mp3_index, f, indent=2, ensure_ascii=False)
        
        print(f"💾 Index sauvegardé : {output_file}")
        
        # Créer aussi un fichier par méthode
        mp3_dir = self.repo_root / 'Base de connaissances' / 'MP3'
        
        for method_name, method_data in self.mp3_index['methods'].items():
            method_index_file = mp3_dir / method_name / 'mp3_index.json'
            
            method_index = {
                'metadata': {
                    'method_name': method_name,
                    'total_mp3': method_data['total_mp3'],
                    'generated_at': self.mp3_index['metadata']['generated_at']
                },
                'mp3_files': method_data['mp3_files']
            }
            
            with open(method_index_file, 'w', encoding='utf-8') as f:
                json.dump(method_index, f, indent=2, ensure_ascii=False)
            
            print(f"   📄 {method_name}/mp3_index.json")
    
    def print_summary(self):
        """Affiche un résumé"""
        print("\n" + "="*60)
        print("🎵 RÉSUMÉ - INDEX MP3")
        print("="*60)
        
        for method_name, method_data in self.mp3_index['methods'].items():
            print(f"\n📁 {method_name}")
            print(f"   Fichiers MP3 : {method_data['total_mp3']}")
            
            # Stats patterns
            patterns_stats = {
                'track': 0,
                'page': 0,
                'exercise': 0,
                'disc': 0
            }
            
            for mp3 in method_data['mp3_files']:
                for pattern in patterns_stats.keys():
                    if pattern in mp3['patterns']:
                        patterns_stats[pattern] += 1
            
            print(f"   Patterns détectés :")
            for pattern, count in patterns_stats.items():
                if count > 0:
                    print(f"     - {pattern}: {count}")
        
        print("\n" + "="*60)
        print(f"📊 TOTAL : {self.mp3_index['metadata']['total_mp3']} fichiers MP3")
        print("="*60)
    
    def run(self):
        """Exécute le workflow complet"""
        self.generate_index()
        self.save_index()
        self.print_summary()


if __name__ == '__main__':
    import sys
    
    # Déterminer le chemin du repo
    repo_root = Path.cwd()
    if len(sys.argv) > 1:
        repo_root = Path(sys.argv[1])
    
    print(f"📂 Repository : {repo_root}\n")
    
    # Générer l'index
    generator = MP3IndexGenerator(repo_root)
    generator.run()
    
    print("\n✅ TERMINÉ !")
    print("\n📁 Fichiers générés :")
    print("  - mp3_index.json (index global)")
    print("  - [Méthode]/mp3_index.json (un par méthode)")
