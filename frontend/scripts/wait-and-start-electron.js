import { spawn } from 'child_process';
import waitOn from 'wait-on';
import http from 'http';

// Helper function to check if server is ready
function checkServer(url) {
  return new Promise((resolve) => {
    const req = http.get(url, (res) => {
      resolve(res.statusCode === 200);
    });
    req.on('error', () => resolve(false));
    req.setTimeout(2000, () => {
      req.destroy();
      resolve(false);
    });
  });
}

const viteUrl = 'http://localhost:5173';

console.log('[Electron Launcher] Waiting for Vite dev server...');

// Poll until server is ready
async function waitForVite() {
  for (let i = 0; i < 60; i++) {
    const isReady = await checkServer(viteUrl);
    if (isReady) {
      console.log('[Electron Launcher] Vite is ready, starting Electron...');
      return true;
    }
    await new Promise(resolve => setTimeout(resolve, 500));
  }
  throw new Error('Vite server did not become ready in time');
}

waitForVite()
  .then(() => {
    const electron = spawn('electron', ['.'], {
      env: { ...process.env, VITE_DEV_SERVER_URL: viteUrl },
      stdio: 'inherit',
      shell: true,
    });
    
    electron.on('error', (err) => {
      console.error('[Electron Launcher] Failed to start Electron:', err);
      process.exit(1);
    });
    
    electron.on('exit', (code) => {
      if (code !== 0 && code !== null) {
        console.error(`[Electron Launcher] Electron exited with code ${code}`);
      }
    });
  })
  .catch((err) => {
    console.error('[Electron Launcher] Error waiting for Vite:', err);
    process.exit(1);
  });

