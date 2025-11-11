#!/usr/bin/env python3
"""
Programme de modification d'URLs pour Prof de Basse
Modifie les URLs dans les fichiers HTML, JSON, MD, etc.
"""

import os
import json
import re
from pathlib import Path
from typing import List, Dict, Tuple

class URLFixer:
    def __init__(self, repo_path: str):
        self.repo_path = Path(repo_path)
        self.changes_made = []
        
    def find_files(self, extensions: List[str]) -> List[Path]:
        """Trouve tous les fichiers avec les extensions données"""
        files = []
        for ext in extensions:
            files.extend(self.repo_path.rglob(f"*{ext}"))
        return files
    
    def replace_in_file(self, filepath: Path, old_pattern: str, new_pattern: str) -> int:
        """Remplace un pattern dans un fichier"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Compter les occurrences
            count = content.count(old_pattern)
            
            if count > 0:
                # Faire le remplacement
                new_content = content.replace(old_pattern, new_pattern)
                
                # Écrire le fichier
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(new_content)
                
                self.changes_made.append({
                    'file': str(filepath.relative_to(self.repo_path)),
                    'old': old_pattern,
                    'new': new_pattern,
                    'count': count
                })
                
                return count
            
            return 0
        
        except Exception as e:
            print(f"❌ Erreur sur {filepath}: {e}")
            return 0
    
    def replace_regex_in_file(self, filepath: Path, pattern: str, replacement: str) -> int:
        """Remplace avec regex dans un fichier"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Compter les matches
            matches = re.findall(pattern, content)
            count = len(matches)
            
            if count > 0:
                # Faire le remplacement
                new_content = re.sub(pattern, replacement, content)
                
                # Écrire le fichier
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(new_content)
                
                self.changes_made.append({
                    'file': str(filepath.relative_to(self.repo_path)),
                    'pattern': pattern,
                    'replacement': replacement,
                    'count': count
                })
                
                return count
            
            return 0
        
        except Exception as e:
            print(f"❌ Erreur sur {filepath}: {e}")
            return 0
    
    def fix_github_pages_urls(self):
        """Corrige les URLs GitHub Pages"""
        print("🔧 Correction des URLs GitHub Pages...")
        
        old_base = "https://11drumboy11.github.io/Prof-de-basse/"
        new_base = "https://11drumboy11.github.io/Prof-de-basse-V2/"
        
        files = self.find_files(['.html', '.js', '.json', '.md'])
        
        total = 0
        for file in files:
            count = self.replace_in_file(file, old_base, new_base)
            total += count
        
        print(f"✅ {total} URLs GitHub Pages corrigées")
        return total
    
    def fix_mp3_urls(self):
        """Corrige les URLs MP3 avec encodage correct"""
        print("🔧 Correction des URLs MP3...")
        
        # Pattern : Track XX.mp3 → Track%20XX.mp3
        pattern = r'(/MP3/[^"\']*Track )(\d+)(\.mp3)'
        replacement = r'\1%20\2\3'
        
        files = self.find_files(['.html', '.js', '.json'])
        
        total = 0
        for file in files:
            count = self.replace_regex_in_file(file, pattern, replacement)
            total += count
        
        print(f"✅ {total} URLs MP3 corrigées")
        return total
    
    def fix_spaces_in_urls(self):
        """Remplace les espaces par %20 dans les URLs"""
        print("🔧 Correction des espaces dans les URLs...")
        
        # Pattern : URLs avec espaces
        pattern = r'(https://[^"\'\s]+) ([^"\'\s]+)'
        
        files = self.find_files(['.html', '.js', '.json'])
        
        total = 0
        for file in files:
            try:
                with open(file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Remplacer les espaces dans les URLs
                new_content = content
                while re.search(pattern, new_content):
                    new_content = re.sub(pattern, r'\1%20\2', new_content)
                
                if new_content != content:
                    with open(file, 'w', encoding='utf-8') as f:
                        f.write(new_content)
                    total += 1
            
            except Exception as e:
                print(f"❌ Erreur sur {file}: {e}")
        
        print(f"✅ {total} fichiers corrigés")
        return total
    
    def fix_json_index_urls(self):
        """Corrige les URLs dans les index JSON"""
        print("🔧 Correction des URLs dans les index JSON...")
        
        json_files = self.find_files(['.json'])
        
        total = 0
        for json_file in json_files:
            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                # Parcourir récursivement et corriger les URLs
                modified = self._fix_urls_recursive(data)
                
                if modified:
                    with open(json_file, 'w', encoding='utf-8') as f:
                        json.dump(data, f, indent=2, ensure_ascii=False)
                    total += 1
                    print(f"  ✅ {json_file.name}")
            
            except Exception as e:
                print(f"  ⚠️  {json_file.name}: {e}")
        
        print(f"✅ {total} fichiers JSON corrigés")
        return total
    
    def _fix_urls_recursive(self, obj, modified=False):
        """Corrige les URLs récursivement dans un objet JSON"""
        if isinstance(obj, dict):
            for key, value in obj.items():
                if isinstance(value, str) and ('http://' in value or 'https://' in value):
                    # Corriger l'URL
                    new_value = value.replace('Prof-de-basse/', 'Prof-de-basse-V2/')
                    new_value = re.sub(r' ', '%20', new_value)
                    if new_value != value:
                        obj[key] = new_value
                        modified = True
                elif isinstance(value, (dict, list)):
                    modified = self._fix_urls_recursive(value, modified) or modified
        
        elif isinstance(obj, list):
            for i, item in enumerate(obj):
                if isinstance(item, str) and ('http://' in item or 'https://' in item):
                    new_item = item.replace('Prof-de-basse/', 'Prof-de-basse-V2/')
                    new_item = re.sub(r' ', '%20', new_item)
                    if new_item != item:
                        obj[i] = new_item
                        modified = True
                elif isinstance(item, (dict, list)):
                    modified = self._fix_urls_recursive(item, modified) or modified
        
        return modified
    
    def show_report(self):
        """Affiche le rapport des modifications"""
        print("\n" + "="*60)
        print("📊 RAPPORT DES MODIFICATIONS")
        print("="*60 + "\n")
        
        if not self.changes_made:
            print("ℹ️  Aucune modification effectuée")
            return
        
        # Grouper par fichier
        by_file = {}
        for change in self.changes_made:
            file = change['file']
            if file not in by_file:
                by_file[file] = []
            by_file[file].append(change)
        
        # Afficher
        for file, changes in by_file.items():
            print(f"📄 {file}")
            for change in changes:
                if 'old' in change:
                    print(f"   {change['old']}")
                    print(f"   → {change['new']}")
                    print(f"   ({change['count']} occurrence(s))")
                else:
                    print(f"   Pattern: {change['pattern']}")
                    print(f"   ({change['count']} occurrence(s))")
            print()
        
        print(f"✅ Total: {len(self.changes_made)} modifications dans {len(by_file)} fichiers")


def main():
    """Menu principal"""
    print("""
╔═══════════════════════════════════════════════════════════╗
║           🔧 FIXEUR D'URLS - PROF DE BASSE 🎸            ║
╚═══════════════════════════════════════════════════════════╝
    """)
    
    # Chemin du repo
    repo_path = input("📂 Chemin du repo (ou Enter pour chemin actuel): ").strip()
    if not repo_path:
        repo_path = "."
    
    fixer = URLFixer(repo_path)
    
    while True:
        print("\n" + "="*60)
        print("OPTIONS:")
        print("="*60)
        print("1. Corriger URLs GitHub Pages (Prof-de-basse → Prof-de-basse-V2)")
        print("2. Corriger URLs MP3 (espaces → %20)")
        print("3. Corriger tous les espaces dans les URLs")
        print("4. Corriger URLs dans les JSON")
        print("5. TOUT CORRIGER (recommandé)")
        print("6. Afficher le rapport")
        print("0. Quitter")
        print("="*60)
        
        choice = input("\n👉 Choix: ").strip()
        
        if choice == "1":
            fixer.fix_github_pages_urls()
        
        elif choice == "2":
            fixer.fix_mp3_urls()
        
        elif choice == "3":
            fixer.fix_spaces_in_urls()
        
        elif choice == "4":
            fixer.fix_json_index_urls()
        
        elif choice == "5":
            print("\n🚀 CORRECTION COMPLÈTE EN COURS...\n")
            fixer.fix_github_pages_urls()
            fixer.fix_mp3_urls()
            fixer.fix_spaces_in_urls()
            fixer.fix_json_index_urls()
            print("\n✅ TOUTES LES CORRECTIONS TERMINÉES!")
        
        elif choice == "6":
            fixer.show_report()
        
        elif choice == "0":
            print("\n👋 Au revoir!")
            break
        
        else:
            print("❌ Choix invalide")
    
    # Rapport final
    if fixer.changes_made:
        print("\n📋 RÉSUMÉ FINAL:")
        fixer.show_report()
        
        # Demander si on commit
        commit = input("\n💾 Commit et push les changements? (y/N): ").strip().lower()
        if commit == 'y':
            print("\n📦 Git commands à exécuter:")
            print("  git add .")
            print("  git commit -m 'Fix URLs'")
            print("  git push origin main")


if __name__ == "__main__":
    main()
