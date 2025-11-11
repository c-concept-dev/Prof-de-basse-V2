#!/usr/bin/env python3
"""
Correction UNIVERSELLE des chemins pour Prof de Basse V2
Corrige TOUS les dossiers pour ajouter _v4.0 et /pages/
"""

import json
import re
from pathlib import Path
from datetime import datetime

def print_header(title):
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80 + "\n")

def apply_universal_path_corrections(path):
    """
    Applique les corrections universelles basées sur la structure réelle
    
    Structure réelle découverte:
    - TOUS les dossiers ont _v4.0
    - TOUS les assets sont dans /assets/pages/
    
    Exemples de corrections:
    - Theorie/Arpeges/assets/ → Theorie/Arpeges_v4.0/assets/pages/
    - Methodes/Funk/assets/ → Methodes/70s Funk & Disco Bass_v4.0/assets/pages/
    """
    
    corrections = []
    original_path = path
    
    # Mapping des noms de dossiers (nom court → nom complet avec version)
    folder_mappings = {
        # Partitions
        'realbook Volume-3-C': 'realbook Volume-3-C_v4.0',
        'The_Real_Rock_Book': 'The_Real_Rock_Book_v4.0',
        'Sade-DiamondLife-BassTranscriptions': 'Sade-DiamondLife-BassTranscriptions_v4.0',
        'Realbook Bass F': 'Realbook Bass F_v4.0',
        'Stevie-Wonder-Songs-in-the-Key-of-Life': 'Stevie-Wonder-Songs-in-the-Key-of-Life_v4.0',
        'Aebersold - The Jazz Fake Book': 'Aebersold - The Jazz Fake Book_v4.0',
        'Volume-2-contrebasse': 'Volume-2-contrebasse_v4.0',
        
        # Methodes
        'Jon Liebman - Funk Fusion Bass': 'Jon Liebman - Funk Fusion Bass_v4.0',
        'Paul westwood 1-2': 'Paul westwood 1-2_v4.0',
        '70s Funk & Disco Bass': '70s Funk & Disco Bass_v4.0',
        'aebersold-FRENCH': 'aebersold-FRENCH_v4.0',
        'Paul westwood 2-5': 'Paul westwood 2-5_v4.0',
        
        # Theorie
        'Pratique': 'Pratique_v4.0',
        'Theorie': 'Theorie_v4.0',
        'Harmonie': 'Harmonie_v4.0',
        'Arpeges': 'Arpeges_v4.0',
    }
    
    # Appliquer les corrections de noms de dossiers
    for short_name, full_name in folder_mappings.items():
        # Pattern: chercher le nom court suivi de / (pas déjà _v4.0)
        pattern = f'/{short_name}/'
        if pattern in path and '_v4.0' not in path.split(short_name)[0] + short_name:
            path = path.replace(pattern, f'/{full_name}/')
            corrections.append(f'{short_name} → {full_name}')
    
    # Correction universelle: /assets/ → /assets/pages/
    if '/assets/' in path and '/assets/pages/' not in path:
        path = path.replace('/assets/', '/assets/pages/')
        corrections.append('assets → assets/pages')
    
    return path, corrections

