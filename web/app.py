from fastapi import FastAPI, UploadFile, File
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from markitdown import MarkItDown

import tempfile
import os
import time

app = FastAPI(title="MarkItDown")

app.mount("/static", StaticFiles(directory="static"), name="static")


@app.api_route("/", methods=["GET", "HEAD"])
async def home():
    return FileResponse("templates/index.html")


@app.post("/convert")
async def convert(file: UploadFile = File(...)):
    start = time.time()

    suffix = os.path.splitext(file.filename)[1]

    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as temp:
        temp.write(await file.read())
        temp_path = temp.name

    try:
        md = MarkItDown()
        result = md.convert(temp_path)

        markdown = getattr(
            result,
            "text_content",
            str(result)
        )

        elapsed = round(time.time() - start, 2)

        return JSONResponse(
            {
                "success": True,
                "filename": file.filename,
                "markdown": markdown,
                "conversion_time": elapsed
            }
        )

    except Exception as e:
        return JSONResponse(
            {
                "success": False,
                "error": str(e)
            },
            status_code=500
        )

    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)