#!/usr/bin/env python3
"""
Auto-Index Generator pour Prof de Basse - VERSION PRODUCTION
Scanne automatiquement le repository GitHub et génère les index.html
"""

import os
import re
from pathlib import Path
from collections import defaultdict

# Template HTML (identique à la version de test)
HTML_TEMPLATE = '''<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title} - Prof de Basse</title>
    <meta name="description" content="{description}">
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 20px;
            line-height: 1.6;
        }}
        .container {{
            background: white;
            max-width: 1400px;
            margin: 0 auto;
            border-radius: 20px;
            box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
            overflow: hidden;
        }}
        header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 40px;
            text-align: center;
        }}
        header h1 {{
            font-size: 42px;
            margin-bottom: 10px;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        }}
        .header-info {{ font-size: 18px; margin-top: 15px; opacity: 0.95; }}
        nav {{
            background: #f8f9fa;
            padding: 20px 40px;
            border-bottom: 3px solid #667eea;
            display: flex;
            justify-content: center;
            flex-wrap: wrap;
            gap: 10px;
        }}
        nav a {{
            text-decoration: none;
            color: #667eea;
            font-weight: 600;
            padding: 10px 20px;
            border-radius: 8px;
            background: white;
            border: 2px solid #667eea;
            transition: all 0.3s;
        }}
        nav a:hover {{ background: #667eea; color: white; transform: translateY(-2px); }}
        .content {{ padding: 40px; }}
        .search-box {{
            background: #f8f9fa;
            padding: 20px;
            border-radius: 10px;
            margin-bottom: 30px;
        }}
        .search-box input {{
            width: 100%;
            padding: 15px;
            border: 2px solid #667eea;
            border-radius: 8px;
            font-size: 16px;
        }}
        .stats {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
            gap: 20px;
            margin: 30px 0;
        }}
        .stat-card {{
            background: #f8f9fa;
            padding: 25px;
            border-radius: 10px;
            text-align: center;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        }}
        .stat-number {{ font-size: 42px; font-weight: 700; color: #667eea; margin-bottom: 10px; }}
        .stat-label {{ font-size: 16px; color: #666; }}
        .track-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
            gap: 25px;
            margin: 30px 0;
        }}
        .track-card {{
            background: #f8f9fa;
            border-radius: 12px;
            padding: 20px;
            box-shadow: 0 4px 10px rgba(0,0,0,0.1);
            transition: all 0.3s;
        }}
        .track-card:hover {{ transform: translateY(-5px); box-shadow: 0 8px 20px rgba(0,0,0,0.15); }}
        .track-card h3 {{ color: #667eea; margin-bottom: 15px; font-size: 20px; }}
        .track-card img {{
            width: 100%;
            border-radius: 8px;
            margin-bottom: 15px;
            cursor: zoom-in;
        }}
        .track-card audio {{ width: 100%; margin-top: 15px; }}
        .track-info {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-top: 10px;
            padding: 10px;
            background: white;
            border-radius: 6px;
            font-size: 14px;
            color: #666;
        }}
        .lightbox {{
            display: none;
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0, 0, 0, 0.95);
            z-index: 1000;
            justify-content: center;
            align-items: center;
            cursor: pointer;
        }}
        .lightbox img {{ max-width: 95%; max-height: 95%; border-radius: 10px; }}
        .lightbox.active {{ display: flex; }}
        .controls {{
            position: fixed;
            bottom: 30px;
            right: 30px;
            display: flex;
            gap: 10px;
            z-index: 999;
        }}
        .control-btn {{
            background: #667eea;
            color: white;
            border: none;
            padding: 15px 20px;
            border-radius: 10px;
            cursor: pointer;
            font-size: 16px;
            box-shadow: 0 4px 10px rgba(0,0,0,0.2);
            transition: all 0.3s;
        }}
        .control-btn:hover {{ background: #764ba2; transform: translateY(-2px); }}
        footer {{ background: #333; color: white; text-align: center; padding: 30px; margin-top: 40px; }}
        .no-content {{ text-align: center; padding: 30px 20px; color: #999; }}
        @media (max-width: 768px) {{
            header h1 {{ font-size: 32px; }}
            .track-grid {{ grid-template-columns: 1fr; }}
            nav {{ flex-direction: column; }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>🎸 {title}</h1>
            <div class="header-info"><p>{description}</p></div>
        </header>
        <nav>
            <a href="https://11drumboy11.github.io/Prof-de-basse-V2/">🏠 Accueil</a>
            <a href="#stats">📊 Stats</a>
            <a href="#exercises">🎵 Exercices</a>
            <a href="https://github.com/11drumboy11/Prof-de-basse">📚 GitHub</a>
        </nav>
        <div class="content">
            <div id="stats" class="stats">
                <div class="stat-card">
                    <div class="stat-number">{track_count}</div>
                    <div class="stat-label">Exercices</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">{mp3_count}</div>
                    <div class="stat-label">MP3</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">{image_count}</div>
                    <div class="stat-label">Partitions</div>
                </div>
            </div>
            <div class="search-box">
                <input type="text" id="searchInput" placeholder="🔍 Rechercher..." onkeyup="filterTracks()">
            </div>
            <div id="exercises" class="track-grid">
{tracks_html}
            </div>
        </div>
    </div>
    <div class="lightbox" id="lightbox" onclick="closeLightbox()">
        <img src="" id="lightboxImg" alt="Partition">
    </div>
    <div class="controls">
        <button class="control-btn" onclick="scrollToTop()">⬆️</button>
    </div>
    <footer>
        <p><strong>Prof de Basse - {title}</strong></p>
        <p style="margin-top: 10px;">Auto-généré • © 2025</p>
    </footer>
    <script>
        function openLightbox(src) {{
            document.getElementById('lightboxImg').src = src;
            document.getElementById('lightbox').classList.add('active');
        }}
        function closeLightbox() {{
            document.getElementById('lightbox').classList.remove('active');
        }}
        function scrollToTop() {{
            window.scrollTo({{ top: 0, behavior: 'smooth' }});
        }}
        function filterTracks() {{
            const input = document.getElementById('searchInput');
            const filter = input.value.toLowerCase();
            const cards = document.querySelectorAll('.track-card');
            cards.forEach(card => {{
                card.style.display = card.textContent.toLowerCase().includes(filter) ? '' : 'none';
            }});
        }}
        document.addEventListener('keydown', (e) => {{
            if (e.key === 'Escape') closeLightbox();
        }});
    </script>
</body>
</html>'''

