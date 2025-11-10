#!/usr/bin/env python3
"""
Générateur d'index MEGA pour Prof de Basse
Scanne la Base de connaissances et crée un index JSON complet
"""

import json
import os
from pathlib import Path
from typing import Dict, List, Any
import re

# Configuration
BASE_DIR = Path("Base de connaissances")
GITHUB_BASE = "https://11drumboy11.github.io/Prof-de-basse"
OUTPUT_FILE = "mega-search-index-v2.json"

class MegaIndexGenerator:
    def __init__(self):
        self.resources = []
        self.stats = {
            "total_resources": 0,
            "mp3_count": 0,
            "png_count": 0,
            "jpg_count": 0,
            "json_count": 0,
            "html_count": 0,
            "methods_count": 0,
            "partitions_count": 0,
            "theory_count": 0
        }
    
    def scan_base_connaissances(self):
        """Scanne toute la base de connaissances"""
        print("🔍 Scanning Base de connaissances...")
        
        if not BASE_DIR.exists():
            print(f"❌ Directory not found: {BASE_DIR}")
            return
        
        # Scanner les 4 dossiers principaux
        self.scan_methodes()
        self.scan_partitions()
        self.scan_theorie()
        self.scan_mp3()
        
        self.stats["total_resources"] = len(self.resources)
        print(f"✅ Found {self.stats['total_resources']} resources")
    
    def scan_methodes(self):
        """Scanner le dossier Methodes/"""
        methodes_dir = BASE_DIR / "Methodes"
        if not methodes_dir.exists():
            return
        
        print("📚 Scanning Methodes...")
        
        for method_dir in methodes_dir.iterdir():
            if not method_dir.is_dir() or method_dir.name.startswith('.'):
                continue
            
            self.stats["methods_count"] += 1
            method_name = method_dir.name.replace('_v4.0', '').replace('_', ' ')
            
            # Scanner songs_index.json
            songs_index = method_dir / "songs_index.json"
            if songs_index.exists():
                self.add_json_resource(songs_index, method_name, "Méthode")
                
                # Charger et parser le JSON pour extraire les songs
                try:
                    with open(songs_index, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        songs = data.get('songs', [])
                        
                        for song in songs:
                            # Ajouter chaque song comme ressource
                            self.resources.append({
                                "id": f"song-{method_name}-{song.get('page_number', 0)}",
                                "title": song.get('title', f"Page {song.get('page_number')}"),
                                "type": "song",
                                "category": "Méthode",
                                "method": method_name,
                                "page": song.get('page_number'),
                                "tonalite": song.get('tonalite'),
                                "track_number": song.get('track_number'),
                                "techniques": song.get('techniques', []),
                                "page_url": f"{GITHUB_BASE}/Base%20de%20connaissances/Methodes/{method_dir.name}/{song.get('page_url', '')}",
                                "mp3_url": song.get('mp3_url'),
                                "searchText": f"{method_name} {song.get('title', '')} {' '.join(song.get('techniques', []))}"
                            })
                except Exception as e:
                    print(f"  ⚠️ Error parsing {songs_index}: {e}")
            
            # Scanner index.html
            index_html = method_dir / "index.html"
            if index_html.exists():
                self.add_html_resource(index_html, method_name, "Méthode")
            
            # Scanner assets/
            assets_dir = method_dir / "assets"
            if assets_dir.exists():
                self.scan_assets(assets_dir, method_name, "Méthode")
    
    def scan_partitions(self):
        """Scanner le dossier Partitions/"""
        partitions_dir = BASE_DIR / "Partitions"
        if not partitions_dir.exists():
            return
        
        print("🎼 Scanning Partitions...")
        
        for partition_dir in partitions_dir.iterdir():
            if not partition_dir.is_dir() or partition_dir.name.startswith('.'):
                continue
            
            self.stats["partitions_count"] += 1
            partition_name = partition_dir.name.replace('_v4.0', '').replace('_', ' ')
            
            # Scanner songs_index.json
            songs_index = partition_dir / "songs_index.json"
            if songs_index.exists():
                self.add_json_resource(songs_index, partition_name, "Partition")
                
                # Parser pour extraire les songs
                try:
                    with open(songs_index, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        songs = data.get('songs', [])
                        
                        for song in songs:
                            self.resources.append({
                                "id": f"song-{partition_name}-{song.get('page_number', 0)}",
                                "title": song.get('title', f"Page {song.get('page_number')}"),
                                "type": "song",
                                "category": "Partition",
                                "partition": partition_name,
                                "page": song.get('page_number'),
                                "tonalite": song.get('tonalite'),
                                "composer": song.get('composer'),
                                "page_url": f"{GITHUB_BASE}/Base%20de%20connaissances/Partitions/{partition_dir.name}/{song.get('page_url', '')}",
                                "searchText": f"{partition_name} {song.get('title', '')} {song.get('composer', '')}"
                            })
                except Exception as e:
                    print(f"  ⚠️ Error parsing {songs_index}: {e}")
            
            # Scanner index.html
            index_html = partition_dir / "index.html"
            if index_html.exists():
                self.add_html_resource(index_html, partition_name, "Partition")
            
            # Scanner assets/
            assets_dir = partition_dir / "assets"
            if assets_dir.exists():
                self.scan_assets(assets_dir, partition_name, "Partition")
    
    def scan_theorie(self):
        """Scanner le dossier Theorie/"""
        theorie_dir = BASE_DIR / "Theorie"
        if not theorie_dir.exists():
            return
        
        print("📖 Scanning Théorie...")
        
        for theory_dir in theorie_dir.iterdir():
            if not theory_dir.is_dir() or theory_dir.name.startswith('.'):
                continue
            
            self.stats["theory_count"] += 1
            theory_name = theory_dir.name.replace('_v4.0', '').replace('_', ' ')
            
            # Scanner songs_index.json
            songs_index = theory_dir / "songs_index.json"
            if songs_index.exists():
                self.add_json_resource(songs_index, theory_name, "Théorie")
                
                # Parser
                try:
                    with open(songs_index, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        songs = data.get('songs', [])
                        
                        for song in songs:
                            self.resources.append({
                                "id": f"song-{theory_name}-{song.get('page_number', 0)}",
                                "title": song.get('title', f"Page {song.get('page_number')}"),
                                "type": "song",
                                "category": "Théorie",
                                "course": theory_name,
                                "page": song.get('page_number'),
                                "tonalite": song.get('tonalite'),
                                "techniques": song.get('techniques', []),
                                "page_url": f"{GITHUB_BASE}/Base%20de%20connaissances/Theorie/{theory_dir.name}/{song.get('page_url', '')}",
                                "searchText": f"{theory_name} {song.get('title', '')} {' '.join(song.get('techniques', []))}"
                            })
                except Exception as e:
                    print(f"  ⚠️ Error parsing {songs_index}: {e}")
            
            # Scanner index.html
            index_html = theory_dir / "index.html"
            if index_html.exists():
                self.add_html_resource(index_html, theory_name, "Théorie")
            
            # Scanner assets/
            assets_dir = theory_dir / "assets"
            if assets_dir.exists():
                self.scan_assets(assets_dir, theory_name, "Théorie")
    
    def scan_mp3(self):
        """Scanner le dossier MP3/"""
        mp3_dir = BASE_DIR / "MP3"
        if not mp3_dir.exists():
            return
        
        print("🎵 Scanning MP3...")
        
        for mp3_folder in mp3_dir.iterdir():
            if not mp3_folder.is_dir() or mp3_folder.name.startswith('.'):
                continue
            
            folder_name = mp3_folder.name
            
            # Scanner tous les MP3
            for mp3_file in mp3_folder.glob("*.mp3"):
                self.stats["mp3_count"] += 1
                
                # Extraire le numéro de track
                track_match = re.search(r'(\d+)', mp3_file.stem)
                track_num = track_match.group(1) if track_match else None
                
                self.resources.append({
                    "id": f"mp3-{folder_name}-{mp3_file.stem}",
                    "title": mp3_file.stem,
                    "type": "mp3",
                    "category": "Audio",
                    "method": folder_name.replace('_', ' '),
                    "track": track_num,
                    "url": f"{GITHUB_BASE}/Base%20de%20connaissances/MP3/{folder_name}/{mp3_file.name}",
                    "searchText": f"{folder_name} {mp3_file.stem} track {track_num or ''}"
                })
    
    def scan_assets(self, assets_dir: Path, parent_name: str, category: str):
        """Scanner un dossier assets/"""
        pages_dir = assets_dir / "pages"
        if pages_dir.exists():
            assets_dir = pages_dir
        
        # Scanner PNG
        for png_file in assets_dir.glob("*.png"):
            self.stats["png_count"] += 1
            
            # Extraire numéro de page
            page_match = re.search(r'(\d+)', png_file.stem)
            page_num = int(page_match.group(1)) if page_match else None
            
            relative_path = png_file.relative_to(BASE_DIR)
            
            self.resources.append({
                "id": f"png-{parent_name}-{png_file.stem}",
                "title": f"{parent_name} - Page {page_num}" if page_num else png_file.stem,
                "type": "image",
                "format": "png",
                "category": category,
                "parent": parent_name,
                "page": page_num,
                "url": f"{GITHUB_BASE}/Base%20de%20connaissances/{relative_path}",
                "searchText": f"{parent_name} page {page_num or ''} partition"
            })
        
        # Scanner JPG
        for jpg_file in assets_dir.glob("*.jpg"):
            self.stats["jpg_count"] += 1
            
            page_match = re.search(r'(\d+)', jpg_file.stem)
            page_num = int(page_match.group(1)) if page_match else None
            
            relative_path = jpg_file.relative_to(BASE_DIR)
            
            self.resources.append({
                "id": f"jpg-{parent_name}-{jpg_file.stem}",
                "title": f"{parent_name} - Page {page_num}" if page_num else jpg_file.stem,
                "type": "image",
                "format": "jpg",
                "category": category,
                "parent": parent_name,
                "page": page_num,
                "url": f"{GITHUB_BASE}/Base%20de%20connaissances/{relative_path}",
                "searchText": f"{parent_name} page {page_num or ''} partition"
            })
    
    def add_json_resource(self, json_path: Path, parent_name: str, category: str):
        """Ajouter une ressource JSON"""
        self.stats["json_count"] += 1
        
        relative_path = json_path.relative_to(BASE_DIR)
        
        self.resources.append({
            "id": f"json-{parent_name}",
            "title": f"{parent_name} - Index JSON",
            "type": "json",
            "category": category,
            "parent": parent_name,
            "url": f"{GITHUB_BASE}/Base%20de%20connaissances/{relative_path}",
            "searchText": f"{parent_name} index json metadata"
        })
    
    def add_html_resource(self, html_path: Path, parent_name: str, category: str):
        """Ajouter une ressource HTML"""
        self.stats["html_count"] += 1
        
        relative_path = html_path.relative_to(BASE_DIR)
        
        self.resources.append({
            "id": f"html-{parent_name}",
            "title": f"{parent_name} - Navigation HTML",
            "type": "html",
            "category": category,
            "parent": parent_name,
            "url": f"{GITHUB_BASE}/Base%20de%20connaissances/{relative_path}",
            "searchText": f"{parent_name} navigation html index"
        })
    
    def generate_tree_structure(self) -> Dict[str, Any]:
        """Générer l'arborescence hiérarchique"""
        tree = {
            "Méthodes": {},
            "Partitions": {},
            "Théorie": {},
            "MP3": {}
        }
        
        for resource in self.resources:
            category = resource.get("category", "Autre")
            
            if category == "Méthode":
                method = resource.get("method", "Unknown")
                if method not in tree["Méthodes"]:
                    tree["Méthodes"][method] = []
                tree["Méthodes"][method].append(resource)
            
            elif category == "Partition":
                partition = resource.get("partition", "Unknown")
                if partition not in tree["Partitions"]:
                    tree["Partitions"][partition] = []
                tree["Partitions"][partition].append(resource)
            
            elif category == "Théorie":
                course = resource.get("course", "Unknown")
                if course not in tree["Théorie"]:
                    tree["Théorie"][course] = []
                tree["Théorie"][course].append(resource)
            
            elif resource.get("type") == "mp3":
                mp3_method = resource.get("method", "Unknown")
                if mp3_method not in tree["MP3"]:
                    tree["MP3"][mp3_method] = []
                tree["MP3"][mp3_method].append(resource)
        
        return tree
    
    def save_index(self):
        """Sauvegarder l'index JSON"""
        tree_structure = self.generate_tree_structure()
        
        output = {
            "metadata": {
                "generated_at": "2025-11-10",
                "version": "2.0.0",
                "github_base": GITHUB_BASE,
                "stats": self.stats
            },
            "tree": tree_structure,
            "resources": self.resources
        }
        
        with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
            json.dump(output, f, ensure_ascii=False, indent=2)
        
        print(f"\n✅ Index saved to: {OUTPUT_FILE}")
        print(f"📊 Stats:")
        for key, value in self.stats.items():
            print(f"   {key}: {value}")

def main():
    print("=" * 60)
    print("🎸 Prof de Basse - Mega Index Generator v2.0")
    print("=" * 60)
    print()
    
    generator = MegaIndexGenerator()
    generator.scan_base_connaissances()
    generator.save_index()
    
    print()
    print("=" * 60)
    print("✅ Done!")
    print("=" * 60)

if __name__ == "__main__":
    main()
