class Translator {
  constructor(locale = 'en') {
    this.currentLocale = locale;
    this.fallbackLocale = 'en';
    this.translations = new Map();
    this.loadedNamespaces = new Set();
    this.listeners = new Set();
    
    this.init();
  }
  
  async init() {
    // Detectar idioma del navegador o localStorage
    this.currentLocale = this.detectLanguage();
    
    // Carregar namespace per defecte
    await this.loadNamespace('common');
    
    // Notificar canvi d'idioma
    this.notifyLanguageChange();
  }
  
  detectLanguage() {
    // Comprovar localStorage primer
    const stored = localStorage.getItem('lfs-ayats-language');
    if (stored && this.isSupported(stored)) {
      return stored;
    }
    
    // Comprovar idioma del navegador
    const browserLang = navigator.language.split('-')[0];
    if (this.isSupported(browserLang)) {
      return browserLang;
    }
    
    // Fallback per defecte
    return 'en';
  }
  
  isSupported(locale) {
    return ['ca', 'en'].includes(locale);
  }
  
  async loadNamespace(namespace) {
    const key = `${this.currentLocale}:${namespace}`;
    if (this.loadedNamespaces.has(key)) {
      return;
    }
    
    try {
      const response = await fetch(`/i18n/locales/${this.currentLocale}/${namespace}.json`);
      const translations = await response.json();
      
      this.translations.set(key, translations);
      this.loadedNamespaces.add(key);
      
      console.log(`✅ Carregat: ${namespace} (${this.currentLocale})`);
    } catch (error) {
      console.warn(`⚠️ No s'ha pogut carregar ${namespace} per ${this.currentLocale}:`, error);
    }
  }
  
  t(key, params = {}) {
    const [namespace, ...keyParts] = key.includes(':') ? key.split(':') : ['common', key];
    const translationKey = keyParts.join(':') || namespace;
    const ns = key.includes(':') ? namespace : 'common';
    
    // Obtenir traducció
    let value = this.getTranslation(translationKey, this.currentLocale, ns);
    
    // Provar fallback si no es troba
    if (value === null && this.currentLocale !== this.fallbackLocale) {
      value = this.getTranslation(translationKey, this.fallbackLocale, ns);
    }
    
    // Retornar clau si no es troba res
    if (value === null) {
      console.warn(`🔍 Traducció no trobada: ${key}`);
      return key;
    }
    
    // Aplicar interpolació de paràmetres
    return this.interpolate(value, params);
  }
  
  getTranslation(key, locale, namespace) {
    const translations = this.translations.get(`${locale}:${namespace}`);
    if (!translations) return null;
    
    const keys = key.split('.');
    let value = translations;
    
    for (const k of keys) {
      value = value?.[k];
      if (value === undefined) return null;
    }
    
    return value;
  }
  
  interpolate(text, params) {
    if (typeof text !== 'string') return text;
    
    return text.replace(/\{\{(\w+)\}\}/g, (match, param) => {
      return params[param] !== undefined ? params[param] : match;
    });
  }
  
  async changeLanguage(locale) {
    if (!this.isSupported(locale)) {
      console.warn(`❌ Idioma no suportat: ${locale}`);
      return;
    }
    
    this.currentLocale = locale;
    
    // Desar a localStorage
    localStorage.setItem('lfs-ayats-language', locale);
    
    // Recarregar namespaces per al nou idioma
    const namespacesToReload = Array.from(this.loadedNamespaces)
      .map(key => key.split(':')[1])
      .filter((ns, index, self) => self.indexOf(ns) === index);
    
    for (const ns of namespacesToReload) {
      await this.loadNamespace(ns);
    }
    
    this.notifyLanguageChange();
    console.log(`🌍 Idioma canviat a: ${locale}`);
  }
  
  getCurrentLanguage() {
    return this.currentLocale;
  }
  
  addLanguageChangeListener(callback) {
    this.listeners.add(callback);
    return () => this.listeners.delete(callback);
  }
  
  notifyLanguageChange() {
    this.listeners.forEach(callback => {
      try {
        callback(this.currentLocale);
      } catch (error) {
        console.error('Error en listener de canvi d\'idioma:', error);
      }
    });
  }
}

// Instància singleton
export const translator = new Translator();
export default Translator;
