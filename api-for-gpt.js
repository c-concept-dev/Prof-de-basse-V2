/**
 * API FOR GPT v2.0 - Prof de Basse
 * ====================================
 * API JavaScript pour faciliter l'accès aux ressources
 * depuis Prof de Basse GPT
 * 
 * Date: 17 novembre 2025
 */

class ProfDeBasse API {
    constructor() {
        this.resources = [];
        this.loaded = false;
        this.baseUrl = 'https://11drumboy11.github.io/Prof-de-basse-V2/';
    }
    
    /**
     * Charger les ressources depuis megasearch.json
     */
    async load() {
        if (this.loaded) return this.resources;
        
        try {
            const response = await fetch('megasearch.json');
            const data = await response.json();
            this.resources = data.resources || [];
            this.loaded = true;
            console.log(`✅ API chargée: ${this.resources.length} ressources`);
            return this.resources;
        } catch (error) {
            console.error('❌ Erreur chargement API:', error);
            throw error;
        }
    }
    
    /**
     * Rechercher des ressources
     * @param {string} query - Terme de recherche
     * @param {Object} filters - Filtres optionnels
     * @returns {Array} Ressources correspondantes
     */
    async search(query, filters = {}) {
        await this.load();
        
        let results = this.resources;
        
        // Filtre par texte
        if (query) {
            const q = query.toLowerCase();
            results = results.filter(r => {
                const searchText = (r.searchText || '').toLowerCase();
                return searchText.includes(q);
            });
        }
        
        // Filtre par type
        if (filters.type) {
            results = results.filter(r => r.type === filters.type);
        }
        
        // Filtre par méthode/livre
        if (filters.book) {
            results = results.filter(r => r.metadata?.book === filters.book);
        }
        
        // Filtre par difficulté
        if (filters.difficulty) {
            results = results.filter(r => r.metadata?.difficulty === filters.difficulty);
        }
        
        // Filtre par style
        if (filters.style) {
            results = results.filter(r => r.metadata?.style === filters.style);
        }
        
        // Filtre MP3 seulement
        if (filters.onlyMp3) {
            results = results.filter(r => r.metadata?.has_mp3);
        }
        
        // Limite
        if (filters.limit) {
            results = results.slice(0, filters.limit);
        }
        
        return results;
    }
    
    /**
     * Obtenir les ressources avec MP3
     * @param {Object} filters - Filtres optionnels
     * @returns {Array} Ressources avec MP3
     */
    async getMp3Resources(filters = {}) {
        return this.search('', { ...filters, onlyMp3: true });
    }
    
    /**
     * Obtenir les ressources par méthode
     * @param {string} bookName - Nom de la méthode
     * @param {Object} filters - Filtres optionnels
     * @returns {Array} Ressources de cette méthode
     */
    async getByBook(bookName, filters = {}) {
        return this.search('', { ...filters, book: bookName });
    }
    
    /**
     * Obtenir les exercices pour un style donné
     * @param {string} style - Style (funk, jazz, rock, etc.)
     * @param {string} difficulty - Difficulté (débutant, intermédiaire, avancé)
     * @returns {Array} Exercices correspondants
     */
    async getExercisesByStyle(style, difficulty = null) {
        const filters = {
            type: 'exercise',
            style: style
        };
        
        if (difficulty) {
            filters.difficulty = difficulty;
        }
        
        return this.search('', filters);
    }
    
    /**
     * Obtenir les morceaux pour un style donné
     * @param {string} style - Style (funk, jazz, rock, etc.)
     * @returns {Array} Morceaux correspondants
     */
    async getSongsByStyle(style) {
        return this.search('', {
            type: 'song',
            style: style
        });
    }
    
    /**
     * Obtenir les ressources par tonalité
     * @param {string} key - Tonalité (C, Dm, Eb7, etc.)
     * @returns {Array} Ressources dans cette tonalité
     */
    async getByKey(key) {
        await this.load();
        return this.resources.filter(r => r.metadata?.key === key);
    }
    
    /**
     * Obtenir toutes les méthodes disponibles
     * @returns {Array} Liste des méthodes
     */
    async getAvailableBooks() {
        await this.load();
        const books = new Set();
        this.resources.forEach(r => {
            if (r.metadata?.book) books.add(r.metadata.book);
        });
        return Array.from(books).sort();
    }
    
    /**
     * Obtenir les stats globales
     * @returns {Object} Statistiques
     */
    async getStats() {
        await this.load();
        
        const stats = {
            total: this.resources.length,
            withMp3: 0,
            byType: {},
            byBook: {},
            byStyle: {},
            byDifficulty: {}
        };
        
        this.resources.forEach(r => {
            // MP3
            if (r.metadata?.has_mp3) stats.withMp3++;
            
            // Type
            const type = r.type || 'unknown';
            stats.byType[type] = (stats.byType[type] || 0) + 1;
            
            // Book
            const book = r.metadata?.book || 'unknown';
            stats.byBook[book] = (stats.byBook[book] || 0) + 1;
            
            // Style
            const style = r.metadata?.style;
            if (style) {
                stats.byStyle[style] = (stats.byStyle[style] || 0) + 1;
            }
            
            // Difficulty
            const difficulty = r.metadata?.difficulty;
            if (difficulty) {
                stats.byDifficulty[difficulty] = (stats.byDifficulty[difficulty] || 0) + 1;
            }
        });
        
        return stats;
    }
    
