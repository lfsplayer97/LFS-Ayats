import fs from 'fs';
import path from 'path';

const validateTranslations = () => {
  const locales = ['ca', 'en'];
  const namespaces = ['common', 'telemetry'];
  
  console.log('🔍 Validant fitxers de traducció...');
  
  let errors = 0;
  
  locales.forEach(locale => {
    namespaces.forEach(namespace => {
      const filePath = `i18n/locales/${locale}/${namespace}.json`;
      
      if (!fs.existsSync(filePath)) {
        console.error(`❌ Falta: ${filePath}`);
        errors++;
        return;
      }
      
      try {
        const content = fs.readFileSync(filePath, 'utf-8');
        JSON.parse(content);
        console.log(`✅ Vàlid: ${filePath}`);
      } catch (error) {
        console.error(`❌ JSON invàlid: ${filePath}`);
        errors++;
      }
    });
  });
  
  if (errors === 0) {
    console.log('🎉 Totes les traduccions són vàlides!');
  } else {
    console.error(`💥 Trobats ${errors} errors`);
    process.exit(1);
  }
};

validateTranslations();
