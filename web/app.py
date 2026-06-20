from fastapi import FastAPI, UploadFile, File
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi import Request
from markitdown import MarkItDown

import tempfile
import os

app = FastAPI(title="MarkItDown")

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
return templates.TemplateResponse(
"index.html",
{"request": request}
)

@app.post("/convert")
async def convert(file: UploadFile = File(…)):
suffix = os.path.splitext(file.filename)[1]

with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as temp:
    temp.write(await file.read())
    temp_path = temp.name
try:
    md = MarkItDown()
    result = md.convert(temp_path)
    return JSONResponse({
        "filename": file.filename,
        "markdown": result.text_content
    })
finally:
    if os.path.exists(temp_path):
        os.remove(temp_path)
