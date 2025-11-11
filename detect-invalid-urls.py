#!/usr/bin/env python3
"""
Détecte toutes les sources de URLs invalides dans le repo
"""
import os
import re
from pathlib import Path

def scan_file_for_issues(filepath):
    """Scanne un fichier pour détecter des problèmes d'URLs"""
    issues = []
    
    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
            lines = content.split('\n')
        
        for i, line in enumerate(lines, 1):
            # Chercher "undefined" dans les URLs
            if 'undefined' in line.lower() and ('http' in line or 'url' in line.lower()):
                issues.append({
                    'file': filepath,
                    'line': i,
                    'type': 'undefined_in_url',
                    'content': line.strip()[:100]
                })
            
            # Chercher des patterns de variables non définies
            patterns = [
                r'\$\{[^}]*undefined[^}]*\}',  # ${...undefined...}
                r'\{\{[^}]*undefined[^}]*\}\}',  # {{...undefined...}}
                r'href="[^"]*undefined[^"]*"',   # href="...undefined..."
                r'src="[^"]*undefined[^"]*"',    # src="...undefined..."
            ]
            
            for pattern in patterns:
                if re.search(pattern, line, re.IGNORECASE):
                    issues.append({
                        'file': filepath,
                        'line': i,
                        'type': 'undefined_variable',
                        'content': line.strip()[:100]
                    })
            
            # Chercher des URLs incomplètes
            if re.search(r'Prof-de-basse-V2/\s*["\']', line):
                issues.append({
                    'file': filepath,
                    'line': i,
                    'type': 'incomplete_url',
                    'content': line.strip()[:100]
                })
            
            # Chercher des concatenations suspectes
            if re.search(r'\+\s*undefined|\bundefined\s*\+', line, re.IGNORECASE):
                issues.append({
                    'file': filepath,
                    'line': i,
                    'type': 'concatenation_issue',
                    'content': line.strip()[:100]
                })
    
    except Exception as e:
        pass
    
    return issues

def main():
    print("="*70)
    print("🔍 DÉTECTION DES SOURCES DE URLs INVALIDES")
    print("="*70 + "\n")
    
    # Extensions à scanner
    extensions = ['.html', '.js', '.json', '.md', '.py']
    
    # Répertoires à ignorer
    ignore_dirs = {'.git', 'node_modules', '__pycache__', '.DS_Store'}
    
    all_issues = []
    
    # Scanner tous les fichiers
    for root, dirs, files in os.walk('.'):
        # Filtrer les répertoires à ignorer
        dirs[:] = [d for d in dirs if d not in ignore_dirs]
        
        for file in files:
            if any(file.endswith(ext) for ext in extensions):
                filepath = os.path.join(root, file)
                issues = scan_file_for_issues(filepath)
                if issues:
                    all_issues.extend(issues)
    
    # Afficher les résultats par type
    if all_issues:
        print("⚠️  PROBLÈMES DÉTECTÉS :\n")
        
        by_type = {}
        for issue in all_issues:
            issue_type = issue['type']
            if issue_type not in by_type:
                by_type[issue_type] = []
            by_type[issue_type].append(issue)
        
        for issue_type, issues in by_type.items():
            print(f"\n📌 {issue_type.upper().replace('_', ' ')} ({len(issues)} occurrences)")
            print("-" * 70)
            
            # Grouper par fichier
            by_file = {}
            for issue in issues:
                filepath = issue['file']
                if filepath not in by_file:
                    by_file[filepath] = []
                by_file[filepath].append(issue)
            
            for filepath, file_issues in list(by_file.items())[:5]:  # Top 5 fichiers
                print(f"\n   📄 {filepath}")
                for issue in file_issues[:3]:  # Top 3 lignes par fichier
                    print(f"      Ligne {issue['line']}: {issue['content']}")
                if len(file_issues) > 3:
                    print(f"      ... (+{len(file_issues)-3} autres)")
        
        print("\n" + "="*70)
        print(f"📊 TOTAL : {len(all_issues)} problèmes détectés dans {len(set(i['file'] for i in all_issues))} fichiers")
        print("="*70 + "\n")
        
        # Fichiers les plus problématiques
        file_counts = {}
        for issue in all_issues:
            file_counts[issue['file']] = file_counts.get(issue['file'], 0) + 1
        
        print("\n🎯 Fichiers les plus problématiques :")
        for filepath, count in sorted(file_counts.items(), key=lambda x: x[1], reverse=True)[:10]:
            print(f"   • {filepath}: {count} problèmes")
    
    else:
        print("✅ Aucun problème détecté !")
    
    print()

if __name__ == '__main__':
    main()
