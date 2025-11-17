#!/usr/bin/env python3
"""
🎵 MP3 Matching System v2 - Prof de Basse
Système intelligent de liaison automatique MP3 ↔ Exercices

CORRIGÉ pour :
- Format songs_index.json avec content.exercises
- Structure mp3_index.json générée
"""

import json
from pathlib import Path
from typing import Dict, List, Optional

class MP3MatcherV2:
    def __init__(self, repo_root: Path = Path('.')):
        self.repo_root = repo_root
        self.mp3_base = repo_root / 'Base de connaissances' / 'MP3'
        self.methods_base = repo_root / 'Base de connaissances' / 'Methodes'
        
        self.mp3_index = {}
        self.exercises = {}
        self.matches = []
        self.stats = {
            'total_mp3': 0,
            'total_exercises': 0,
            'matched': 0,
            'unmatched_mp3': 0,
            'unmatched_exercises': 0
        }
    
    # ==========================================
    # ÉTAPE 1 : CHARGER MP3 INDEX
    # ==========================================
    
    def load_mp3_index(self):
        """Charge l'index MP3 global"""
        print("🎵 ÉTAPE 1 : Chargement de l'index MP3...\n")
        
        mp3_index_file = self.repo_root / 'mp3_index.json'
        
        if not mp3_index_file.exists():
            print(f"❌ mp3_index.json introuvable")
            print(f"   Lance d'abord : python3 mp3-index-generator.py\n")
            return False
        
        with open(mp3_index_file, 'r', encoding='utf-8') as f:
            self.mp3_index = json.load(f)
        
        self.stats['total_mp3'] = self.mp3_index['metadata']['total_mp3']
        
        print(f"✅ {self.stats['total_mp3']} fichiers MP3 chargés")
        print(f"✅ {len(self.mp3_index['methods'])} méthodes\n")
        
        return True
    
    # ==========================================
    # ÉTAPE 2 : CHARGER EXERCICES
    # ==========================================
    
    def load_exercises(self):
        """Charge tous les exercices des méthodes"""
        print("📚 ÉTAPE 2 : Chargement des exercices...\n")
        
        if not self.methods_base.exists():
            print(f"❌ Dossier Methodes introuvable : {self.methods_base}")
            return
        
        for method_dir in self.methods_base.iterdir():
            if not method_dir.is_dir() or method_dir.name.startswith('.'):
                continue
            
            # Chercher songs_index.json
            songs_file = method_dir / 'songs_index.json'
            
            if not songs_file.exists():
                continue
            
            print(f"  📁 {method_dir.name}")
            
            try:
                with open(songs_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                # Format corrigé : content.exercises
                exercises = []
                if 'content' in data and 'exercises' in data['content']:
                    exercises = data['content']['exercises']
                
                # Ajouter un ID unique à chaque exercice
                for i, exercise in enumerate(exercises, 1):
                    exercise['id'] = f"{method_dir.name}_{i:03d}"
                    exercise['method'] = method_dir.name
                
                self.exercises[method_dir.name] = {
                    'method_name': method_dir.name,
                    'total': len(exercises),
                    'exercises': exercises
                }
                
                self.stats['total_exercises'] += len(exercises)
                print(f"     ✅ {len(exercises)} exercices\n")
                
            except Exception as e:
                print(f"    ❌ Erreur : {e}\n")
        
        print(f"✅ {self.stats['total_exercises']} exercices chargés")
        print(f"✅ {len(self.exercises)} méthodes\n")
    
    # ==========================================
    # ÉTAPE 3 : MATCHING
    # ==========================================
    
    def create_automatic_mapping(self) -> Dict[str, str]:
        """Crée mapping automatique MP3 folders → Method names"""
        mapping = {}
        
        # Fonction de normalisation
        def normalize(name: str) -> str:
            """Normalise un nom pour comparaison"""
            import re
            # Enlever version, MP3, v4.0, etc.
            name = re.sub(r'_v\d+\.\d+', '', name)
            name = re.sub(r'\s+MP3', '', name, flags=re.IGNORECASE)
            name = re.sub(r'[_-]', ' ', name)
            name = name.lower().strip()
            return name
        
        # Pour chaque dossier MP3
        for mp3_folder in self.mp3_index['methods'].keys():
            mp3_normalized = normalize(mp3_folder)
            
            best_match = None
            best_score = 0
            
            # Chercher meilleure correspondance
            for method_name in self.exercises.keys():
                method_normalized = normalize(method_name)
                
                # Calcul similarité simple
                score = 0
                mp3_words = set(mp3_normalized.split())
                method_words = set(method_normalized.split())
                
                # Mots en commun
                common = mp3_words & method_words
                score = len(common) * 20
                
                # Bonus si contient "funk", "paul", "liebman", etc.
                key_words = ['funk', 'disco', 'paul', 'westwood', 'liebman', 'jon', 'john']
                for word in key_words:
                    if word in mp3_normalized and word in method_normalized:
                        score += 15
                
                # Correspondance exacte partielle
                if '70' in mp3_normalized and '70' in method_normalized:
                    score += 30
                if 'funk' in mp3_normalized and 'funk' in method_normalized:
                    score += 20
                if 'westwood' in mp3_normalized and 'westwood' in method_normalized:
                    score += 30
                if ('liebman' in mp3_normalized or 'jon' in mp3_normalized or 'john' in mp3_normalized) and \
                   ('liebman' in method_normalized or 'jon' in method_normalized):
                    score += 30
                
                if score > best_score:
                    best_score = score
                    best_match = method_name
            
            # Accepter si score > 40
            if best_score >= 40 and best_match:
                mapping[mp3_folder] = best_match
        
        return mapping
    
    def match_by_method(self):
        """Match MP3 ↔ Exercices par méthode"""
        print("🔗 ÉTAPE 3 : Matching MP3 ↔ Exercices...\n")
        
        # Créer mapping automatique intelligent
        method_mapping = self.create_automatic_mapping()
        
        print("📋 Mappings détectés :")
        for mp3_folder, method_name in method_mapping.items():
            print(f"   {mp3_folder} → {method_name}")
        print()
        
        for mp3_folder, method_name in method_mapping.items():
            if mp3_folder not in self.mp3_index['methods']:
                continue
            
            if method_name not in self.exercises:
                continue
            
            mp3_data = self.mp3_index['methods'][mp3_folder]
            exercise_data = self.exercises[method_name]
            
            print(f"📁 {method_name}")
            print(f"   MP3 : {mp3_data['total_mp3']} | Exercices : {exercise_data['total']}")
            
            # Matcher
            matched_count = self.match_method_resources(
                mp3_data['mp3_files'],
                exercise_data['exercises'],
                method_name
            )
            
            print(f"   ✅ {matched_count} correspondances\n")
    
    def match_method_resources(self, mp3_files: List[Dict], exercises: List[Dict], method_name: str) -> int:
        """Match les ressources d'une méthode"""
        matched = 0
        
        for mp3 in mp3_files:
            best_match = None
            best_score = 0
            
            for exercise in exercises:
                score = self.calculate_match_score(mp3, exercise)
                if score > best_score:
                    best_score = score
                    best_match = exercise
            
            # Seuil minimum
            if best_score >= 40:
                match_info = {
                    'mp3': mp3,
                    'exercise': best_match,
                    'method': method_name,
                    'confidence': best_score / 100.0
                }
                self.matches.append(match_info)
                matched += 1
                self.stats['matched'] += 1
            else:
                self.stats['unmatched_mp3'] += 1
        
        return matched
    
    def calculate_match_score(self, mp3: Dict, exercise: Dict) -> int:
        """Calcule score de matching (0-100)"""
        score = 0
        patterns = mp3.get('patterns', {})
        
        # Match par numéro de track
        if 'track' in patterns:
            track_num = patterns['track']
            
            # Vérifier dans le titre
            if str(track_num) in exercise.get('title', ''):
                score += 30
            
            # Pattern simple : Track X → Pattern X
            pattern_match = re.search(r'Pattern\s*(\d+)', exercise.get('title', ''))
            if pattern_match and int(pattern_match.group(1)) == track_num:
                score += 50
        
        # Match par page
        if 'page' in patterns:
            page_num = patterns['page']
            exercise_page = exercise.get('page')
            
            if exercise_page == page_num:
                score += 60
            elif exercise_page and abs(exercise_page - page_num) <= 1:
                score += 40
        
        # Match par exercice
        if 'exercise' in patterns:
            exercise_num = patterns['exercise']
            if str(exercise_num) in exercise.get('title', ''):
                score += 50
        
        # Match par style
        if 'style' in patterns:
            mp3_style = patterns['style']
            exercise_technique = exercise.get('technique', '').lower()
            
            if mp3_style in exercise_technique:
                score += 20
        
        return score
    
    # ==========================================
    # ÉTAPE 4 : GÉNÉRATION
    # ==========================================
    
    def generate_mapping(self):
        """Génère mp3_mapping.json"""
        print("💾 ÉTAPE 4 : Génération mp3_mapping.json...\n")
        
        from datetime import datetime
        
        mapping = {
            'metadata': {
                'version': '2.0.0',
                'generated_at': datetime.now().isoformat(),
                'total_mp3': self.stats['total_mp3'],
                'total_exercises': self.stats['total_exercises'],
                'matched': self.stats['matched'],
                'match_rate': f"{(self.stats['matched'] / max(self.stats['total_mp3'], 1) * 100):.1f}%"
            },
            'stats': self.stats,
            'mappings': []
        }
        
        for match in self.matches:
            mapping['mappings'].append({
                'exercise_id': match['exercise']['id'],
                'exercise_title': match['exercise'].get('title', ''),
                'exercise_page': match['exercise'].get('page'),
                'exercise_technique': match['exercise'].get('technique', ''),
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
    
    def update_megasearch(self):
        """Met à jour megasearch.json"""
        print("\n🔄 ÉTAPE 5 : Mise à jour megasearch.json...\n")
        
        megasearch_file = self.repo_root / 'megasearch.json'
        
        if not megasearch_file.exists():
            print("⚠️ megasearch.json introuvable (pas grave)")
            return
        
        with open(megasearch_file, 'r', encoding='utf-8') as f:
            megasearch = json.load(f)
        
        # Créer index des mappings par exercise_id
        mp3_by_exercise_id = {}
        for match in self.matches:
            exercise_id = match['exercise']['id']
            mp3_by_exercise_id[exercise_id] = {
                'mp3_url': match['mp3']['url'],
                'mp3_filename': match['mp3']['filename'],
                'confidence': match['confidence']
            }
        
        # Mettre à jour les ressources
        updated_count = 0
        for resource in megasearch.get('resources', []):
            resource_id = resource.get('id')
            
            if resource_id in mp3_by_exercise_id:
                mp3_info = mp3_by_exercise_id[resource_id]
                
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
    
    def print_summary(self):
        """Affiche résumé"""
        print("\n" + "="*60)
        print("🎵 RÉSUMÉ FINAL")
        print("="*60)
        print(f"📊 Fichiers MP3          : {self.stats['total_mp3']}")
        print(f"📚 Exercices             : {self.stats['total_exercises']}")
        print(f"✅ Correspondances       : {self.stats['matched']}")
        print(f"❌ MP3 non matchés       : {self.stats['unmatched_mp3']}")
        
        if self.stats['total_mp3'] > 0:
            match_rate = (self.stats['matched'] / self.stats['total_mp3']) * 100
            print(f"\n🎯 Taux de réussite : {match_rate:.1f}%")
        
        print("="*60)
        
        # Top 10
        if self.matches:
            print("\n🏆 TOP 10 DES MEILLEURES CORRESPONDANCES:\n")
            sorted_matches = sorted(self.matches, key=lambda x: x['confidence'], reverse=True)
            for i, match in enumerate(sorted_matches[:10], 1):
                print(f"{i}. {match['mp3']['filename']}")
                print(f"   → {match['exercise'].get('title', 'Sans titre')}")
                print(f"   Page {match['exercise'].get('page', '?')} - Confiance : {match['confidence']:.0%}\n")
    
    def run(self):
        """Exécute le workflow complet"""
        print("🚀 DÉMARRAGE MP3 MATCHING SYSTEM V2\n")
        print("="*60 + "\n")
        
        if not self.load_mp3_index():
            return
        
        self.load_exercises()
        self.match_by_method()
        self.generate_mapping()
        self.update_megasearch()
        self.print_summary()


if __name__ == '__main__':
    import sys
    import re
    
    repo_root = Path.cwd()
    if len(sys.argv) > 1:
        repo_root = Path(sys.argv[1])
    
    print(f"📂 Repository : {repo_root}\n")
    
    matcher = MP3MatcherV2(repo_root)
    matcher.run()
    
    print("\n✅ TERMINÉ !")
