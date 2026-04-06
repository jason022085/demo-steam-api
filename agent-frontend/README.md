# Agent 前端應用 (React + TypeScript + Vite)

這是一個使用 React、TypeScript 和 Vite 建立的前端專案，主要作為 Agent API (Server-Sent Events) 的圖形化使用者介面。

本專案提供了一個極簡的設定，讓 React 可以在 Vite 環境中運行，並包含 HMR (熱模組替換) 與一些 ESLint 規則。

目前提供兩個官方外掛：

- [@vitejs/plugin-react](https://github.com/vitejs/vite-plugin-react/blob/main/packages/plugin-react) 使用 [Oxc](https://oxc.rs) 進行編譯
- [@vitejs/plugin-react-swc](https://github.com/vitejs/vite-plugin-react/blob/main/packages/plugin-react-swc) 使用 [SWC](https://swc.rs/) 進行編譯

## 🚀 快速啟動

本應用程式包含前端 (React) 與後端 (Python FastAPI) 兩部分，為了讓應用程式正常運作，請分別啟動兩者。

### 1. 啟動後端 API (FastAPI)

請開啟一個終端機視窗，前往上一層的專案根目錄 (`demo-steam-api`)：

```bash
# 安裝 Python 依賴項 (只需執行一次)
pip install -r requirements.txt

# 啟動 FastAPI 伺服器
python stream_api.py
```
> 後端伺服器預設會運行在 `http://127.0.0.1:8000`。

### 2. 啟動前端介面 (React)

請開啟另一個終端機視窗，並確保位於 `agent-frontend` 目錄下：

1. **安裝依賴套件**
   請確保你已經安裝了 Node.js。執行：
   ```bash
   npm install
   ```

2. **啟動開發伺服器**
   ```bash
   npm run dev
   ```
   啟動後，請開啟瀏覽器並前往 `http://localhost:5173` 即可預覽並與 API 進行互動。

3. **建置正式環境版本**
   ```bash
   npm run build
   ```
   建置完成的檔案會輸出到 `dist` 資料夾。

## 擴展 ESLint 設定

如果你正在開發正式環境的應用程式，我們建議更新設定以啟用基於型別的 lint 規則：

```js
// eslint.config.js
export default defineConfig([
  globalIgnores(['dist']),
  {
    files: ['**/*.{ts,tsx}'],
    extends: [
      // 其他設定...

      // 移除 tseslint.configs.recommended 並替換為以下設定
      tseslint.configs.recommendedTypeChecked,
      // 或者使用這個以啟用更嚴格的規則
      tseslint.configs.strictTypeChecked,
      // (選擇性) 加入樣式規則
      tseslint.configs.stylisticTypeChecked,

      // 其他設定...
    ],
    languageOptions: {
      parserOptions: {
        project: ['./tsconfig.node.json', './tsconfig.app.json'],
        tsconfigRootDir: import.meta.dirname,
      },
      // 其他選項...
    },
  },
])
```

你也可以安裝 [eslint-plugin-react-x](https://github.com/Rel1cx/eslint-react/tree/main/packages/plugins/eslint-plugin-react-x) 和 [eslint-plugin-react-dom](https://github.com/Rel1cx/eslint-react/tree/main/packages/plugins/eslint-plugin-react-dom) 來取得 React 專用的 lint 規則：

```js
// eslint.config.js
import reactX from 'eslint-plugin-react-x'
import reactDom from 'eslint-plugin-react-dom'

export default defineConfig([
  globalIgnores(['dist']),
  {
    files: ['**/*.{ts,tsx}'],
    extends: [
      // 其他設定...
      // 啟用 React lint 規則
      reactX.configs['recommended-typescript'],
      // 啟用 React DOM lint 規則
      reactDom.configs.recommended,
    ],
    languageOptions: {
      parserOptions: {
        project: ['./tsconfig.node.json', './tsconfig.app.json'],
        tsconfigRootDir: import.meta.dirname,
      },
      // 其他選項...
    },
  },
])
```
