#!/usr/bin/env python3
"""
Correction DÉFINITIVE - Enlever _v4.0 des dossiers PARENTS
Structure réelle: Theorie/Arpeges_v4.0/ (PAS Theorie_v4.0/Arpeges_v4.0/)
"""

import json
from pathlib import Path
from datetime import datetime

def print_header(title):
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80 + "\n")

def remove_parent_versions(path):
    """
    Enlève _v4.0 des dossiers PARENTS uniquement
    
    AVANT:
    Base de connaissances/Theorie_v4.0/Arpeges_v4.0/assets/pages/page_056.png
    
    APRÈS:
    Base de connaissances/Theorie/Arpeges_v4.0/assets/pages/page_056.png
                          ↑       ↑
                       Enlevé   Gardé
    """
    
    corrections = []
    original_path = path
    
    # Dossiers PARENTS qui ne doivent PAS avoir _v4.0
    parent_folders = [
        'Theorie',
        'Methodes', 
        'Partitions'
    ]
    
    # Enlever _v4.0 des parents
    for parent in parent_folders:
        old_pattern = f'/{parent}_v4.0/'
        new_pattern = f'/{parent}/'
        
        if old_pattern in path:
            path = path.replace(old_pattern, new_pattern)
            corrections.append(f'{parent}_v4.0 → {parent}')
    
    return path, corrections

