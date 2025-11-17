/**
 * 🎸 PROF DE BASSE - API FOR GPT
 * API pour faciliter la création de cours
 */

class ProfDeBasse {
    constructor() {
        this.resources = [];
        this.loaded = false;
    }
    
    async loadData() {
        if (this.loaded) return;
        try {
            const response = await fetch('megasearch.json');
            const data = await response.json();
            this.resources = data.resources || [];
            this.loaded = true;
            console.log(`✅ ${this.resources.length} ressources chargées`);
        } catch (error) {
            console.error('❌ Erreur:', error);
        }
    }
    
    findResourcesForLesson(style, level, partNumber) {
        const typeMap = { 1: 'exercise', 2: 'exercise', 3: 'song', 4: 'exercise', 5: 'song' };
        const targetType = typeMap[partNumber] || 'exercise';
        
        return this.resources.filter(r => {
            if (r.type !== targetType) return false;
            
            const meta = r.metadata || {};
            const resourceStyle = (meta.style || '').toLowerCase();
            const resourceLevel = (meta.difficulty || meta.level || '').toLowerCase();
            
            if (style && !resourceStyle.includes(style.toLowerCase())) return false;
            if (level && !resourceLevel.includes(level.toLowerCase())) return false;
            
            return true;
        });
    }
    
    getStats() {
        return {
            total: this.resources.length,
            songs: this.resources.filter(r => r.type === 'song').length,
            exercises: this.resources.filter(r => r.type === 'exercise').length
        };
    }
}

const profDeBasse = new ProfDeBasse();
if (typeof window !== 'undefined') {
    window.ProfDeBasse = profDeBasse;
    document.addEventListener('DOMContentLoaded', () => profDeBasse.loadData());
}
