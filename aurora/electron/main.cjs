// Electron main process for Aurora Sunum (Windows desktop app).
const { app, BrowserWindow, shell, Menu } = require('electron')
const path = require('path')

// In dev you can point the window at the Vite dev server:
//   ELECTRON_START_URL=http://localhost:5173 electron .
const START_URL = process.env.ELECTRON_START_URL

function createWindow() {
  const win = new BrowserWindow({
    width: 1360,
    height: 860,
    minWidth: 1024,
    minHeight: 640,
    backgroundColor: '#07070c',
    autoHideMenuBar: true,
    show: false,
    title: 'Aurora Sunum',
    webPreferences: {
      contextIsolation: true,
      nodeIntegration: false,
      // Allow loading the bundled Google-free fonts / local assets.
      sandbox: true,
    },
  })

  // Remove the default application menu (cleaner, app-like feel).
  Menu.setApplicationMenu(null)

  if (START_URL) {
    win.loadURL(START_URL)
    win.webContents.openDevTools({ mode: 'detach' })
  } else {
    win.loadFile(path.join(__dirname, '..', 'dist', 'index.html'))
  }

  // Show only once content is ready to avoid a white flash.
  win.once('ready-to-show', () => win.show())

  // Open any external (http/https) links in the user's real browser, not the app.
  win.webContents.setWindowOpenHandler(({ url }) => {
    if (url.startsWith('http://') || url.startsWith('https://')) {
      shell.openExternal(url)
      return { action: 'deny' }
    }
    return { action: 'allow' }
  })

  // F11 / fullscreen friendliness for presenting.
  win.webContents.on('before-input-event', (event, input) => {
    if (input.key === 'F11' && input.type === 'keyDown') {
      win.setFullScreen(!win.isFullScreen())
      event.preventDefault()
    }
  })
}

app.whenReady().then(() => {
  createWindow()
  app.on('activate', () => {
    if (BrowserWindow.getAllWindows().length === 0) createWindow()
  })
})

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') app.quit()
})
