#!/usr/bin/env python3
"""
🎸 Prof de Basse - Validation Structure JSON
Valide TOUS les fichiers JSON du repo (Pratique.json, songs_index.json, etc.)
"""

import json
import sys
from pathlib import Path
from typing import Dict, List

# ============================================
# SCHÉMAS ATTENDUS
# ============================================

# Format standard v4.0 (Pratique.json)
SCHEMA_V4_REQUIRED = {
    'metadata': ['version', 'book_name', 'category', 'total_resources'],
    'resources': ['id', 'type', 'title', 'page', 'url']
}

# Format songs_index.json (ancien format)
SCHEMA_SONGS_REQUIRED = {
    'songs': ['id', 'title', 'page', 'url']
}

class JSONValidator:
    def __init__(self):
        self.errors = []
        self.warnings = []
        self.validated_count = 0
        self.total_resources = 0
    
    def validate_file(self, json_file: Path) -> bool:
        """Valide un fichier JSON"""
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Déterminer le format
            if 'metadata' in data and 'resources' in data:
                return self.validate_v4_format(json_file, data)
            elif 'songs' in data:
                return self.validate_songs_format(json_file, data)
            else:
                self.warnings.append(f"⚠️  {json_file.name}: Format non standard (ignoré)")
                return True
        
        except json.JSONDecodeError as e:
            self.errors.append(f"❌ {json_file.name}: JSON invalide - {e}")
            return False
        except Exception as e:
            self.errors.append(f"❌ {json_file.name}: Erreur - {e}")
            return False
    
    def validate_v4_format(self, json_file: Path, data: Dict) -> bool:
        """Valide format v4.0 (Pratique.json)"""
        valid = True
        
        # Vérifier metadata
        metadata = data.get('metadata', {})
        for field in SCHEMA_V4_REQUIRED['metadata']:
            if field not in metadata:
                self.errors.append(f"❌ {json_file.name}: metadata.{field} manquant")
                valid = False
        
        # Vérifier resources
        resources = data.get('resources', [])
        if not isinstance(resources, list):
            self.errors.append(f"❌ {json_file.name}: resources doit être une liste")
            return False
        
        # Vérifier chaque ressource
        for i, resource in enumerate(resources):
            for field in SCHEMA_V4_REQUIRED['resources']:
                if field not in resource:
                    self.errors.append(
                        f"❌ {json_file.name}: resource[{i}].{field} manquant"
                    )
                    valid = False
        
        if valid:
            self.validated_count += 1
            self.total_resources += len(resources)
            print(f"✅ {json_file.name}: {len(resources)} ressources")
        
        return valid
    
    def validate_songs_format(self, json_file: Path, data: Dict) -> bool:
        """Valide format songs_index.json"""
        valid = True
        
        songs = data.get('songs', [])
        if not isinstance(songs, list):
            self.errors.append(f"❌ {json_file.name}: songs doit être une liste")
            return False
        
        # Vérifier chaque song
        for i, song in enumerate(songs):
            for field in SCHEMA_SONGS_REQUIRED['songs']:
                if field not in song:
                    self.errors.append(
                        f"❌ {json_file.name}: songs[{i}].{field} manquant"
                    )
                    valid = False
        
        if valid:
            self.validated_count += 1
            self.total_resources += len(songs)
            print(f"✅ {json_file.name}: {len(songs)} chansons")
        
        return valid
    
    def validate_all(self, base_path: Path = Path('.')) -> bool:
        """Valide tous les JSON du repo"""
        print("="*60)
        print("🔍 VALIDATION STRUCTURE JSON")
        print("="*60)
        print()
        
        # Trouver tous les JSON
        json_files = []
        
        # Format v4.0
        json_files.extend(base_path.glob('Base de connaissances/**/*_v4.0/*.json'))
        
        # Format ancien (songs_index.json)
        json_files.extend(base_path.glob('Base de connaissances/**/songs_index.json'))
        
        # Exclure .git et node_modules
        json_files = [f for f in json_files if '.git' not in str(f) and 'node_modules' not in str(f)]
        
        if not json_files:
            print("⚠️  Aucun fichier JSON trouvé")
            return True
        
        print(f"📊 {len(json_files)} fichiers JSON trouvés\n")
        
        # Valider
        all_valid = True
        for json_file in sorted(json_files):
            if not self.validate_file(json_file):
                all_valid = False
        
        # Résumé
        print()
        print("="*60)
        print("📊 RÉSUMÉ")
        print("="*60)
        print(f"✅ Fichiers validés : {self.validated_count}")
        print(f"📚 Ressources totales : {self.total_resources}")
        print(f"⚠️  Avertissements : {len(self.warnings)}")
        print(f"❌ Erreurs : {len(self.errors)}")
        
        if self.warnings:
            print("\n⚠️  AVERTISSEMENTS:")
            for warning in self.warnings:
                print(f"  {warning}")
        
        if self.errors:
            print("\n❌ ERREURS:")
            for error in self.errors:
                print(f"  {error}")
        
        print("="*60)
        
        if all_valid:
            print("\n🎉 Validation réussie !\n")
        else:
            print("\n💥 Validation échouée - Corrigez les erreurs\n")
        
        return all_valid

def main():
    validator = JSONValidator()
    success = validator.validate_all()
    sys.exit(0 if success else 1)

if __name__ == '__main__':
    main()
