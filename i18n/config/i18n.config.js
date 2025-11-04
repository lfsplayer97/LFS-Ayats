export const i18nConfig = {
  // Idiomes suportats
  supportedLocales: ['ca', 'en'],
  
  // Idioma per defecte
  defaultLocale: 'en',
  
  // Idioma de fallback
  fallbackLocale: 'en',
  
  // Detecció automàtica
  detection: {
    order: ['localStorage', 'navigator', 'htmlTag'],
    caches: ['localStorage'],
    lookupLocalStorage: 'lfs-ayats-language'
  },
  
  // Namespaces
  defaultNS: 'common',
  ns: ['common', 'ui', 'errors', 'telemetry']
};
