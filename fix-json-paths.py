#!/usr/bin/env python3
"""
Corrige les chemins dans assets_ocr_index.json et megasearch.json
pour correspondre à la structure réelle sur GitHub
"""

import json
import re
from pathlib import Path
from datetime import datetime

def print_header(title):
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80 + "\n")

def apply_path_corrections(path):
    """
    Applique les corrections de chemins pour correspondre à la structure réelle
    
    Corrections connues:
    - Arpeges → Arpeges_v4.0
    - /assets/ → /assets/pages/
    - Etc. (à compléter selon structure réelle)
    """
    
    corrections = []
    original_path = path
    
    # Correction 1: Arpeges → Arpeges_v4.0
    if '/Arpeges/' in path and '_v' not in path:
        path = path.replace('/Arpeges/', '/Arpeges_v4.0/')
        corrections.append('Arpeges → Arpeges_v4.0')
    
    # Correction 2: /assets/ → /assets/pages/ (si pas déjà présent)
    if '/assets/' in path and '/assets/pages/' not in path:
        path = path.replace('/assets/', '/assets/pages/')
        corrections.append('assets → assets/pages')
    
    # Retourner le chemin corrigé et les corrections appliquées
    return path, corrections

def fix_json_file(input_file, output_file=None):
    """Corrige les chemins dans un fichier JSON"""
    
    if output_file is None:
        output_file = input_file
    
    print(f"📂 Traitement de {input_file}...")
    
    # Lire le fichier
    with open(input_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Backup
    backup_file = f"{input_file}.backup-path-fix-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
    with open(backup_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(f"✅ Backup créé: {backup_file}\n")
    
    # Statistiques
    stats = {
        'total': 0,
        'corrected': 0,
        'unchanged': 0,
        'corrections_by_type': {}
    }
    
    # Traiter les ressources
    if isinstance(data.get('resources'), list):
        resources = data['resources']
    elif isinstance(data.get('resources'), dict):
        # Convertir dict → array si nécessaire
        resources = list(data['resources'].values())
    else:
        print("❌ Structure 'resources' non reconnue")
        return stats
    
    print(f"📊 Total ressources: {len(resources)}\n")
    print("🔧 Application des corrections...\n")
    
    corrected_resources = []
    
    for resource in resources:
        stats['total'] += 1
        
        # Récupérer le path
        path = resource.get('path', '')
        url = resource.get('url', '')
        resource_id = resource.get('id', '')
        
        if not path:
            corrected_resources.append(resource)
            stats['unchanged'] += 1
            continue
        
        # Appliquer les corrections
        new_path, corrections = apply_path_corrections(path)
        
        if new_path != path:
            stats['corrected'] += 1
            
            # Compter les types de corrections
            for correction in corrections:
                stats['corrections_by_type'][correction] = \
                    stats['corrections_by_type'].get(correction, 0) + 1
            
            # Afficher les premières corrections
            if stats['corrected'] <= 5:
                print(f"📝 Correction #{stats['corrected']}:")
                print(f"   AVANT: {path}")
                print(f"   APRÈS: {new_path}")
                print(f"   Types: {', '.join(corrections)}")
                print()
            
            # Mettre à jour le resource
            resource['path'] = new_path
            
            # Mettre à jour l'URL si nécessaire
            if url:
                # Reconstruire l'URL avec le nouveau path
                base_url = 'https://11drumboy11.github.io/Prof-de-basse-V2/'
                # Encoder les espaces
                encoded_path = new_path.replace(' ', '%20')
                new_url = base_url + encoded_path
                resource['url'] = new_url
            
            # Mettre à jour l'ID si nécessaire
            if resource_id and resource_id == path:
                resource['id'] = new_path.replace(' ', '%20')
        else:
            stats['unchanged'] += 1
        
        corrected_resources.append(resource)
    
    # Mettre à jour les ressources
    if isinstance(data.get('resources'), list):
        data['resources'] = corrected_resources
    elif isinstance(data.get('resources'), dict):
        # Reconstruire le dict
        data['resources'] = {r.get('id', str(i)): r 
                           for i, r in enumerate(corrected_resources)}
    
    # Sauvegarder
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    print(f"\n✅ Fichier corrigé sauvegardé: {output_file}\n")
    
    return stats

def main():
    print("=" * 80)
    print("  🔧 CORRECTION DES CHEMINS - Prof de Basse V2")
    print("=" * 80)
    
    print("\n📋 Ce script corrige les chemins dans les fichiers JSON pour")
    print("   correspondre à la structure réelle sur GitHub\n")
    
    # Liste des fichiers à corriger
    files_to_fix = [
        'assets_ocr_index.json',
        'megasearch.json',
        'mega-search-index.json'
    ]
    
    all_stats = {}
    
    for filename in files_to_fix:
        if Path(filename).exists():
            print_header(f"Traitement de {filename}")
            
            stats = fix_json_file(filename)
            all_stats[filename] = stats
            
            print(f"📊 Statistiques {filename}:")
            print(f"   Total: {stats['total']}")
            print(f"   Corrigé: {stats['corrected']}")
            print(f"   Inchangé: {stats['unchanged']}")
            
            if stats['corrections_by_type']:
                print(f"\n   Types de corrections:")
                for corr_type, count in stats['corrections_by_type'].items():
                    print(f"      • {corr_type}: {count}x")
            print()
        else:
            print(f"⚠️  {filename} non trouvé, ignoré\n")
    
    # Résumé global
    print_header("📊 RÉSUMÉ GLOBAL")
    
    total_corrected = sum(s['corrected'] for s in all_stats.values())
    total_resources = sum(s['total'] for s in all_stats.values())
    
    print(f"Total ressources traitées: {total_resources}")
    print(f"Total corrections appliquées: {total_corrected}")
    print(f"Pourcentage corrigé: {total_corrected/total_resources*100:.1f}%")
    
    print("\n" + "=" * 80)
    print("📝 PROCHAINES ÉTAPES")
    print("=" * 80 + "\n")
    
    print("""
1. Vérifier les corrections:
   
   # Tester une URL corrigée
   python3 -c "
   import json
   d = json.load(open('megasearch.json'))
   r = [r for r in d['resources'] if 'Arpeges' in r['path']][0]
   print(r['url'])
   "

2. Tester l'URL dans le navigateur:
   
   Copier l'URL et vérifier qu'elle fonctionne

3. Si OK, commit:
   
   git add assets_ocr_index.json megasearch.json
   git commit -m "Fix: Chemins corrigés (Arpeges_v4.0 + /pages/)"
   git push origin main

4. Si les corrections sont incomplètes:
   
   Éditer ce script et ajouter d'autres corrections
   dans la fonction apply_path_corrections()
    """)
    
    print("\n💡 NOTE IMPORTANTE:")
    print("   Ce script corrige UNIQUEMENT:")
    print("   - Arpeges → Arpeges_v4.0")
    print("   - /assets/ → /assets/pages/")
    print("\n   Si d'autres dossiers ont des versions (_vX.X),")
    print("   il faut les ajouter dans apply_path_corrections()")

if __name__ == '__main__':
    main()