def find_all_files(base_path, extensions):
    """Trouve tous les fichiers avec les extensions données"""
    files = []
    for ext in extensions:
        files.extend(Path(base_path).rglob(f'*.{ext}'))
        files.extend(Path(base_path).rglob(f'*.{ext.upper()}'))
    return files

def organize_files_by_folder(files, base_path):
    """Organise les fichiers par dossier parent"""
    structure = defaultdict(lambda: {'mp3': [], 'images': []})
    
    for file in files:
        folder = file.parent
        rel_folder = folder.relative_to(base_path)
        
        if file.suffix.lower() in ['.mp3']:
            structure[rel_folder]['mp3'].append(file)
        elif file.suffix.lower() in ['.png', '.jpg', '.jpeg']:
            structure[rel_folder]['images'].append(file)
    
    return structure

def match_files(mp3_list, img_list):
    """Associe intelligemment les MP3 et images par numéro"""
    mp3_dict = {}
    for mp3 in mp3_list:
        numbers = re.findall(r'\d+', mp3.stem)
        if numbers:
            mp3_dict[int(numbers[0])] = mp3
    
    img_dict = {}
    for img in img_list:
        numbers = re.findall(r'\d+', img.stem)
        if numbers:
            img_dict[int(numbers[0])] = img
    
    all_keys = sorted(set(mp3_dict.keys()) | set(img_dict.keys()))
    
    return [{'number': k, 'mp3': mp3_dict.get(k), 'image': img_dict.get(k)} for k in all_keys]

