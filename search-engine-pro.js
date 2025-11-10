/**
 * Search Engine Pro V3 - Prof de Basse
 * Recherche ultra-rapide avec full-text, OCR, filtres avancés
 */

class ProfDeBasseSearch {
    constructor() {
        this.megaIndex = [];
        this.searchCache = new Map();
        this.initialized = false;
    }

    /**
     * Initialise le moteur avec le MEGA index
     */
    async init(indexUrl = 'mega-search-index.json') {
        try {
            console.log('🔍 Chargement MEGA index...');
            const response = await fetch(indexUrl);
            const data = await response.json();
            
            this.megaIndex = data.resources || [];
            this.initialized = true;
            
            console.log(`✅ ${this.megaIndex.length} ressources chargées`);
            return true;
        } catch (error) {
            console.error('❌ Erreur chargement index:', error);
            return false;
        }
    }

    /**
     * Recherche principale - full-text + filtres
     */
    search(query, filters = {}) {
        if (!this.initialized) {
            console.warn('⚠️ Index non initialisé');
            return [];
        }

        // Cache
        const cacheKey = JSON.stringify({ query, filters });
        if (this.searchCache.has(cacheKey)) {
            return this.searchCache.get(cacheKey);
        }

        const startTime = performance.now();
        
        // Normaliser la requête
        const normalizedQuery = query.toLowerCase().trim();
        
        if (!normalizedQuery && Object.keys(filters).length === 0) {
            return this.megaIndex;
        }

        // Recherche
        let results = this.megaIndex;

        // 1. Filtres de type
        if (filters.type && filters.type !== 'all') {
            results = results.filter(r => r.type === filters.type);
        }

        // 2. Filtres de style
        if (filters.style) {
            results = results.filter(r => {
                const styles = r.metadata?.styles || [];
                const techniques = r.metadata?.techniques || [];
                const tags = r.metadata?.tags || [];
                const allTags = [...styles, ...techniques, ...tags].map(t => t.toLowerCase());
                return allTags.includes(filters.style.toLowerCase());
            });
        }

        // 3. Filtres de niveau
        if (filters.level) {
            results = results.filter(r => 
                r.metadata?.level?.toLowerCase() === filters.level.toLowerCase()
            );
        }

        // 4. Recherche full-text
        if (normalizedQuery) {
            // Séparer les termes
            const terms = normalizedQuery.split(/\s+/).filter(t => t.length > 0);
            
            results = results.filter(resource => {
                const searchText = resource.search_text || '';
                const title = resource.title.toLowerCase();
                
                // Recherche par phrase exacte
                if (normalizedQuery.includes('"')) {
                    const exactPhrase = normalizedQuery.replace(/"/g, '');
                    return searchText.includes(exactPhrase) || title.includes(exactPhrase);
                }
                
                // Recherche par tous les termes
                return terms.every(term => 
                    searchText.includes(term) || title.includes(term)
                );
            });
            
            // Scoring de pertinence
            results = results.map(resource => {
                let score = 0;
                const title = resource.title.toLowerCase();
                const searchText = resource.search_text || '';
                
                // +10 si dans le titre
                terms.forEach(term => {
                    if (title.includes(term)) score += 10;
                });
                
                // +5 si dans le contenu
                terms.forEach(term => {
                    if (searchText.includes(term)) score += 5;
                });
                
                // +3 si titre exact
                if (title === normalizedQuery) score += 100;
                
                // +2 si commence par query
                if (title.startsWith(normalizedQuery)) score += 50;
                
                return { ...resource, _score: score };
            });
            
            // Trier par score
            results.sort((a, b) => b._score - a._score);
        }

        const endTime = performance.now();
        console.log(`⚡ Recherche: ${(endTime - startTime).toFixed(2)}ms - ${results.length} résultats`);

        // Cache
        this.searchCache.set(cacheKey, results);
        
        return results;
    }

    /**
     * Recherche par phrase exacte
     */
    searchExact(phrase) {
        return this.search(`"${phrase}"`);
    }

    /**
     * Suggestions auto-complete
     */
    getSuggestions(partial, limit = 10) {
        if (!partial || partial.length < 2) return [];
        
        const lower = partial.toLowerCase();
        const suggestions = new Set();
        
        this.megaIndex.forEach(resource => {
            const title = resource.title.toLowerCase();
            if (title.includes(lower)) {
                suggestions.add(resource.title);
            }
            
            // Ajouter aussi les tags
            const tags = [
                ...(resource.metadata?.styles || []),
                ...(resource.metadata?.techniques || []),
                ...(resource.metadata?.tags || [])
            ];
            
            tags.forEach(tag => {
                if (tag.toLowerCase().includes(lower)) {
                    suggestions.add(tag);
                }
            });
        });
        
        return Array.from(suggestions).slice(0, limit);
    }

    /**
     * Filtres disponibles
     */
    getAvailableFilters() {
        const types = new Set();
        const styles = new Set();
        const levels = new Set();
        
        this.megaIndex.forEach(resource => {
            types.add(resource.type);
            
            const resourceStyles = [
                ...(resource.metadata?.styles || []),
                ...(resource.metadata?.techniques || [])
            ];
            resourceStyles.forEach(s => styles.add(s));
            
            if (resource.metadata?.level) {
                levels.add(resource.metadata.level);
            }
        });
        
        return {
            types: Array.from(types).sort(),
            styles: Array.from(styles).sort(),
            levels: Array.from(levels).sort()
        };
    }

    /**
     * Statistiques
     */
    getStats() {
        const stats = {
            total: this.megaIndex.length,
            byType: {},
            byStyle: {},
            byLevel: {}
        };
        
        this.megaIndex.forEach(resource => {
            // Par type
            stats.byType[resource.type] = (stats.byType[resource.type] || 0) + 1;
            
            // Par style
            const styles = [
                ...(resource.metadata?.styles || []),
                ...(resource.metadata?.techniques || [])
            ];
            styles.forEach(style => {
                stats.byStyle[style] = (stats.byStyle[style] || 0) + 1;
            });
            
            // Par niveau
            const level = resource.metadata?.level;
            if (level) {
                stats.byLevel[level] = (stats.byLevel[level] || 0) + 1;
            }
        });
        
        return stats;
    }

    /**
     * Trouve une ressource par ID
     */
    getResourceById(id) {
        return this.megaIndex.find(r => r.id === id);
    }

    /**
     * Recherche similaire (basée sur tags communs)
     */
    findSimilar(resource, limit = 5) {
        const resourceTags = [
            ...(resource.metadata?.styles || []),
            ...(resource.metadata?.techniques || []),
            ...(resource.metadata?.tags || [])
        ].map(t => t.toLowerCase());
        
        if (resourceTags.length === 0) return [];
        
        const similar = this.megaIndex
            .filter(r => r.id !== resource.id)
            .map(r => {
                const rTags = [
                    ...(r.metadata?.styles || []),
                    ...(r.metadata?.techniques || []),
                    ...(r.metadata?.tags || [])
                ].map(t => t.toLowerCase());
                
                // Compter tags communs
                const commonTags = resourceTags.filter(t => rTags.includes(t));
                
                return {
                    ...r,
                    _similarity: commonTags.length
                };
            })
            .filter(r => r._similarity > 0)
            .sort((a, b) => b._similarity - a._similarity)
            .slice(0, limit);
        
        return similar;
    }
}

// Export pour utilisation globale
window.ProfDeBasseSearch = ProfDeBasseSearch;
