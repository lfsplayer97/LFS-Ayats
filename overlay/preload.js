const { contextBridge } = require('electron');

contextBridge.exposeInMainWorld('electronOverlay', {
  platform: process.platform,
  electron: process.versions.electron,
});
