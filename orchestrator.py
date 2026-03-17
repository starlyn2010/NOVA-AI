import logging
import json
from functools import wraps
from contextlib import contextmanager
from typing import Callable, Any, Dict, TypeVar

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

T = TypeVar('T')

@contextmanager
def log_context(action: str) -> None:
    logger.info(f'Starting {action}')
    try:
        yield
    except Exception as e:
        logger.error(f'Error during {action}: {e}')
        raise
    finally:
        logger.info(f'Completed {action}')

def cache(func: Callable[..., T]) -> Callable[..., T]:
    cached_results: Dict[str, T] = {}

    @wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> T:
        key = json.dumps((args, kwargs))
        if key not in cached_results:
            logger.info(f'Calculating result for: {key}')
            cached_results[key] = func(*args, **kwargs)
        return cached_results[key]
    return wrapper

def validate_config(config: Dict[str, Any]) -> None:
    # Example validation logic
    if 'settings' not in config:
        raise ValueError('Invalid configuration: missing settings.')  

@cache
def process_data(data: Any) -> str:
    # Your data processing logic goes here
    # e.g., transform and return a result
    result = str(data)  # Simply convert to string for this example
    return result

if __name__ == '__main__':
    config = {'settings': {'param1': 'value1'}}  # Placeholder for actual config
    validate_config(config)

    with log_context('processing data'):
        try:
            data = {'key': 'value'}  # Sample input data
            result = process_data(data)
            logger.info(f'Processed result: {result}')
        except Exception as e:
            logger.error(f'Processing failed: {e}'),"message":"Updated orchestrator.py with comprehensive refactoring and improvements.","owner":"starlyn2010","path":"orchestrator.py","repo":"NOVA-AI","sha":"48edef4ada6bdc7cf94602d1454198469b911750"}