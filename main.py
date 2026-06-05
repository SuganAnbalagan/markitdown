import os
import tempfile
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.concurrency import run_in_threadpool
from markitdown import MarkItDown

app = FastAPI()

@app.get("/", response_class=HTMLResponse)
async def index():
    return """
    <html><body>
    <h2>MarkItDown Converter</h2>
    <form action="/convert" method="post" enctype="multipart/form-data">
        <input type="file" name="file" required>
        <button type="submit">Convert to Markdown</button>
    </form>
    </body></html>
    """

@app.post("/convert")
async def convert(file: UploadFile = File(...)):
    suffix = os.path.splitext(file.filename)[1] or ".tmp"
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
        if os.path.exists(tmp_path):
            os.remove(tmp_path)