def fix_json_file(input_file, output_file=None, dry_run=False):
    """Corrige les chemins dans un fichier JSON"""
    
    if output_file is None:
        output_file = input_file
    
    print(f"📂 Traitement de {input_file}...")
    
    # Vérifier que le fichier existe
    if not Path(input_file).exists():
        print(f"⚠️  Fichier non trouvé: {input_file}\n")
        return None
    
    # Lire le fichier
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except Exception as e:
        print(f"❌ Erreur lecture: {e}\n")
        return None
    
    # Backup (sauf en dry-run)
    if not dry_run:
        backup_file = f"{input_file}.backup-universal-fix-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
        with open(backup_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print(f"✅ Backup créé: {backup_file}\n")
    
    # Statistiques
    stats = {
        'total': 0,
        'corrected': 0,
        'unchanged': 0,
        'corrections_by_type': {},
        'examples': []
    }
    
    # Traiter les ressources
    if isinstance(data.get('resources'), list):
        resources = data['resources']
    elif isinstance(data.get('resources'), dict):
        resources = list(data['resources'].values())
    else:
        print("❌ Structure 'resources' non reconnue\n")
        return stats
    
    print(f"📊 Total ressources: {len(resources)}\n")
    
    if dry_run:
        print("🔍 MODE DRY-RUN: Simulation des corrections...\n")
    else:
        print("⚡ MODE RÉEL: Application des corrections...\n")
    
    corrected_resources = []
    
    for resource in resources:
        stats['total'] += 1
        
        # Récupérer les chemins
        path = resource.get('path', '')
        url = resource.get('url', '')
        resource_id = resource.get('id', '')
        
        if not path:
            corrected_resources.append(resource)
            stats['unchanged'] += 1
            continue
        
        # Appliquer les corrections
        new_path, corrections = apply_universal_path_corrections(path)
        
        if new_path != path:
            stats['corrected'] += 1
            
            # Compter les types de corrections
            for correction in corrections:
                stats['corrections_by_type'][correction] = \
                    stats['corrections_by_type'].get(correction, 0) + 1
            
            # Garder quelques exemples
            if len(stats['examples']) < 10:
                stats['examples'].append({
                    'original': path,
                    'corrected': new_path,
                    'corrections': corrections
                })
            
            # Afficher les premières corrections
            if stats['corrected'] <= 5:
                print(f"📝 Correction #{stats['corrected']}:")
                print(f"   AVANT: {path}")
                print(f"   APRÈS: {new_path}")
                print(f"   Types: {', '.join(corrections)}")
                print()
            
            # Mettre à jour le resource
            if not dry_run:
                resource['path'] = new_path
                
                # Mettre à jour l'URL
                if url:
                    base_url = 'https://11drumboy11.github.io/Prof-de-basse-V2/'
                    encoded_path = new_path.replace(' ', '%20')
                    new_url = base_url + encoded_path
                    resource['url'] = new_url
                
                # Mettre à jour l'ID
                if resource_id and resource_id == path:
                    resource['id'] = new_path.replace(' ', '%20')
        else:
            stats['unchanged'] += 1
        
        corrected_resources.append(resource)
    
    # Afficher résumé
    if stats['corrected'] > 5:
        print(f"... ({stats['corrected'] - 5} autres corrections)\n")
    
    # Mettre à jour les ressources
    if not dry_run:
        if isinstance(data.get('resources'), list):
            data['resources'] = corrected_resources
        elif isinstance(data.get('resources'), dict):
            data['resources'] = {r.get('id', str(i)): r 
                               for i, r in enumerate(corrected_resources)}
        
        # Sauvegarder
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Fichier corrigé sauvegardé: {output_file}\n")
    else:
        print(f"🔍 DRY-RUN: Aucune modification effectuée\n")
    
    return stats

def display_examples(stats):
    """Affiche des exemples de corrections"""
    if stats.get('examples'):
        print_header("📋 EXEMPLES DE CORRECTIONS")
        
        for i, ex in enumerate(stats['examples'][:5], 1):
            print(f"{i}. {ex['corrections']}")
            print(f"   AVANT: {ex['original']}")
            print(f"   APRÈS: {ex['corrected']}")
            print()

def main():
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Correction universelle des chemins - Prof de Basse V2'
    )
    parser.add_argument(
        '--dry-run', 
        action='store_true', 
        help='Simuler sans modifier les fichiers'
    )
    parser.add_argument(
        '--files',
        nargs='+',
        default=['assets_ocr_index.json', 'megasearch.json', 'mega-search-index.json'],
        help='Fichiers à corriger'
    )
    
    args = parser.parse_args()
    
    print("=" * 80)
    print("  🔧 CORRECTION UNIVERSELLE DES CHEMINS - Prof de Basse V2")
    print("=" * 80)
    
    if args.dry_run:
        print("\n🔍 MODE DRY-RUN: Simulation sans modifications\n")
    else:
        print("\n⚡ MODE RÉEL: Les modifications seront appliquées\n")
        print("⚠️  Cette opération va modifier les fichiers JSON")
        response = input("Continuer ? (oui/non): ")
        if response.lower() not in ['oui', 'yes', 'y', 'o']:
            print("\n❌ Annulé par l'utilisateur")
            return
        print()
    
    # Traiter tous les fichiers
    all_stats = {}
    
    for filename in args.files:
        print_header(f"Traitement de {filename}")
        
        stats = fix_json_file(filename, dry_run=args.dry_run)
        
        if stats:
            all_stats[filename] = stats
            
            print(f"📊 Statistiques {filename}:")
            print(f"   Total ressources: {stats['total']}")
            print(f"   Corrigées: {stats['corrected']} ({stats['corrected']/stats['total']*100:.1f}%)")
            print(f"   Inchangées: {stats['unchanged']}")
            
            if stats['corrections_by_type']:
                print(f"\n   Types de corrections:")
                for corr_type, count in sorted(
                    stats['corrections_by_type'].items(), 
                    key=lambda x: x[1], 
                    reverse=True
                ):
                    print(f"      • {corr_type}: {count}x")
            
            # Afficher exemples
            if stats.get('examples'):
                display_examples(stats)
    
    # Résumé global
    print_header("📊 RÉSUMÉ GLOBAL")
    
    total_corrected = sum(s['corrected'] for s in all_stats.values())
    total_resources = sum(s['total'] for s in all_stats.values())
    
    print(f"📈 Total ressources traitées: {total_resources}")
    print(f"✅ Total corrections appliquées: {total_corrected}")
    print(f"📊 Pourcentage corrigé: {total_corrected/total_resources*100:.1f}%")
    
    if not args.dry_run and total_corrected > 0:
        print("\n" + "=" * 80)
        print("📝 PROCHAINES ÉTAPES")
        print("=" * 80 + "\n")
        
        print("""
1. Vérifier qu'une URL fonctionne:
   
   python3 -c "
   import json
   d = json.load(open('megasearch.json'))
   r = [r for r in d['resources'] if 'Arpeges' in r['path']][0]
   print('\\nURL à tester:')
   print(r['url'])
   "
   
   → Copier cette URL et la tester dans le navigateur

2. Si l'URL fonctionne, commit:
   
   git add assets_ocr_index.json megasearch.json mega-search-index.json
   git commit -m "Fix: Chemins universels corrigés (_v4.0 + /pages/)"
   git push origin main

3. Attendre 2-3 minutes, puis tester le site:
   
   https://11drumboy11.github.io/Prof-de-basse-V2/

4. Chercher "Arpeges" et cliquer "Ouvrir"
   → L'image devrait s'afficher ✅
        """)
    
    elif args.dry_run:
        print("\n💡 POUR APPLIQUER LES CORRECTIONS:")
        print("   python3 fix-json-paths-universal.py")
        print("   (sans --dry-run)")

if __name__ == '__main__':
    main()
