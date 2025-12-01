import { contextBridge, ipcRenderer } from "electron";

contextBridge.exposeInMainWorld("electron", {
  setIgnoreMouseEvents: (ignore: boolean, options?: { forward: boolean }) => {
    ipcRenderer.invoke("set-ignore-mouse-events", ignore, options);
  },
  moveWindow: (deltaX: number, deltaY: number) => {
    ipcRenderer.invoke("move-window", deltaX, deltaY);
  },
});

