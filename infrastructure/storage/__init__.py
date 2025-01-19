from utils.logs import logger


_query_logs_count = 0


def db_log(message, *args, **kwargs):
    global _query_logs_count
    logger.debug("[Neo4J#%d] " + message, _query_logs_count, *args, **kwargs)
    _query_logs_count += 1
