/**
 * 🎸 PROF DE BASSE - API FOR GPT
 * API JavaScript pour faciliter la création de cours avec GPT
 * 
 * USAGE dans Prof de Basse GPT:
 * 
 * // Trouver ressources pour Partie 1 (Échauffement)
 * const warmup = ProfDeBasse.findResourcesForLesson('funk', 'débutant', 1);
 * 
 * // Suggérer exercice pour technique spécifique
 * const slap = ProfDeBasse.findByTechnique('slap', 'funk');
 * 
 * // Exercice aléatoire pour Partie 5 (Fun)
 * const fun = ProfDeBasse.getRandomExercise({ style: 'funk' });
 * 
 * // Rechercher dans un livre spécifique
 * const liebman = ProfDeBasse.getFromBook('Liebman');
 */

class ProfDeBasse {
    constructor() {
        this.resources = [];
        this.loaded = false;
    }
    
    /**
     * Charge les données depuis megasearch.json
     */
    async loadData() {
        if (this.loaded) return;
        
        try {
            const response = await fetch('megasearch.json');
            const data = await response.json();
            this.resources = data.resources || [];
            this.loaded = true;
            console.log(`✅ Prof de Basse API : ${this.resources.length} ressources chargées`);
        } catch (error) {
            console.error('❌ Erreur chargement données:', error);
        }
    }
    
    /**
     * Trouve ressources pour une leçon spécifique (Structure 5 parties)
     * @param {string} style - Style musical ('funk', 'jazz', 'rock', etc.)
     * @param {string} level - Niveau ('débutant', 'intermédiaire', 'avancé')
     * @param {number} partNumber - Numéro partie (1-5)
     * @returns {Array} Ressources filtrées
     * 
     * Partie 1 : Échauffement (exercises)
     * Partie 2 : Théorie (exercises théoriques)
     * Partie 3 : Application (songs)
     * Partie 4 : Improvisation (exercises)
     * Partie 5 : Fun (songs)
     */
    findResourcesForLesson(style, level, partNumber) {
        const typeMap = {
            1: 'exercise',      // Échauffement
            2: 'exercise',      // Théorie
            3: 'song',          // Application
            4: 'exercise',      // Improvisation
            5: 'song'           // Fun
        };
        
        const targetType = typeMap[partNumber] || 'exercise';
        
        return this.resources.filter(r => {
            const meta = r.metadata || {};
            
            // Filtrer par type
            if (r.type !== targetType) return false;
            
            // Filtrer par style
            const resourceStyle = (meta.style || '').toLowerCase();
            if (style && !resourceStyle.includes(style.toLowerCase())) return false;
            
            // Filtrer par niveau
            const resourceLevel = (meta.difficulty || meta.level || '').toLowerCase();
            if (level && !resourceLevel.includes(level.toLowerCase())) return false;
            
            return true;
        });
    }
    
    /**
     * Trouve ressources par technique
     * @param {string} technique - Technique ('slap', 'walking', 'fingerstyle', etc.)
     * @param {string} style - Style optionnel
     * @returns {Array} Ressources avec cette technique
     */
    findByTechnique(technique, style = null) {
        return this.resources.filter(r => {
            const meta = r.metadata || {};
            const resourceTechnique = (meta.technique || '').toLowerCase();
            const title = (r.title || '').toLowerCase();
            
            // Vérifier technique dans metadata ou titre
            if (!resourceTechnique.includes(technique.toLowerCase()) && 
                !title.includes(technique.toLowerCase())) return false;
            
            // Filtrer par style si spécifié
            if (style) {
                const resourceStyle = (meta.style || '').toLowerCase();
                if (!resourceStyle.includes(style.toLowerCase())) return false;
            }
            
            return true;
        });
    }
    
    /**
     * Obtient un exercice aléatoire
     * @param {Object} filters - Filtres optionnels { style, level, type, technique }
     * @returns {Object|null} Ressource aléatoire
     */
    getRandomExercise(filters = {}) {
        let filtered = this.resources;
        
        // Appliquer filtres
        if (filters.style) {
            filtered = filtered.filter(r => {
                const style = (r.metadata?.style || '').toLowerCase();
                return style.includes(filters.style.toLowerCase());
            });
        }
        
        if (filters.level || filters.difficulty) {
            const targetLevel = (filters.level || filters.difficulty).toLowerCase();
            filtered = filtered.filter(r => {
                const level = (r.metadata?.difficulty || r.metadata?.level || '').toLowerCase();
                return level.includes(targetLevel);
            });
        }
        
        if (filters.type) {
            filtered = filtered.filter(r => r.type === filters.type);
        }
        
        if (filters.technique) {
            filtered = filtered.filter(r => {
                const technique = (r.metadata?.technique || '').toLowerCase();
                const title = (r.title || '').toLowerCase();
                return technique.includes(filters.technique.toLowerCase()) ||
                       title.includes(filters.technique.toLowerCase());
            });
        }
        
        // Retourner aléatoire
        if (filtered.length === 0) return null;
        
        const randomIndex = Math.floor(Math.random() * filtered.length);
        return filtered[randomIndex];
    }
    
    /**
     * Recherche ressources par mots-clés
     * @param {string} keywords - Mots-clés de recherche
     * @returns {Array} Ressources correspondantes
     */
    search(keywords) {
        const query = keywords.toLowerCase();
        
        return this.resources.filter(r => {
            const searchText = (r.searchText || '').toLowerCase();
            const title = (r.title || '').toLowerCase();
            const book = (r.metadata?.book || '').toLowerCase();
            const technique = (r.metadata?.technique || '').toLowerCase();
            
            return searchText.includes(query) || 
                   title.includes(query) || 
                   book.includes(query) ||
                   technique.includes(query);
        });
    }
    
