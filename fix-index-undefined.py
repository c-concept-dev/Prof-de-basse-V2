#!/usr/bin/env python3
"""
Corrige le JavaScript dans index.html pour gérer les URLs undefined
"""

def fix_index_html():
    print("🔧 Correction du JavaScript dans index.html\n")
    
    with open('index.html', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Correction 1: Dans createResourceCard
    old_code_1 = '''<button class="action-btn primary" onclick="event.stopPropagation(); openResourceDirect('${resource.url || resource.page_url}')">'''
    new_code_1 = '''<button class="action-btn primary" onclick="event.stopPropagation(); openResourceDirect('${resource.url || resource.page_url || resource.file_path || ""}')">'''
    
    # Correction 2: Dans la fonction copyUrl
    old_code_2 = '''<button class="action-btn" onclick="event.stopPropagation(); copyUrl('${resource.url || resource.page_url}')">'''
    new_code_2 = '''<button class="action-btn" onclick="event.stopPropagation(); copyUrl('${resource.url || resource.page_url || resource.file_path || ""}')">'''
    
    # Correction 3: Ajouter une validation dans openResourceDirect
    old_func = '''function openResourceDirect(url) {
            if (url) {
                window.open(url, '_blank');
            }
        }'''
    
    new_func = '''function openResourceDirect(url) {
            if (url && url !== 'undefined' && url.trim() !== '') {
                window.open(url, '_blank');
            } else {
                alert('⚠️ URL non disponible pour cette ressource');
            }
        }'''
    
    # Correction 4: Ajouter une validation dans copyUrl
    old_copy = '''function copyUrl(url) {
            if (url) {
                navigator.clipboard.writeText(url).then(() => {
                    alert('✅ URL copiée !');
                });
            }
        }'''
    
    new_copy = '''function copyUrl(url) {
            if (url && url !== 'undefined' && url.trim() !== '') {
                navigator.clipboard.writeText(url).then(() => {
                    alert('✅ URL copiée !');
                });
            } else {
                alert('⚠️ URL non disponible pour cette ressource');
            }
        }'''
    
    # Correction 5: Dans openResource
    old_resource = '''function openResource(resource) {
            const modal = document.getElementById('resourceModal');
            const modalBody = document.getElementById('modalBody');
            
            const url = resource.url || resource.page_url;'''
    
    new_resource = '''function openResource(resource) {
            const modal = document.getElementById('resourceModal');
            const modalBody = document.getElementById('modalBody');
            
            const url = resource.url || resource.page_url || resource.file_path || '';
            
            if (!url || url === 'undefined' || url.trim() === '') {
                alert('⚠️ URL non disponible pour cette ressource');
                return;
            }'''
    
    changes = []
    
    if old_code_1 in content:
        content = content.replace(old_code_1, new_code_1)
        changes.append("✅ Bouton 'Ouvrir'")
    
    if old_code_2 in content:
        content = content.replace(old_code_2, new_code_2)
        changes.append("✅ Bouton 'Copier'")
    
    if old_func in content:
        content = content.replace(old_func, new_func)
        changes.append("✅ Fonction openResourceDirect()")
    
    if old_copy in content:
        content = content.replace(old_copy, new_copy)
        changes.append("✅ Fonction copyUrl()")
    
    if old_resource in content:
        content = content.replace(old_resource, new_resource)
        changes.append("✅ Fonction openResource()")
    
    if changes:
        with open('index.html', 'w', encoding='utf-8') as f:
            f.write(content)
        
        print("Corrections appliquées :")
        for change in changes:
            print(f"  {change}")
        
        print("\n💾 Fichier index.html mis à jour")
        return True
    else:
        print("ℹ️  Aucune correction nécessaire (déjà à jour)")
        return False

if __name__ == '__main__':
    print("="*60)
    print("🔧 CORRECTION INDEX.HTML - URLs undefined")
    print("="*60 + "\n")
    
    if fix_index_html():
        print("\n" + "="*60)
        print("✅ CORRECTION TERMINÉE")
        print("="*60)
        print("\n🔧 Commandes Git :")
        print("   git add index.html")
        print('   git commit -m "Fix: Gestion URLs undefined dans index.html"')
        print("   git push origin main")
        print("\n📝 Puis teste le site :")
        print("   https://11drumboy11.github.io/Prof-de-basse-V2/")
        print()
