#!/usr/bin/env python3
"""
🎵 MP3 Matching System - Prof de Basse
Système intelligent de liaison automatique MP3 ↔ Exercices

Fonctionnalités :
1. Scan tous les MP3 dans Base de connaissances/MP3/
2. Détecte patterns dans noms de fichiers (Track XX, Pg.XX, Exercise XX)
3. Match automatiquement avec ressources JSON
4. Génère mp3_mapping.json
5. Met à jour megasearch.json avec liens MP3
"""

import os
import re
import json
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from collections import defaultdict

class MP3Matcher:
    def __init__(self, repo_root: Path = Path('.')):
        self.repo_root = repo_root
        self.mp3_base = repo_root / 'Base de connaissances' / 'MP3'
        self.methods_base = repo_root / 'Base de connaissances' / 'Methodes'
        
        self.mp3_files = []
        self.methods = {}
        self.matches = []
        self.stats = {
            'total_mp3': 0,
            'total_resources': 0,
            'matched': 0,
            'unmatched_mp3': 0,
            'unmatched_resources': 0
        }
    
    # ==========================================
    # ÉTAPE 1 : SCANNER LES MP3
    # ==========================================
    
    def scan_mp3_files(self):
        """Scanne tous les MP3 et extrait métadonnées"""
        print("🎵 ÉTAPE 1 : Scan des fichiers MP3...")
        print(f"📂 Dossier : {self.mp3_base}\n")
        
        if not self.mp3_base.exists():
            print(f"❌ Dossier MP3 introuvable : {self.mp3_base}")
            return
        
        for mp3_path in self.mp3_base.rglob('*.mp3'):
            mp3_info = self.extract_mp3_metadata(mp3_path)
            if mp3_info:
                self.mp3_files.append(mp3_info)
        
        self.stats['total_mp3'] = len(self.mp3_files)
        print(f"✅ {len(self.mp3_files)} fichiers MP3 trouvés\n")
    
    def extract_mp3_metadata(self, mp3_path: Path) -> Optional[Dict]:
        """Extrait métadonnées d'un fichier MP3"""
        relative_path = mp3_path.relative_to(self.repo_root)
        filename = mp3_path.stem
        
        # Déterminer la méthode source
        method_folder = None
        if '70 Funk' in str(mp3_path):
            method_folder = '70s Funk & Disco Bass_v4.0'
        elif 'Paul westwood' in str(mp3_path):
            if 'Vol 1' in str(mp3_path) or 'Vol%201' in str(mp3_path):
                method_folder = 'Paul westwood 1-2_v4.0'
            else:
                method_folder = 'Paul westwood 2-5_v4.0'
        elif 'Jon Liebman' in str(mp3_path):
            method_folder = 'Jon Liebman - Funk Fusion Bass_v4.0'
        
        # Pattern matching pour extraire numéros
        patterns = self.detect_patterns(filename)
        
        return {
            'path': str(relative_path),
            'filename': filename,
            'method_folder': method_folder,
            'url': self.build_github_url(relative_path),
            'patterns': patterns
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
        
        # Pattern 4 : Numéro au début (ex: "1-01", "2-05")
        disc_track_match = re.search(r'^(\d+)-(\d+)', filename)
        if disc_track_match:
            patterns['disc'] = int(disc_track_match.group(1))
            patterns['disc_track'] = int(disc_track_match.group(2))
        
        return patterns
    
    def build_github_url(self, relative_path: Path) -> str:
        """Construit URL GitHub Pages pour MP3"""
        base_url = "https://11drumboy11.github.io/Prof-de-basse-V2/"
        # Encoder les espaces et caractères spéciaux
        path_str = str(relative_path).replace(' ', '%20').replace('&', '%26')
        return base_url + path_str
    
    # ==========================================
    # ÉTAPE 2 : CHARGER LES RESSOURCES
    # ==========================================
    
    def load_method_resources(self):
        """Charge toutes les ressources des méthodes"""
        print("📚 ÉTAPE 2 : Chargement des ressources JSON...\n")
        
        if not self.methods_base.exists():
            print(f"❌ Dossier Methodes introuvable : {self.methods_base}")
            return
        
        for method_dir in self.methods_base.iterdir():
            if not method_dir.is_dir() or method_dir.name.startswith('.'):
                continue
            
            # Chercher fichier JSON
            json_files = list(method_dir.glob('*.json'))
            json_files = [f for f in json_files if 'metadata' not in f.name.lower()]
            
            if not json_files:
                continue
            
            json_file = json_files[0]
            print(f"  📁 {method_dir.name}/{json_file.name}")
            
            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                resources = []
                if isinstance(data, dict) and 'resources' in data:
                    resources = data['resources']
                elif isinstance(data, list):
                    resources = data
                
                self.methods[method_dir.name] = {
                    'json_file': str(json_file),
                    'resources': resources,
                    'total': len(resources)
                }
                
                self.stats['total_resources'] += len(resources)
                
            except Exception as e:
                print(f"    ❌ Erreur : {e}")
        
        print(f"\n✅ {self.stats['total_resources']} ressources chargées")
        print(f"✅ {len(self.methods)} méthodes trouvées\n")
    
    # ==========================================
    # ÉTAPE 3 : MATCHING INTELLIGENT
    # ==========================================
    
    def match_mp3_to_resources(self):
        """Match automatique MP3 ↔ Ressources"""
        print("🔗 ÉTAPE 3 : Matching MP3 ↔ Ressources...\n")
        
        for mp3 in self.mp3_files:
            # Trouver méthode correspondante
            method_name = mp3['method_folder']
            if not method_name or method_name not in self.methods:
                self.stats['unmatched_mp3'] += 1
                continue
            
            method_data = self.methods[method_name]
            resources = method_data['resources']
            
            # Chercher match
            matched_resource = self.find_matching_resource(mp3, resources)
            
            if matched_resource:
                match_info = {
                    'mp3': mp3,
                    'resource': matched_resource,
                    'method': method_name,
                    'confidence': self.calculate_confidence(mp3, matched_resource)
                }
                self.matches.append(match_info)
                self.stats['matched'] += 1
                
                print(f"  ✅ {mp3['filename']}")
                print(f"     → {matched_resource.get('title', 'Sans titre')}")
                print(f"     Confiance : {match_info['confidence']:.0%}\n")
            else:
                self.stats['unmatched_mp3'] += 1
        
        # Ressources non matchées
        matched_ids = {m['resource']['id'] for m in self.matches}
        for method_data in self.methods.values():
            for resource in method_data['resources']:
                if resource['id'] not in matched_ids:
                    self.stats['unmatched_resources'] += 1
        
        print(f"✅ Matching terminé : {self.stats['matched']} correspondances\n")
    
    def find_matching_resource(self, mp3: Dict, resources: List[Dict]) -> Optional[Dict]:
        """Trouve la ressource correspondant au MP3"""
        best_match = None
        best_score = 0
        
        for resource in resources:
            score = self.calculate_match_score(mp3, resource)
            if score > best_score:
                best_score = score
                best_match = resource
        
        # Seuil de confiance minimum
        return best_match if best_score >= 50 else None
    
    def calculate_match_score(self, mp3: Dict, resource: Dict) -> int:
        """Calcule score de matching (0-100)"""
        score = 0
        patterns = mp3['patterns']
        
        # Match par numéro de track
        if 'track' in patterns:
            track_num = patterns['track']
            # Vérifier dans le titre ou ID
            if str(track_num) in str(resource.get('id', '')):
                score += 40
            if str(track_num) in str(resource.get('title', '')):
                score += 20
        
        # Match par numéro de page
        if 'page' in patterns:
            page_num = patterns['page']
            resource_page = resource.get('page')
            if resource_page == page_num:
                score += 50
            elif resource_page and abs(resource_page - page_num) <= 2:
                score += 30  # Pages proches
        
        # Match par numéro d'exercice
        if 'exercise' in patterns:
            exercise_num = patterns['exercise']
            if str(exercise_num) in str(resource.get('title', '')):
                score += 40
        
        return score
    
    def calculate_confidence(self, mp3: Dict, resource: Dict) -> float:
        """Calcule confiance du match (0-1)"""
        score = self.calculate_match_score(mp3, resource)
        return min(score / 100.0, 1.0)
    
    # ==========================================
    # ÉTAPE 4 : GÉNÉRATION FICHIERS
    # ==========================================
    
    def generate_mp3_mapping(self):
        """Génère mp3_mapping.json"""
        print("💾 ÉTAPE 4 : Génération mp3_mapping.json...\n")
        
        mapping = {
            'metadata': {
                'version': '1.0.0',
                'generated_at': self.get_timestamp(),
                'total_mp3': self.stats['total_mp3'],
                'total_resources': self.stats['total_resources'],
                'matched': self.stats['matched'],
                'match_rate': f"{(self.stats['matched'] / self.stats['total_mp3'] * 100):.1f}%"
            },
            'stats': self.stats,
            'mappings': []
        }
        
        # Ajouter les mappings
        for match in self.matches:
            mapping['mappings'].append({
                'resource_id': match['resource']['id'],
                'resource_title': match['resource'].get('title', ''),
                'resource_page': match['resource'].get('page'),
                'mp3_filename': match['mp3']['filename'],
                'mp3_url': match['mp3']['url'],
                'method': match['method'],
                'confidence': match['confidence']
            })
        
        # Sauvegarder
        output_file = self.repo_root / 'mp3_mapping.json'
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(mapping, f, indent=2, ensure_ascii=False)
        
        print(f"✅ mp3_mapping.json généré ({len(mapping['mappings'])} mappings)")
        return mapping
    
    def update_megasearch_with_mp3(self):
        """Met à jour megasearch.json avec liens MP3"""
        print("\n🔄 ÉTAPE 5 : Mise à jour megasearch.json...\n")
        
        megasearch_file = self.repo_root / 'megasearch.json'
        if not megasearch_file.exists():
            print("❌ megasearch.json introuvable")
            return
        
        # Charger megasearch.json
        with open(megasearch_file, 'r', encoding='utf-8') as f:
            megasearch = json.load(f)
        
        # Créer index des mappings
        mp3_by_resource_id = {}
        for match in self.matches:
            resource_id = match['resource']['id']
            mp3_by_resource_id[resource_id] = {
                'mp3_url': match['mp3']['url'],
                'mp3_filename': match['mp3']['filename'],
                'confidence': match['confidence']
            }
        
        # Mettre à jour les ressources
        updated_count = 0
        for resource in megasearch.get('resources', []):
            resource_id = resource.get('id')
            if resource_id in mp3_by_resource_id:
                mp3_info = mp3_by_resource_id[resource_id]
                
                # Ajouter métadonnées MP3
                if 'metadata' not in resource:
                    resource['metadata'] = {}
                
                resource['metadata']['has_mp3'] = True
                resource['metadata']['mp3_url'] = mp3_info['mp3_url']
                resource['metadata']['mp3_filename'] = mp3_info['mp3_filename']
                resource['metadata']['mp3_match_confidence'] = mp3_info['confidence']
                
                updated_count += 1
        
        # Mettre à jour métadonnées globales
        if 'metadata' in megasearch:
            megasearch['metadata']['has_mp3_integration'] = True
            megasearch['metadata']['mp3_resources_count'] = updated_count
        
        # Sauvegarder
        with open(megasearch_file, 'w', encoding='utf-8') as f:
            json.dump(megasearch, f, indent=2, ensure_ascii=False)
        
        print(f"✅ megasearch.json mis à jour ({updated_count} ressources avec MP3)")
    
    # ==========================================
    # UTILITAIRES
    # ==========================================
    
    def get_timestamp(self):
        """Retourne timestamp ISO"""
        from datetime import datetime
        return datetime.now().isoformat()
    
    def print_summary(self):
        """Affiche résumé détaillé"""
        print("\n" + "="*60)
        print("🎵 RÉSUMÉ FINAL - MP3 MATCHING SYSTEM")
        print("="*60)
        print(f"📊 Fichiers MP3 trouvés     : {self.stats['total_mp3']}")
        print(f"📚 Ressources JSON          : {self.stats['total_resources']}")
        print(f"✅ Correspondances réussies : {self.stats['matched']}")
        print(f"❌ MP3 non matchés          : {self.stats['unmatched_mp3']}")
        print(f"❌ Ressources sans MP3      : {self.stats['unmatched_resources']}")
        
        if self.stats['total_mp3'] > 0:
            match_rate = (self.stats['matched'] / self.stats['total_mp3']) * 100
            print(f"\n🎯 Taux de réussite : {match_rate:.1f}%")
        
        print("="*60)
        
        # Top 10 des matches
        if self.matches:
            print("\n🏆 TOP 10 DES MEILLEURES CORRESPONDANCES:\n")
            sorted_matches = sorted(self.matches, key=lambda x: x['confidence'], reverse=True)
            for i, match in enumerate(sorted_matches[:10], 1):
                print(f"{i}. {match['mp3']['filename']}")
                print(f"   → {match['resource'].get('title', 'Sans titre')}")
                print(f"   Confiance : {match['confidence']:.0%}\n")
    
    def run_complete_workflow(self):
        """Exécute le workflow complet"""
        print("🚀 DÉMARRAGE DU SYSTÈME DE MATCHING MP3\n")
        print("="*60 + "\n")
        
        # Étape 1 : Scanner MP3
        self.scan_mp3_files()
        
        # Étape 2 : Charger ressources
        self.load_method_resources()
        
        # Étape 3 : Matching
        self.match_mp3_to_resources()
        
        # Étape 4 : Générer mapping
        self.generate_mp3_mapping()
        
        # Étape 5 : Mettre à jour megasearch
        self.update_megasearch_with_mp3()
        
        # Résumé
        self.print_summary()


if __name__ == '__main__':
    import sys
    
    # Déterminer le chemin du repo
    repo_root = Path.cwd()
    if len(sys.argv) > 1:
        repo_root = Path(sys.argv[1])
    
    print(f"📂 Repository : {repo_root}\n")
    
    # Lancer le matching
    matcher = MP3Matcher(repo_root)
    matcher.run_complete_workflow()
    
    print("\n✅ TERMINÉ !")
    print("\n📁 Fichiers générés :")
    print("  - mp3_mapping.json (mappings détaillés)")
    print("  - megasearch.json (mis à jour avec MP3)")
