// Simulació de càrrega per testing
const mockTranslations = {
  ca: {
    'app.name': 'LFS Ayats',
    'app.description': 'Sistema de telemetria per a Live for Speed',
    'actions.start': 'Iniciar',
    'actions.stop': 'Aturar',
    'actions.connect': 'Connectar',
    'actions.disconnect': 'Desconnectar',
    'actions.save': 'Desar',
    'actions.load': 'Carregar',
    'status.connected': 'Connectat',
    'status.disconnected': 'Desconnectat',
    'status.loading': 'Carregant...'
  },
  en: {
    'app.name': 'LFS Ayats',
    'app.description': 'Telemetry system for Live for Speed',
    'actions.start': 'Start',
    'actions.stop': 'Stop',
    'actions.connect': 'Connect',
    'actions.disconnect': 'Disconnect',
    'actions.save': 'Save',
    'actions.load': 'Load',
    'status.connected': 'Connected',
    'status.disconnected': 'Disconnected',
    'status.loading': 'Loading...'
  }
};

// Sistema de traducció simple
class SimpleTranslator {
  constructor() {
    this.locale = localStorage.getItem('lfs-ayats-language') || 'en';
    this.translations = mockTranslations;
  }
  
  t(key) {
    return this.translations[this.locale]?.[key] || key;
  }
  
  changeLanguage(locale) {
    this.locale = locale;
    localStorage.setItem('lfs-ayats-language', locale);
    this.updateUI();
  }
  
  updateUI() {
    document.querySelectorAll('[data-i18n]').forEach(element => {
      const key = element.getAttribute('data-i18n');
      element.textContent = this.t(key);
    });
    document.title = this.t('app.name');
  }
}

// Crear instància global
window.translator = new SimpleTranslator();

// Selector simple
function createLanguageSelector(containerId) {
  const container = document.getElementById(containerId);
  container.innerHTML = `
    <label>Idioma / Language:</label>
    <select id="lang-select">
      <option value="ca" ${window.translator.locale === 'ca' ? 'selected' : ''}>🏴󠁥󠁳󠁣󠁴󠁿 Català</option>
      <option value="en" ${window.translator.locale === 'en' ? 'selected' : ''}>🇺🇸 English</option>
    </select>
  `;
  
  container.querySelector('#lang-select').addEventListener('change', (e) => {
    window.translator.changeLanguage(e.target.value);
  });
}

// Inicialització
document.addEventListener('DOMContentLoaded', () => {
  createLanguageSelector('language-selector-container');
  window.translator.updateUI();
});
