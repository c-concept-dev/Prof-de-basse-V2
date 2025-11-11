#!/usr/bin/env python3
"""
Nettoie les marqueurs de conflit Git dans mega-search-index.json
"""
import re

def clean_git_conflicts():
    print("="*70)
    print("🧹 NETTOYAGE DES MARQUEURS DE CONFLIT GIT")
    print("="*70 + "\n")
    
    # Lire le fichier
    with open('mega-search-index.json', 'r', encoding='utf-8') as f:
        content = f.read()
    
    print(f"📏 Taille fichier: {len(content):,} caractères\n")
    
    # Chercher les marqueurs de conflit
    conflict_markers = [
        r'<<<<<<< HEAD\n',
        r'=======\n',
        r'>>>>>>> .*\n'
    ]
    
    conflicts_found = 0
    for marker in conflict_markers:
        count = len(re.findall(marker, content))
        conflicts_found += count
    
    if conflicts_found == 0:
        print("✅ Aucun marqueur de conflit trouvé")
        return
    
    print(f"⚠️  {conflicts_found} marqueurs de conflit trouvés\n")
    
    # Afficher le contexte d'un conflit
    match = re.search(r'<<<<<<< HEAD.*?>>>>>>> [^\n]*', content, re.DOTALL)
    if match:
        print("📝 Exemple de conflit:")
        print("-" * 70)
        print(match.group(0)[:500])
        print("-" * 70 + "\n")
    
    # Stratégie: garder la version HEAD et supprimer les marqueurs
    print("🔧 Nettoyage en cours...\n")
    
    # Supprimer les sections de conflit
    # Pattern: <<<<<<< HEAD ... ======= ... >>>>>>> branch
    # On garde ce qui est entre <<<<<<< HEAD et =======
    
    pattern = r'<<<<<<< HEAD\n(.*?)\n=======\n.*?\n>>>>>>> [^\n]*\n'
    
    def replace_conflict(match):
        # Garder seulement la partie HEAD
        return match.group(1) + '\n'
    
    cleaned_content = re.sub(pattern, replace_conflict, content, flags=re.DOTALL)
    
    # Supprimer les marqueurs restants isolés
    cleaned_content = re.sub(r'<<<<<<< HEAD\n', '', cleaned_content)
    cleaned_content = re.sub(r'=======\n', '', cleaned_content)
    cleaned_content = re.sub(r'>>>>>>> [^\n]*\n', '', cleaned_content)
    
    # Vérifier que c'est du JSON valide maintenant
    import json
    try:
        data = json.loads(cleaned_content)
        print(f"✅ JSON valide après nettoyage!")
        print(f"   • Ressources: {len(data.get('resources', []))}\n")
        
        # Sauvegarder
        with open('mega-search-index.json', 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        print("💾 Fichier nettoyé et sauvegardé!\n")
        
        print("="*70)
        print("✅ NETTOYAGE TERMINÉ")
        print("="*70)
        
    except json.JSONDecodeError as e:
        print(f"❌ JSON toujours invalide après nettoyage:")
        print(f"   Erreur: {e}")
        print(f"   Position: ligne {e.lineno}, colonne {e.colno}")
        
        # Sauvegarder quand même le contenu nettoyé
        with open('mega-search-index.json', 'w', encoding='utf-8') as f:
            f.write(cleaned_content)
        
        print("\n⚠️  Fichier sauvegardé mais nécessite correction manuelle")

if __name__ == '__main__':
    clean_git_conflicts()
