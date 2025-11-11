#!/usr/bin/env python3
"""
Répare le mega-search-index.json corrompu
Le problème : une URL tronquée à la ligne 3036
"""
import json
import re

def repair_json():
    print("="*70)
    print("🔧 RÉPARATION DU MEGA-SEARCH-INDEX.JSON")
    print("="*70 + "\n")
    
    # Lire le fichier
    with open('mega-search-index.json', 'r', encoding='utf-8') as f:
        content = f.read()
    
    print(f"📏 Taille fichier: {len(content):,} caractères")
    print(f"📄 Lignes: {content.count(chr(10)):,}\n")
    
    # Le problème spécifique détecté
    problem_pattern = r'"url":\s*"https://1\{'
    
    if re.search(problem_pattern, content):
        print("⚠️  Problème détecté: URL tronquée 'https://1{'\n")
        
        # Trouver la ressource complète qui a le problème
        # Elle devrait avoir un ID commençant par "Base%20de%20connaissances/Base%20de%20connaissances/Theorie/Arpeges/assets/page_003.png"
        
        # Pattern pour reconstruire l'URL correcte
        correct_url = "https://11drumboy11.github.io/Prof-de-basse-V2/Base%20de%20connaissances/Theorie/Arpeges_v4.0/assets/page_003.png"
        
        # Remplacer l'URL cassée
        content = re.sub(
            r'"url":\s*"https://1\{',
            f'"url": "{correct_url}"',
            content
        )
        
        print(f"✅ URL réparée:\n   {correct_url}\n")
    
    # Vérifier maintenant si le JSON est valide
    try:
        data = json.loads(content)
        print("✅ JSON valide après réparation!\n")
        
        resources = data.get('resources', [])
        print(f"📊 Statistiques:")
        print(f"   • Total ressources: {len(resources)}")
        print(f"   • Version: {data.get('version', 'N/A')}")
        
        # Vérifier que toutes les ressources ont une URL
        with_url = sum(1 for r in resources if r.get('url') or r.get('page_url') or r.get('file_path'))
        print(f"   • Ressources avec URL: {with_url}/{len(resources)}\n")
        
        # Sauvegarder le fichier réparé
        with open('mega-search-index.json', 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        print("💾 Fichier réparé et sauvegardé!\n")
        
        print("="*70)
        print("✅ RÉPARATION TERMINÉE")
        print("="*70)
        
        return True
        
    except json.JSONDecodeError as e:
        print(f"❌ JSON toujours invalide: {e}")
        print(f"   Position: ligne {e.lineno}, colonne {e.colno}\n")
        
        # Montrer le contexte de l'erreur
        lines = content.split('\n')
        if e.lineno <= len(lines):
            print("Contexte de l'erreur:")
            start = max(0, e.lineno - 3)
            end = min(len(lines), e.lineno + 2)
            for i in range(start, end):
                marker = ">>> " if i == e.lineno - 1 else "    "
                print(f"{marker}{i+1:5d}: {lines[i][:100]}")
        
        return False

if __name__ == '__main__':
    repair_json()
