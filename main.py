import os
import tempfile
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import HTMLResponse, Response
from fastapi.concurrency import run_in_threadpool
from markitdown import MarkItDown

app = FastAPI()

HTML = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0">
<title>MarkItDown</title>
<style>
  *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
  :root {
    --bg: #0f0f0f; --surface: #1a1a1a; --surface2: #242424;
    --border: rgba(255,255,255,0.08); --text: #e8e8e8; --muted: #888;
    --accent: #4f98a3; --accent-hover: #3d7d87; --radius: 14px;
    --font: -apple-system, BlinkMacSystemFont, 'SF Pro Text', 'Segoe UI', sans-serif;
  }
  html, body { height: 100%; background: var(--bg); color: var(--text); font-family: var(--font); -webkit-font-smoothing: antialiased; }
  body { display: flex; flex-direction: column; align-items: center; justify-content: flex-start; min-height: 100dvh; padding: 48px 20px 40px; }
  .card { width: 100%; max-width: 390px; background: var(--surface); border: 1px solid var(--border); border-radius: var(--radius); padding: 28px 24px; display: flex; flex-direction: column; align-items: center; gap: 20px; }
  .logo { display: flex; align-items: center; gap: 10px; }
  h1 { font-size: 20px; font-weight: 600; letter-spacing: -0.3px; }
  .subtitle { font-size: 13px; color: var(--muted); text-align: center; }
  .drop-zone { width: 100%; border: 1.5px dashed rgba(79,152,163,0.35); border-radius: 10px; padding: 32px 20px; display: flex; flex-direction: column; align-items: center; gap: 10px; cursor: pointer; transition: border-color 0.2s, background 0.2s; background: var(--surface2); position: relative; }
  .drop-zone:active, .drop-zone.dragover { border-color: var(--accent); background: rgba(79,152,163,0.06); }
  .drop-zone input[type="file"] { position: absolute; inset: 0; opacity: 0; cursor: pointer; width: 100%; height: 100%; }
  .drop-icon { color: var(--accent); opacity: 0.8; }
  .drop-label { font-size: 14px; font-weight: 500; }
  .drop-hint { font-size: 12px; color: var(--muted); }
  .file-name { font-size: 13px; color: var(--accent); font-weight: 500; text-align: center; word-break: break-all; display: none; width: 100%; }
  .btn { width: 100%; background: var(--accent); color: #fff; border: none; border-radius: 10px; padding: 14px; font-size: 15px; font-weight: 600; cursor: pointer; transition: background 0.18s, transform 0.1s; -webkit-tap-highlight-color: transparent; display: flex; align-items: center; justify-content: center; gap: 8px; }
  .btn:active { background: var(--accent-hover); transform: scale(0.98); }
  .btn:disabled { opacity: 0.4; cursor: not-allowed; transform: none; }
  .spinner { display: none; width: 18px; height: 18px; border: 2px solid rgba(255,255,255,0.25); border-top-color: #fff; border-radius: 50%; animation: spin 0.7s linear infinite; }
  @keyframes spin { to { transform: rotate(360deg); } }
  .result-box { width: 100%; display: none; flex-direction: column; gap: 12px; }
  .result-header { display: flex; justify-content: space-between; align-items: center; }
  .result-label { font-size: 11px; font-weight: 700; text-transform: uppercase; letter-spacing: 0.7px; color: var(--muted); }
  .copy-btn { font-size: 13px; font-weight: 600; color: var(--accent); background: none; border: 1px solid rgba(79,152,163,0.3); border-radius: 7px; cursor: pointer; padding: 5px 12px; transition: background 0.15s; -webkit-tap-highlight-color: transparent; }
  .copy-btn:active { background: rgba(79,152,163,0.12); }
  textarea { width: 100%; min-height: 200px; background: var(--surface2); border: 1px solid var(--border); border-radius: 10px; color: var(--text); font-family: 'SF Mono', 'Menlo', monospace; font-size: 12px; line-height: 1.65; padding: 14px; resize: vertical; outline: none; -webkit-appearance: none; }
  textarea:focus { border-color: rgba(79,152,163,0.4); }
  .error { width: 100%; background: rgba(161,44,123,0.1); border: 1px solid rgba(161,44,123,0.25); border-radius: 10px; padding: 12px 14px; font-size: 13px; color: #d163a7; display: none; }
  .divider { width: 100%; height: 1px; background: var(--border); }
</style>
</head>
<body>
<div class="card">
  <div class="logo">
    <svg class="drop-icon" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
      <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/>
      <line x1="16" y1="13" x2="8" y2="13"/><line x1="16" y1="17" x2="8" y2="17"/>
    </svg>
    <h1>MarkItDown</h1>
  </div>
  <p class="subtitle">Convert any file to clean Markdown</p>
  <div class="divider"></div>

  <div class="drop-zone" id="dropZone">
    <input type="file" id="fileInput" accept="*/*">
    <svg class="drop-icon" width="34" height="34" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">
      <polyline points="16 16 12 12 8 16"/><line x1="12" y1="12" x2="12" y2="21"/>
      <path d="M20.39 18.39A5 5 0 0 0 18 9h-1.26A8 8 0 1 0 3 16.3"/>
    </svg>
    <span class="drop-label">Tap to choose a file</span>
    <span class="drop-hint">PDF · DOCX · PPTX · XLSX · images & more</span>
  </div>

  <p class="file-name" id="fileName"></p>

  <button class="btn" id="convertBtn" disabled onclick="convertFile()">
    <span id="btnText">Convert to Markdown</span>
    <div class="spinner" id="spinner"></div>
  </button>

  <div class="error" id="errorBox"></div>

  <div class="result-box" id="resultBox">
    <div class="divider"></div>
    <div class="result-header">
      <span class="result-label">Output</span>
      <button class="copy-btn" onclick="copyText()">Copy</button>
    </div>
    <textarea id="output" readonly></textarea>
  </div>
</div>

<script>
  const fileInput = document.getElementById('fileInput');
  const dropZone = document.getElementById('dropZone');
  const fileName = document.getElementById('fileName');
  const convertBtn = document.getElementById('convertBtn');
  const btnText = document.getElementById('btnText');
  const spinner = document.getElementById('spinner');
  const resultBox = document.getElementById('resultBox');
  const output = document.getElementById('output');
  const errorBox = document.getElementById('errorBox');

  fileInput.addEventListener('change', () => {
    if (fileInput.files[0]) {
      fileName.textContent = fileInput.files[0].name;
      fileName.style.display = 'block';
      convertBtn.disabled = false;
      resultBox.style.display = 'none';
      errorBox.style.display = 'none';
    }
  });

  dropZone.addEventListener('dragover', e => { e.preventDefault(); dropZone.classList.add('dragover'); });
  dropZone.addEventListener('dragleave', () => dropZone.classList.remove('dragover'));
  dropZone.addEventListener('drop', e => {
    e.preventDefault();
    dropZone.classList.remove('dragover');
    fileInput.files = e.dataTransfer.files;
    fileInput.dispatchEvent(new Event('change'));
  });

  async function convertFile() {
    const file = fileInput.files[0];
    if (!file) return;
    btnText.style.display = 'none';
    spinner.style.display = 'block';
    convertBtn.disabled = true;
    errorBox.style.display = 'none';
    resultBox.style.display = 'none';
    const form = new FormData();
    form.append('file', file);
    try {
      const res = await fetch('/convert', { method: 'POST', body: form });
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || 'Conversion failed');
      output.value = data.markdown;
      resultBox.style.display = 'flex';
      resultBox.scrollIntoView({ behavior: 'smooth', block: 'start' });
    } catch (e) {
      errorBox.textContent = e.message;
      errorBox.style.display = 'block';
    } finally {
      btnText.style.display = 'inline';
      spinner.style.display = 'none';
      convertBtn.disabled = false;
    }
  }

  function copyText() {
    navigator.clipboard.writeText(output.value).then(() => {
      const btn = document.querySelector('.copy-btn');
      btn.textContent = 'Copied!';
      setTimeout(() => btn.textContent = 'Copy', 2000);
    });
  }
</script>
</body>
</html>"""

@app.get("/", response_class=HTMLResponse)
async def index():
    return HTML

@app.get("/favicon.ico", include_in_schema=False)
async def favicon():
    return Response(status_code=204)

@app.post("/convert")
async def convert(file: UploadFile = File(...)):
    suffix = os.path.splitext(file.filename)[1] or ".tmp"
    tmp_path = None
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            tmp.write(await file.read())
            tmp_path = tmp.name
        md = MarkItDown()
        result = await run_in_threadpool(md.convert, tmp_path)
        return {"filename": file.filename, "markdown": result.text_content}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if tmp_path and os.path.exists(tmp_path):
            os.remove(tmp_path)