    /**
     * MÉTHODE SPÉCIALE POUR PROF DE BASSE GPT
     * Recherche intelligente pour créer un cours
     * @param {Object} params - Paramètres du cours
     * @returns {Object} Ressources organisées par partie
     */
    async buildCourseResources(params) {
        const {
            style = 'funk',
            difficulty = 'débutant',
            includeWarmup = true,
            includeTheory = true,
            includeApplication = true,
            includeImprovisation = true,
            includeFun = true
        } = params;
        
        await this.load();
        
        const course = {
            warmup: [],
            theory: [],
            application: [],
            improvisation: [],
            fun: []
        };
        
        // PARTIE 1 : Échauffement (3-5 exercices simples)
        if (includeWarmup) {
            course.warmup = await this.search('', {
                type: 'exercise',
                style: style,
                difficulty: 'débutant',
                limit: 5
            });
        }
        
        // PARTIE 2 : Théorie (concepts + exemples avec MP3)
        if (includeTheory) {
            course.theory = await this.search(style, {
                type: 'concept',
                limit: 3
            });
        }
        
        // PARTIE 3 : Application (morceau complet avec MP3)
        if (includeApplication) {
            course.application = await this.search('', {
                type: 'song',
                style: style,
                difficulty: difficulty,
                onlyMp3: true,
                limit: 1
            });
        }
        
        // PARTIE 4 : Improvisation (backing tracks)
        if (includeImprovisation) {
            course.improvisation = await this.search('vamp', {
                type: 'exercise',
                style: style,
                onlyMp3: true,
                limit: 2
            });
        }
        
        // PARTIE 5 : Fun (riffs iconiques courts)
        if (includeFun) {
            course.fun = await this.search('riff', {
                type: 'exercise',
                style: style,
                limit: 1
            });
        }
        
        return course;
    }
    
    /**
     * Obtenir des recommandations basées sur une ressource
     * @param {Object} resource - Ressource de référence
     * @param {number} limit - Nombre de recommandations
     * @returns {Array} Ressources similaires
     */
    async getRecommendations(resource, limit = 5) {
        await this.load();
        
        const filters = {
            type: resource.type,
            style: resource.metadata?.style,
            difficulty: resource.metadata?.difficulty
        };
        
        let recommendations = await this.search('', filters);
        
        // Exclure la ressource elle-même
        recommendations = recommendations.filter(r => r.id !== resource.id);
        
        // Limiter
        return recommendations.slice(0, limit);
    }
    
    /**
     * ENDPOINT POUR GPT : Recherche d'exercices pour échauffement
     * @param {string} style - Style musical
     * @param {number} count - Nombre d'exercices (3-5)
     * @returns {Array} Exercices d'échauffement
     */
    async getWarmupExercises(style, count = 5) {
        return this.search('', {
            type: 'exercise',
            style: style,
            difficulty: 'débutant',
            limit: count
        });
    }
    
    /**
     * ENDPOINT POUR GPT : Recherche de backing tracks
     * @param {string} style - Style musical
     * @param {string} key - Tonalité (optionnel)
     * @returns {Array} Backing tracks avec MP3
     */
    async getBackingTracks(style, key = null) {
        const filters = {
            onlyMp3: true,
            style: style
        };
        
        let tracks = await this.search('backing', filters);
        
        if (key) {
            tracks = tracks.filter(t => t.metadata?.key === key);
        }
        
        return tracks;
    }
    
    /**
     * ENDPOINT POUR GPT : Recherche de morceaux complets
     * @param {string} style - Style musical
     * @param {string} difficulty - Difficulté
     * @param {boolean} requireMp3 - MP3 obligatoire
     * @returns {Array} Morceaux complets
     */
    async getCompleteSongs(style, difficulty = null, requireMp3 = true) {
        const filters = {
            type: 'song',
            style: style,
            onlyMp3: requireMp3
        };
        
        if (difficulty) {
            filters.difficulty = difficulty;
        }
        
        return this.search('', filters);
    }
}

// =============================================
// INITIALISATION GLOBALE
// =============================================

// Créer instance globale
window.profDeBasse = new ProfDeBasse();

// Log de confirmation
console.log('✅ API Prof de Basse v2.0 chargée');
console.log('📘 Documentation: window.profDeBasse');
console.log('🎸 Exemples:');
console.log('   - profDeBasse.search("funk")');
console.log('   - profDeBasse.getMp3Resources()');
console.log('   - profDeBasse.buildCourseResources({style: "funk"})');
console.log('   - profDeBasse.getWarmupExercises("funk", 5)');
console.log('   - profDeBasse.getBackingTracks("jazz", "Dm7")');

// Export pour modules ES6 (optionnel)
if (typeof module !== 'undefined' && module.exports) {
    module.exports = ProfDeBasse;
}
