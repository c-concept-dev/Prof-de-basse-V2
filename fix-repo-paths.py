#!/usr/bin/env python3
"""
Corrige tous les chemins qui pointent vers l'ancien repo
"""

import os
import re
from pathlib import Path

def fix_paths_in_file(filepath, old_path, new_path):
    """Corrige les chemins dans un fichier"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        if old_path in content:
            new_content = content.replace(old_path, new_path)
            
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(new_content)
            
            return True
        
        return False
    
    except Exception as e:
        print(f"❌ Erreur sur {filepath}: {e}")
        return False

def main():
    print("🔧 Correction des chemins dans le repo...\n")
    
    repo_path = Path(".")
    
    # Patterns à corriger
    old_patterns = [
        "/Users/christophebonnet/Documents/GitHub/Prof-de-basse-V2/Prof-de-basse-V2/",
        "Prof-de-basse-V2/",
        "11drumboy11.github.io/Prof-de-basse-V2/"
    ]
    
    new_patterns = [
        "/Users/christophebonnet/Documents/GitHub/Prof-de-basse-V2/Prof-de-basse-V2/",
        "Prof-de-basse-V2/",
        "11drumboy11.github.io/Prof-de-basse-V2/"
    ]
    
    # Fichiers à vérifier
    extensions = ['.py', '.sh', '.yml', '.yaml', '.json', '.md']
    
    files_to_check = []
    for ext in extensions:
        files_to_check.extend(repo_path.rglob(f"*{ext}"))
    
    print(f"📁 {len(files_to_check)} fichiers à vérifier\n")
    
    fixed_files = []
    
    for filepath in files_to_check:
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            
            modified = False
            new_content = content
            
            # Tester chaque pattern
            for old, new in zip(old_patterns, new_patterns):
                if old in new_content:
                    new_content = new_content.replace(old, new)
                    modified = True
            
            if modified:
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(new_content)
                
                fixed_files.append(str(filepath.relative_to(repo_path)))
                print(f"✅ {filepath.relative_to(repo_path)}")
        
        except Exception as e:
            pass  # Ignorer les fichiers binaires
    
    print(f"\n✅ {len(fixed_files)} fichiers corrigés")
    
    if fixed_files:
        print("\n📋 Fichiers modifiés:")
        for f in fixed_files:
            print(f"   - {f}")
        
        print("\n🔧 Commandes Git:")
        print("   git add .")
        print("   git commit -m 'Fix repository paths'")
        print("   git push origin main")

if __name__ == "__main__":
    main()
