from utils.logs import logger


_query_logs_count = 0

DB_LOGGING = False


def db_log(message, *args, **kwargs):
    if not DB_LOGGING:
        return
    global _query_logs_count
    logger.debug("[Neo4J#%d] " + message, _query_logs_count, *args, **kwargs)
    _query_logs_count += 1