def generate_track_html(match, folder_path):
    """Génère le HTML d'une carte de track"""
    num = match['number']
    mp3 = match.get('mp3')
    img = match.get('image')
    
    html = f'                <div class="track-card">\n'
    html += f'                    <h3>Track {num:02d}</h3>\n'
    
    if img:
        img_rel = img.relative_to(folder_path)
        html += f'                    <img src="{img_rel}" alt="Track {num}" onclick="openLightbox(\'{img_rel}\')">\n'
    else:
        html += '                    <div class="no-content">📄 Pas de partition</div>\n'
    
    if mp3:
        mp3_rel = mp3.relative_to(folder_path)
        html += f'                    <audio controls preload="none">\n'
        html += f'                        <source src="{mp3_rel}" type="audio/mpeg">\n'
        html += '                    </audio>\n'
    else:
        html += '                    <div class="no-content">🎵 Pas de MP3</div>\n'
    
    html += '                    <div class="track-info">\n'
    html += f'                        <span>#{num:02d}</span>\n'
    if mp3:
        html += f'                        <span>{mp3.name}</span>\n'
    html += '                    </div>\n'
    html += '                </div>\n'
    
    return html

def generate_index(folder_path, mp3_files, img_files):
    """Génère un index.html pour un dossier"""
    matches = match_files(mp3_files, img_files)
    
    if not matches:
        return None
    
    tracks_html = '\n'.join([generate_track_html(m, folder_path) for m in matches])
    
    title = folder_path.name.replace('_', ' ').replace('%20', ' ')
    
    html = HTML_TEMPLATE.format(
        title=title,
        description=f"Méthode complète - {len(matches)} exercices",
        track_count=len(matches),
        mp3_count=len([m for m in matches if m.get('mp3')]),
        image_count=len([m for m in matches if m.get('image')]),
        tracks_html=tracks_html or '<div class="no-content"><h3>Aucun exercice</h3></div>'
    )
    
    return html

def main():
    """Fonction principale"""
    print("🎸 Auto-Index Generator - Prof de Basse (Production)")
    print("=" * 60)
    
    # Chemin du repository
    base_path = Path.cwd()
    print(f"📂 Repository : {base_path}")
    
    # Trouver tous les fichiers
    mp3_files = find_all_files(base_path, ['mp3'])
    img_files = find_all_files(base_path, ['png', 'jpg', 'jpeg'])
    
    print(f"✅ {len(mp3_files)} MP3 trouvés")
    print(f"✅ {len(img_files)} images trouvées")
    
    # Organiser par dossier
    all_files = mp3_files + img_files
    structure = organize_files_by_folder(all_files, base_path)
    
    # Générer les index pour les dossiers Methodes
    generated_count = 0
    
    for folder, files in structure.items():
        # Ne générer que pour les sous-dossiers de Methodes
        if 'Methodes' not in str(folder):
            continue
        
        # Ne pas générer pour les sous-sous-dossiers (MP3, partitions, etc.)
        if str(folder).count('/') > 1:
            continue
        
        folder_path = base_path / folder
        
        print(f"\n📁 {folder}")
        
        html = generate_index(folder_path, files['mp3'], files['images'])
        
        if html:
            index_file = folder_path / 'index.html'
            index_file.write_text(html, encoding='utf-8')
            print(f"   ✅ Généré : index.html")
            generated_count += 1
        else:
            print(f"   ⚠️  Pas de contenu")
    
    print("\n" + "=" * 60)
    print(f"✅ {generated_count} fichiers index.html générés !")

if __name__ == "__main__":
    main()
