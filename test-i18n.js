import { translator } from './i18n/utils/translator.js';

console.log('🧪 Provant sistema i18n...');

// Provar càrrega de traduccions
await translator.loadNamespace('common');
await translator.loadNamespace('telemetry');

console.log('📝 Proves en català:');
await translator.changeLanguage('ca');
console.log('App name:', translator.t('app.name'));
console.log('Start action:', translator.t('actions.start'));
console.log('Connection status:', translator.t('telemetry.connection.status.connected'));
console.log('Channels with params:', translator.t('telemetry.data.channels', { count: 5 }));

console.log('📝 Proves en anglès:');
await translator.changeLanguage('en');
console.log('App name:', translator.t('app.name'));
console.log('Start action:', translator.t('actions.start'));
console.log('Connection status:', translator.t('telemetry.connection.status.connected'));
console.log('Channels with params:', translator.t('telemetry.data.channels', { count: 5 }));

console.log('✅ Proves completades!');
