#!/usr/bin/env python3
"""
Correction FINALE des chemins - Prof de Basse V2
Structure réelle confirmée:
- Base de connaissances/Theorie/Arpeges_v4.0/ (PAS Theorie_v4.0/Arpeges_v4.0/)
- Tous les _v4.0 sont au niveau des sous-dossiers uniquement
"""

import json
import re
from pathlib import Path
from datetime import datetime

def print_header(title):
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80 + "\n")

def apply_final_corrections(path):
    """
    Applique les corrections finales basées sur la structure RÉELLE
    
    Structure confirmée:
    Base de connaissances/Theorie/Arpeges_v4.0/assets/pages/page_056.png
                          ↑       ↑
                       Pas de _v4.0  Avec _v4.0
    
    Les dossiers avec _v4.0 sont:
    - Theorie/Arpeges_v4.0, Theorie/Harmonie_v4.0, etc.
    - Methodes/70s Funk & Disco Bass_v4.0, etc.
    - Partitions/Realbook Bass F_v4.0, etc.
    """
    
    corrections = []
    original_path = path
    
    # Liste COMPLÈTE des dossiers avec _v4.0 (noms exacts)
    folders_with_version = [
        # Partitions
        'realbook Volume-3-C_v4.0',
        'The_Real_Rock_Book_v4.0',
        'Sade-DiamondLife-BassTranscriptions_v4.0',
        'Realbook Bass F_v4.0',
        'Stevie-Wonder-Songs-in-the-Key-of-Life_v4.0',
        'Aebersold - The Jazz Fake Book_v4.0',
        'Volume-2-contrebasse_v4.0',
        
        # Methodes
        'Jon Liebman - Funk Fusion Bass_v4.0',
        'Paul westwood 1-2_v4.0',
        '70s Funk & Disco Bass_v4.0',
        'aebersold-FRENCH_v4.0',
        'Paul westwood 2-5_v4.0',
        
        # Theorie
        'Pratique_v4.0',
        'Theorie_v4.0',
        'Harmonie_v4.0',
        'Arpeges_v4.0',
    ]
    
    # Pour chaque dossier avec version, corriger UNIQUEMENT si absent
    for folder_with_v in folders_with_version:
        # Extraire le nom sans version
        folder_base = folder_with_v.replace('_v4.0', '')
        
        # Pattern: chercher /folder_base/ qui n'est PAS déjà /folder_base_v4.0/
        # On doit vérifier qu'il est suivi de / ou de la fin
        pattern = f'/{re.escape(folder_base)}/'
        
        if pattern in path:
            # Vérifier que ce n'est pas déjà avec _v4.0
            if f'/{folder_with_v}/' not in path:
                # Remplacer
                path = path.replace(pattern, f'/{folder_with_v}/')
                corrections.append(f'{folder_base} → {folder_with_v}')
    
    # Correction universelle: /assets/ → /assets/pages/
    if '/assets/' in path and '/assets/pages/' not in path:
        path = path.replace('/assets/', '/assets/pages/')
        corrections.append('assets → assets/pages')
    
    return path, corrections

def fix_json_file(input_file, dry_run=False):
    """Corrige les chemins ET les URLs dans un fichier JSON"""
    
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
        backup_file = f"{input_file}.backup-final-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
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
        new_path, corrections = apply_final_corrections(path)
        
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
                
                # Reconstruire l'URL complète avec le bon chemin
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
        description='Correction FINALE - Structure réelle confirmée'
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
    print("  🔧 CORRECTION FINALE - Prof de Basse V2")
    print("=" * 80)
    print("\n📝 Structure confirmée:")
    print("   Base de connaissances/Theorie/Arpeges_v4.0/assets/pages/")
    print("                         ↑       ↑")
    print("                      Pas _v4.0  Avec _v4.0\n")
    
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
1. Tester une URL:
   
   python3 test-url.py
   
   → Copier l'URL et la tester dans le navigateur
   → Elle DOIT afficher l'image ✅

2. Si OK, commit:
   
   git add assets_ocr_index.json megasearch.json mega-search-index.json
   git commit -m "Fix: Chemins et URLs corrigés (structure finale)"
   git push origin main

3. Attendre 2-3 minutes, puis tester:
   
   https://11drumboy11.github.io/Prof-de-basse-V2/Prof-de-basse-V2/

4. Chercher "Arpeges" → Cliquer "Ouvrir" → Image s'affiche ✅
        """)

if __name__ == '__main__':
    main()
