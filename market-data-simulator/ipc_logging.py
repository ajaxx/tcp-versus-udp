import logging
import logging.handlers

def configure(args):
    if 'debug' in args and args.debug:
        logging_level = logging.DEBUG
    elif 'log_level' in args and not args.log_level is None:
        logging_level = getattr(logging, args.log_level.upper())
    else:
        logging_level = logging.INFO

    logging_handlers = None
    if args.log is not None:
        logging_handlers = [
            logging.handlers.RotatingFileHandler(args.log),
            logging.StreamHandler(),
        ]

    logging.basicConfig(level=logging_level, handlers=logging_handlers)