    /**
     * Obtient ressources d'un livre spécifique
     * @param {string} bookName - Nom du livre (partiel OK)
     * @returns {Array} Ressources du livre
     */
    getFromBook(bookName) {
        const query = bookName.toLowerCase();
        
        return this.resources.filter(r => {
            const book = (r.metadata?.book || '').toLowerCase();
            return book.includes(query);
        });
    }
    
    /**
     * Obtient les ressources par page (pour retrouver un exercice spécifique)
     * @param {string} bookName - Nom du livre
     * @param {number} page - Numéro de page
     * @returns {Array} Ressources de cette page
     */
    getByPage(bookName, page) {
        return this.resources.filter(r => {
            const book = (r.metadata?.book || '').toLowerCase();
            return book.includes(bookName.toLowerCase()) && r.page === page;
        });
    }
    
    /**
     * Obtient statistiques globales
     * @returns {Object} Stats complètes
     */
    getStats() {
        const stats = {
            total: this.resources.length,
            songs: 0,
            exercises: 0,
            byDifficulty: {},
            byStyle: {},
            byBook: {},
            byTechnique: {}
        };
        
        this.resources.forEach(r => {
            // Par type
            if (r.type === 'song') stats.songs++;
            if (r.type === 'exercise') stats.exercises++;
            
            const meta = r.metadata || {};
            
            // Par difficulté
            const difficulty = meta.difficulty || meta.level || 'unknown';
            stats.byDifficulty[difficulty] = (stats.byDifficulty[difficulty] || 0) + 1;
            
            // Par style
            const style = meta.style || 'unknown';
            stats.byStyle[style] = (stats.byStyle[style] || 0) + 1;
            
            // Par livre
            const book = meta.book || 'unknown';
            stats.byBook[book] = (stats.byBook[book] || 0) + 1;
            
            // Par technique
            const technique = meta.technique || 'none';
            if (technique !== 'none') {
                stats.byTechnique[technique] = (stats.byTechnique[technique] || 0) + 1;
            }
        });
        
        return stats;
    }
    
    /**
     * Obtient la liste des livres disponibles avec stats
     * @returns {Array} Liste des livres triés par nombre de ressources
     */
    getAvailableBooks() {
        const books = {};
        
        this.resources.forEach(r => {
            const book = r.metadata?.book || 'unknown';
            if (!books[book]) {
                books[book] = {
                    name: book,
                    count: 0,
                    songs: 0,
                    exercises: 0,
                    style: r.metadata?.style || 'unknown',
                    category: r.metadata?.category || 'unknown'
                };
            }
            books[book].count++;
            if (r.type === 'song') books[book].songs++;
            if (r.type === 'exercise') books[book].exercises++;
        });
        
        return Object.values(books).sort((a, b) => b.count - a.count);
    }
    
    /**
     * Obtient les styles disponibles
     * @returns {Array} Liste des styles avec nombre de ressources
     */
    getAvailableStyles() {
        const styles = {};
        
        this.resources.forEach(r => {
            const style = r.metadata?.style || 'unknown';
            styles[style] = (styles[style] || 0) + 1;
        });
        
        return Object.entries(styles)
            .map(([name, count]) => ({ name, count }))
            .sort((a, b) => b.count - a.count);
    }
    
    /**
     * Obtient les techniques disponibles
     * @returns {Array} Liste des techniques avec nombre de ressources
     */
    getAvailableTechniques() {
        const techniques = {};
        
        this.resources.forEach(r => {
            const technique = r.metadata?.technique;
            if (technique) {
                techniques[technique] = (techniques[technique] || 0) + 1;
            }
        });
        
        return Object.entries(techniques)
            .map(([name, count]) => ({ name, count }))
            .sort((a, b) => b.count - a.count);
    }
    
    /**
     * Génère un cours complet automatiquement
     * @param {string} style - Style du cours
     * @param {string} level - Niveau du cours
     * @returns {Object} Structure de cours avec 5 parties
     */
    generateCourse(style, level) {
        return {
            metadata: {
                style,
                level,
                generatedAt: new Date().toISOString()
            },
            partie1: this.findResourcesForLesson(style, level, 1).slice(0, 3),
            partie2: this.findResourcesForLesson(style, level, 2).slice(0, 2),
            partie3: this.findResourcesForLesson(style, level, 3).slice(0, 1),
            partie4: this.findResourcesForLesson(style, level, 4).slice(0, 2),
            partie5: this.getRandomExercise({ style, type: 'song' })
        };
    }
}

// Instance globale
const profDeBasse = new ProfDeBasse();

// Auto-load au chargement page
if (typeof window !== 'undefined') {
    window.ProfDeBasse = profDeBasse;
    
    // Charger automatiquement au démarrage
    document.addEventListener('DOMContentLoaded', () => {
        profDeBasse.loadData().then(() => {
            console.log('🎸 Prof de Basse API prête !');
            console.log('📊 Utilisez ProfDeBasse.getStats() pour voir les stats');
            console.log('📚 Utilisez ProfDeBasse.getAvailableBooks() pour voir les livres');
        });
    });
}

// Export pour Node.js
if (typeof module !== 'undefined' && module.exports) {
    module.exports = ProfDeBasse;
}
