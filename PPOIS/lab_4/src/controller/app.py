from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pathlib import Path
from src.controller.api.routes import router
from src.controller.exception import register_exception_handlers


def create_app() -> FastAPI:
    app = FastAPI(title="Virtual department", version="0.1.0")
    app.include_router(router)
    register_exception_handlers(app)

    static_dir = Path(__file__).resolve().parent.parent.parent / "static"
    if static_dir.exists():
        app.mount("/static", StaticFiles(directory=static_dir), name="static")

    @app.get("/")
    def index():
        index_file = static_dir / "index.html"
        if index_file.exists():
            return FileResponse(index_file)
        return {"message": "Virtual department API"}

    return app


app = create_app()
