"""
성능 유틸리티 모듈: 캐싱, 타이밍 등 성능 관련 기능을 제공합니다.
"""
import functools
import time
from typing import Any, Callable, Dict, TypeVar
import logging

T = TypeVar('T')

def cache_with_ttl(ttl: int):
    """
    TTL 기반 캐싱 데코레이터
    
    Args:
        ttl: 캐시 유효 시간(초)
        
    Returns:
        Callable: 데코레이터 함수
    """
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        cache: Dict[str, Any] = {}
        cache_times: Dict[str, float] = {}
        
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> T:
            key = str(args) + str(kwargs)
            current_time = time.time()
            
            # 캐시에 있고 TTL이 지나지 않았으면 캐시된 값 반환
            if key in cache and current_time - cache_times[key] < ttl:
                return cache[key]
            
            # 캐시에 없거나 TTL이 지났으면 함수 실행 후 캐싱
            result = func(*args, **kwargs)
            cache[key] = result
            cache_times[key] = current_time
            return result
            
        return wrapper
    return decorator

def timing_decorator(func: Callable[..., T]) -> Callable[..., T]:
    """
    함수 실행 시간을 측정하는 데코레이터
    
    Args:
        func: 시간을 측정할 함수
        
    Returns:
        Callable: 데코레이터가 적용된 함수
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs) -> T:
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        
        elapsed_ms = (end_time - start_time) * 1000
        logging.getLogger(__name__).info(f"Function {func.__name__} took {elapsed_ms:.2f} ms to execute")
        
        return result
    return wrapper

def memory_usage_info() -> Dict[str, Any]:
    """
    현재 메모리 사용량 정보를 반환합니다.
    
    Returns:
        Dict[str, Any]: 메모리 사용량 정보
    """
    import psutil
    import os
    
    process = psutil.Process(os.getpid())
    memory_info = process.memory_info()
    
    return {
        'rss': memory_info.rss / (1024 * 1024),  # RSS in MB
        'vms': memory_info.vms / (1024 * 1024),  # VMS in MB
        'percent': process.memory_percent()
    }
