#!/usr/bin/env python3
"""
Corrige le bug d'URLs dans index.html
Le problème: index.html ajoute 'Base de connaissances/' en double
"""

def fix_index_html(filename='index.html'):
    print("=" * 80)
    print("🔧 CORRECTION DU BUG D'URLs - index.html")
    print("=" * 80 + "\n")
    
    # Lire le fichier
    with open(filename, 'r', encoding='utf-8') as f:
        content = f.read()
    
    print(f"📄 Fichier: {filename}")
    print(f"📊 Taille: {len(content):,} caractères\n")
    
    # Backup
    backup_file = f"{filename}.backup-url-fix"
    with open(backup_file, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"✅ Backup créé: {backup_file}\n")
    
    # Chercher la ligne problématique
    old_line = "const url = path ? BASE_URL + 'Base de connaissances/Base de connaissances/' + path : '';"
    
    if old_line in content:
        print("❌ BUG TROUVÉ:")
        print(f"   {old_line}\n")
        
        # SOLUTION 1: Utiliser directement l'URL du megasearch.json
        new_line = "const url = resource.url || '';"
        
        print("✅ CORRECTION:")
        print(f"   {new_line}\n")
        
        # Remplacer
        content_fixed = content.replace(old_line, new_line)
        
        # Sauvegarder
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(content_fixed)
        
        print(f"💾 Fichier corrigé et sauvegardé: {filename}\n")
        
        print("=" * 80)
        print("✅ CORRECTION TERMINÉE")
        print("=" * 80 + "\n")
        
        print("📝 EXPLICATION:")
        print("   Avant: index.html CONSTRUISAIT l'URL en ajoutant des chemins")
        print("   Après: index.html UTILISE directement l'URL du JSON\n")
        
        print("🎯 POURQUOI C'EST MIEUX:")
        print("   ✅ Plus de bug de chemins en double")
        print("   ✅ URLs garanties correctes (viennent du JSON)")
        print("   ✅ Plus simple et fiable\n")
        
        print("📋 PROCHAINES ÉTAPES:")
        print("   1. Commit:")
        print("      git add index.html")
        print("      git commit -m 'Fix: URLs correctes (utiliser resource.url direct)'")
        print("      git push origin main\n")
        print("   2. Attendre 2-3 minutes\n")
        print("   3. Tester:")
        print("      https://11drumboy11.github.io/Prof-de-basse-V2/\n")
        
        return True
    else:
        print("⚠️  Ligne problématique non trouvée")
        print("   Le bug a peut-être déjà été corrigé")
        return False

if __name__ == '__main__':
    fix_index_html()
