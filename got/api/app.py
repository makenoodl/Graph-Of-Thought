from fastapi import FastAPI

from got.api.routes.analyze_text import router as analyze_text_router


def create_app() -> FastAPI:
    app = FastAPI(title="Graph-of-Thought API", version="0.1.0")
    app.include_router(analyze_text_router)
    return app


app = create_app()