def fix_json_file(input_file, dry_run=False):
    """Corrige les chemins dans un fichier JSON"""
    
    print(f"📂 Traitement de {input_file}...")
    
    if not Path(input_file).exists():
        print(f"⚠️  Fichier non trouvé: {input_file}\n")
        return None
    
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except Exception as e:
        print(f"❌ Erreur lecture: {e}\n")
        return None
    
    # Backup
    if not dry_run:
        backup_file = f"{input_file}.backup-remove-parent-v4-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
        with open(backup_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print(f"✅ Backup créé: {backup_file}\n")
    
    stats = {
        'total': 0,
        'corrected': 0,
        'unchanged': 0,
        'corrections_by_type': {},
        'examples': []
    }
    
    if isinstance(data.get('resources'), list):
        resources = data['resources']
    elif isinstance(data.get('resources'), dict):
        resources = list(data['resources'].values())
    else:
        print("❌ Structure 'resources' non reconnue\n")
        return stats
    
    print(f"📊 Total ressources: {len(resources)}\n")
    
    if dry_run:
        print("🔍 MODE DRY-RUN: Simulation...\n")
    else:
        print("⚡ MODE RÉEL: Application des corrections...\n")
    
    corrected_resources = []
    
    for resource in resources:
        stats['total'] += 1
        
        path = resource.get('path', '')
        url = resource.get('url', '')
        resource_id = resource.get('id', '')
        
        if not path:
            corrected_resources.append(resource)
            stats['unchanged'] += 1
            continue
        
        # Corriger le path
        new_path, corrections = remove_parent_versions(path)
        
        if new_path != path:
            stats['corrected'] += 1
            
            for correction in corrections:
                stats['corrections_by_type'][correction] = \
                    stats['corrections_by_type'].get(correction, 0) + 1
            
            if len(stats['examples']) < 5:
                stats['examples'].append({
                    'original': path,
                    'corrected': new_path,
                    'corrections': corrections
                })
            
            if stats['corrected'] <= 3:
                print(f"📝 Correction #{stats['corrected']}:")
                print(f"   AVANT: {path}")
                print(f"   APRÈS: {new_path}")
                print(f"   Types: {', '.join(corrections)}")
                print()
            
            if not dry_run:
                resource['path'] = new_path
                
                # Reconstruire l'URL
                base_url = 'https://11drumboy11.github.io/Prof-de-basse-V2/Prof-de-basse-V2/'
                encoded_path = new_path.replace(' ', '%20')
                new_url = base_url + encoded_path
                resource['url'] = new_url
                
                if resource_id:
                    resource['id'] = new_path.replace(' ', '%20')
        else:
            stats['unchanged'] += 1
        
        corrected_resources.append(resource)
    
    if stats['corrected'] > 3:
        print(f"... ({stats['corrected'] - 3} autres corrections)\n")
    
    if not dry_run:
        if isinstance(data.get('resources'), list):
            data['resources'] = corrected_resources
        elif isinstance(data.get('resources'), dict):
            data['resources'] = {r.get('id', str(i)): r 
                               for i, r in enumerate(corrected_resources)}
        
        with open(input_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Fichier corrigé: {input_file}\n")
    else:
        print(f"🔍 DRY-RUN: Aucune modification\n")
    
    return stats

def main():
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Enlever _v4.0 des dossiers PARENTS'
    )
    parser.add_argument('--dry-run', action='store_true', help='Simuler')
    parser.add_argument(
        '--files',
        nargs='+',
        default=['assets_ocr_index.json', 'megasearch.json', 'mega-search-index.json'],
        help='Fichiers à corriger'
    )
    
    args = parser.parse_args()
    
    print("=" * 80)
    print("  🔧 CORRECTION DÉFINITIVE - Enlever _v4.0 des parents")
    print("=" * 80)
    print("\n📝 Structure RÉELLE:")
    print("   Base de connaissances/Theorie/Arpeges_v4.0/assets/pages/")
    print("                         ↑       ↑")
    print("                      PAS _v4.0  AVEC _v4.0")
    print("\n📝 Ce script ENLÈVE _v4.0 de:")
    print("   • Theorie_v4.0 → Theorie")
    print("   • Methodes_v4.0 → Methodes")
    print("   • Partitions_v4.0 → Partitions\n")
    
    if args.dry_run:
        print("🔍 MODE DRY-RUN\n")
    else:
        print("⚡ MODE RÉEL\n")
        response = input("Continuer ? (oui/non): ")
        if response.lower() not in ['oui', 'yes', 'y', 'o']:
            print("\n❌ Annulé")
            return
        print()
    
    all_stats = {}
    
    for filename in args.files:
        print_header(f"Traitement de {filename}")
        
        stats = fix_json_file(filename, dry_run=args.dry_run)
        
        if stats:
            all_stats[filename] = stats
            
            print(f"📊 Statistiques {filename}:")
            print(f"   Total: {stats['total']}")
            print(f"   Corrigé: {stats['corrected']} ({stats['corrected']/stats['total']*100:.1f}%)")
            print(f"   Inchangé: {stats['unchanged']}")
            
            if stats['corrections_by_type']:
                print(f"\n   Types de corrections:")
                for corr_type, count in sorted(
                    stats['corrections_by_type'].items(), 
                    key=lambda x: x[1], 
                    reverse=True
                ):
                    print(f"      • {corr_type}: {count}x")
            print()
    
    print_header("📊 RÉSUMÉ GLOBAL")
    
    total_corrected = sum(s['corrected'] for s in all_stats.values())
    total_resources = sum(s['total'] for s in all_stats.values())
    
    print(f"📈 Total ressources: {total_resources}")
    print(f"✅ Total corrigé: {total_corrected}")
    print(f"📊 Pourcentage: {total_corrected/total_resources*100:.1f}%")
    
    if not args.dry_run and total_corrected > 0:
        print("\n" + "=" * 80)
        print("📝 PROCHAINES ÉTAPES")
        print("=" * 80 + "\n")
        
        print("""
1. Tester l'URL:
   
   python3 test-url.py
   
   → L'URL doit maintenant être:
   .../Theorie/Arpeges_v4.0/... (PAS Theorie_v4.0)
   
   → Copier et tester dans le navigateur
   → L'image DOIT s'afficher ✅

2. Si OK, commit:
   
   git add assets_ocr_index.json megasearch.json mega-search-index.json
   git commit -m "Fix: Enlevé _v4.0 des dossiers parents"
   git push origin main

3. Attendre 2-3 minutes, puis tester:
   
   https://11drumboy11.github.io/Prof-de-basse-V2/Prof-de-basse-V2/

4. Chercher "Arpeges" → Cliquer "Ouvrir" → Image s'affiche ✅
        """)

if __name__ == '__main__':
    main()
