import { app, BrowserWindow, Menu, nativeTheme, ipcMain } from "electron";
import path from "path";
import url from "url";
import { fileURLToPath } from "url";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const isDev = !!process.env.VITE_DEV_SERVER_URL;
let mainWindow: BrowserWindow | null = null;

const createWindow = async () => {
  console.log("[Electron] Creating window...");
  mainWindow = new BrowserWindow({
    width: 500,
    height: 700,
    minWidth: 400,
    minHeight: 500,
    frame: false,
    transparent: true,
    backgroundColor: "#00000000",
    alwaysOnTop: true,
    resizable: true,
    movable: true,
    show: false,
    webPreferences: {
      preload: path.join(__dirname, isDev ? "preload.js" : "preload.js"),
      contextIsolation: true,
      nodeIntegration: false
    }
  });

  mainWindow.once("ready-to-show", () => {
    console.log("[Electron] Window ready to show");
    mainWindow?.show();
  });
  
  // IPC handlers for window control
  ipcMain.handle("set-ignore-mouse-events", (event, ignore, options) => {
    if (mainWindow) {
      mainWindow.setIgnoreMouseEvents(ignore, options);
    }
  });
  
  ipcMain.handle("move-window", (event, deltaX, deltaY) => {
    if (mainWindow) {
      const [x, y] = mainWindow.getPosition();
      mainWindow.setPosition(x + deltaX, y + deltaY);
    }
  });

  if (isDev && process.env.VITE_DEV_SERVER_URL) {
    await mainWindow.loadURL(process.env.VITE_DEV_SERVER_URL);
    mainWindow.webContents.openDevTools({ mode: "detach" });
  } else {
    const indexPath = url.pathToFileURL(
      path.join(__dirname, "../renderer/index.html")
    ).toString();
    await mainWindow.loadURL(indexPath);
  }
};

app.whenReady().then(async () => {
  console.log("[Electron] App is ready");
  Menu.setApplicationMenu(null);
  nativeTheme.themeSource = "dark";
  await createWindow();

  app.on("activate", async () => {
    if (BrowserWindow.getAllWindows().length === 0) {
      await createWindow();
    }
  });
});

app.on("window-all-closed", () => {
  if (process.platform !== "darwin") {
    app.quit();
  }
});


