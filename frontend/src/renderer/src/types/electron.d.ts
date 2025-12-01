export interface ElectronAPI {
  setIgnoreMouseEvents: (ignore: boolean, options?: { forward: boolean }) => Promise<void>;
  moveWindow: (deltaX: number, deltaY: number) => Promise<void>;
}

declare global {
  interface Window {
    electron?: ElectronAPI;
  }
}

