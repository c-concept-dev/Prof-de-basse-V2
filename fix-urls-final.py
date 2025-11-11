#!/usr/bin/env python3
"""
Correction FINALE des URLs - Prof de Basse V2
Ajoute le sous-dossier /Prof-de-basse-V2/ manquant dans les URLs
"""

import json
from pathlib import Path
from datetime import datetime

def print_header(title):
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80 + "\n")

def fix_url_structure(url):
    """
    Corrige l'URL pour ajouter le sous-dossier manquant
    
    AVANT:
    https://11drumboy11.github.io/Prof-de-basse-V2/Base de connaissances/...
    
    APRÈS:
    https://11drumboy11.github.io/Prof-de-basse-V2/Prof-de-basse-V2/Base de connaissances/...
                                                     ↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑
    """
    
    if not url:
        return url, False
    
    # Pattern à remplacer
    old_base = 'https://11drumboy11.github.io/Prof-de-basse-V2/'
    new_base = 'https://11drumboy11.github.io/Prof-de-basse-V2/Prof-de-basse-V2/'
    
    # Si l'URL a déjà le sous-dossier, ne rien faire
    if new_base in url:
        return url, False
    
    # Remplacer
    if old_base in url:
        new_url = url.replace(old_base, new_base, 1)
        return new_url, True
    
    return url, False

def fix_json_file(input_file, dry_run=False):
    """Corrige les URLs dans un fichier JSON"""
    
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
        backup_file = f"{input_file}.backup-url-fix-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
        with open(backup_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print(f"✅ Backup créé: {backup_file}\n")
    
    # Statistiques
    stats = {
        'total': 0,
        'corrected': 0,
        'unchanged': 0,
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
        
        # Récupérer l'URL
        url = resource.get('url', '')
        
        if not url:
            corrected_resources.append(resource)
            stats['unchanged'] += 1
            continue
        
        # Corriger l'URL
        new_url, was_corrected = fix_url_structure(url)
        
        if was_corrected:
            stats['corrected'] += 1
            
            # Garder quelques exemples
            if len(stats['examples']) < 5:
                stats['examples'].append({
                    'original': url,
                    'corrected': new_url
                })
            
            # Afficher les premières corrections
            if stats['corrected'] <= 3:
                print(f"📝 Correction #{stats['corrected']}:")
                print(f"   AVANT: {url}")
                print(f"   APRÈS: {new_url}")
                print()
            
            # Mettre à jour le resource
            if not dry_run:
                resource['url'] = new_url
        else:
            stats['unchanged'] += 1
        
        corrected_resources.append(resource)
    
    # Afficher résumé
    if stats['corrected'] > 3:
        print(f"... ({stats['corrected'] - 3} autres corrections)\n")
    
    # Mettre à jour les ressources
    if not dry_run:
        if isinstance(data.get('resources'), list):
            data['resources'] = corrected_resources
        elif isinstance(data.get('resources'), dict):
            data['resources'] = {r.get('id', str(i)): r 
                               for i, r in enumerate(corrected_resources)}
        
        # Sauvegarder
        with open(input_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Fichier corrigé sauvegardé: {input_file}\n")
    else:
        print(f"🔍 DRY-RUN: Aucune modification effectuée\n")
    
    return stats

def display_examples(stats):
    """Affiche des exemples de corrections"""
    if stats.get('examples'):
        print_header("📋 EXEMPLES DE CORRECTIONS")
        
        for i, ex in enumerate(stats['examples'], 1):
            print(f"{i}.")
            print(f"   AVANT: {ex['original']}")
            print(f"   APRÈS: {ex['corrected']}")
            print()

def main():
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Correction finale des URLs - Ajout sous-dossier Prof-de-basse-V2'
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
    print("  🔧 CORRECTION FINALE DES URLs - Prof de Basse V2")
    print("=" * 80)
    
    print("\n📝 Ce script ajoute le sous-dossier manquant dans les URLs:")
    print("   /Prof-de-basse-V2/Prof-de-basse-V2/Base de connaissances/...")
    print("                      ↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑")
    print("                   Sous-dossier ajouté\n")
    
    if args.dry_run:
        print("🔍 MODE DRY-RUN: Simulation sans modifications\n")
    else:
        print("⚡ MODE RÉEL: Les modifications seront appliquées\n")
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
            print(f"   URLs corrigées: {stats['corrected']} ({stats['corrected']/stats['total']*100:.1f}%)")
            print(f"   Inchangées: {stats['unchanged']}")
            
            # Afficher exemples
            if stats.get('examples'):
                display_examples(stats)
    
    # Résumé global
    print_header("📊 RÉSUMÉ GLOBAL")
    
    total_corrected = sum(s['corrected'] for s in all_stats.values())
    total_resources = sum(s['total'] for s in all_stats.values())
    
    print(f"📈 Total ressources traitées: {total_resources}")
    print(f"✅ Total URLs corrigées: {total_corrected}")
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
   print('\\nURL à tester:')
   print(d['resources'][0]['url'])
   "
   
   → Copier cette URL et la tester dans le navigateur
   → L'image DOIT s'afficher ✅

2. Si l'URL fonctionne, commit:
   
   git add assets_ocr_index.json megasearch.json mega-search-index.json
   git commit -m "Fix: URLs corrigées (sous-dossier Prof-de-basse-V2)"
   git push origin main

3. Attendre 2-3 minutes, puis tester le site:
   
   https://11drumboy11.github.io/Prof-de-basse-V2/Prof-de-basse-V2/
   
   ⚠️  NOTE: L'URL du site a aussi changé !
   Nouveau lien: /Prof-de-basse-V2/Prof-de-basse-V2/

4. Chercher "Arpeges" et cliquer "Ouvrir"
   → L'image devrait s'afficher ✅

5. Mettre à jour index.html si nécessaire:
   
   Le fichier index.html doit aussi être accessible à:
   https://11drumboy11.github.io/Prof-de-basse-V2/Prof-de-basse-V2/index.html
        """)
    
    elif args.dry_run:
        print("\n💡 POUR APPLIQUER LES CORRECTIONS:")
        print("   python3 fix-urls-final.py")
        print("   (sans --dry-run)")

if __name__ == '__main__':
    main()
