import { translator } from '../utils/translator.js';

class LanguageSelector {
  constructor(containerId) {
    this.container = document.getElementById(containerId);
    this.currentLanguage = translator.getCurrentLanguage();
    this.languages = {
      'ca': { name: 'Català', flag: '🏴󠁥󠁳󠁣󠁴󠁿' },
      'en': { name: 'English', flag: '🇺🇸' }
    };
    
    this.render();
    this.setupEventListeners();
  }
  
  render() {
    this.container.innerHTML = `
      <div class="language-selector">
        <label for="language-select">Idioma / Language:</label>
        <select id="language-select" class="language-dropdown">
          ${Object.entries(this.languages).map(([code, info]) => `
            <option value="${code}" ${code === this.currentLanguage ? 'selected' : ''}>
              ${info.flag} ${info.name}
            </option>
          `).join('')}
        </select>
        <span class="loading-indicator" style="display: none;">🔄</span>
      </div>
      
      <style>
        .language-selector {
          display: flex;
          align-items: center;
          gap: 10px;
          margin: 10px 0;
        }
        
        .language-dropdown {
          padding: 5px 10px;
          border: 1px solid #ccc;
          border-radius: 4px;
          background: white;
          cursor: pointer;
        }
        
        .language-dropdown:hover {
          border-color: #007cba;
        }
        
        .loading-indicator {
          animation: spin 1s linear infinite;
        }
        
        @keyframes spin {
          from { transform: rotate(0deg); }
          to { transform: rotate(360deg); }
        }
      </style>
    `;
  }
  
  setupEventListeners() {
    const select = this.container.querySelector('#language-select');
    const loading = this.container.querySelector('.loading-indicator');
    
    select.addEventListener('change', async (e) => {
      const newLanguage = e.target.value;
      
      if (newLanguage === this.currentLanguage) return;
      
      loading.style.display = 'inline';
      select.disabled = true;
      
      try {
        await translator.changeLanguage(newLanguage);
        this.currentLanguage = newLanguage;
        this.updateUI();
        
        console.log(`🌍 Idioma canviat a: ${newLanguage}`);
      } catch (error) {
        console.error('Error canviant idioma:', error);
      } finally {
        loading.style.display = 'none';
        select.disabled = false;
      }
    });
  }
  
  updateUI() {
    const elements = document.querySelectorAll('[data-i18n]');
    elements.forEach(element => {
      const key = element.getAttribute('data-i18n');
      const translation = translator.t(key);
      
      if (element.tagName === 'INPUT' && element.type !== 'button') {
        element.placeholder = translation;
      } else {
        element.textContent = translation;
      }
    });
    
    document.title = translator.t('app.name');
  }
}

export default LanguageSelector;
