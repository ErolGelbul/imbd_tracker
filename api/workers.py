from uvicorn.workers import UvicornWorker


class MyUvicornWorker(UvicornWorker):
    CONFIG_KWARGS = {
        "log_config": "/home/denis/PycharmProjects/movie-tracker/logging.yaml",
    }