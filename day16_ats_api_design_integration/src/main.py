import uvicorn

from .api import app
from .logging_config import configure_logging


def main():
    configure_logging()

    uvicorn.run(
        app,
        host="127.0.0.1",
        port=8000,
        reload=False,
    )


if __name__ == "__main__":
    main()