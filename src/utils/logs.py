from logging import INFO, Logger, StreamHandler, getLogger


def default_module_logger(src_file_name: str) -> Logger:

    logger = getLogger(src_file_name)
    if len(logger.handlers) == 0:
        handler = StreamHandler()
        logger.addHandler(handler)
    logger.setLevel(INFO)

    return logger
