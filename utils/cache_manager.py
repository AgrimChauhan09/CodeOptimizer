import hashlib
import json
import os
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class OptimizationCache:
    def __init__(self):
        self.cache_file = "dataset/optimization_cache.json"
        self.cache = self._load_cache()
    
    def _load_cache(self):
        """Load existing cache from file"""
        if os.path.exists(self.cache_file):
            try:
                with open(self.cache_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                logger.warning(f"Failed to load cache: {str(e)}")
        return {}
    
    def _save_cache(self):
        """Save cache to file"""
        try:
            os.makedirs(os.path.dirname(self.cache_file), exist_ok=True)
            with open(self.cache_file, 'w') as f:
                json.dump(self.cache, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save cache: {str(e)}")
    
    def _get_code_hash(self, code):
        """Generate hash for the C code"""
        normalized_code = self._normalize_code(code)
        return hashlib.md5(normalized_code.encode()).hexdigest()
    
    def _normalize_code(self, code):
        """Normalize code by removing comments and extra whitespace"""
        lines = []
        for line in code.split('\n'):
            # Remove comments
            if '//' in line:
                line = line[:line.index('//')]
            # Remove extra whitespace
            line = line.strip()
            if line:
                lines.append(line)
        return '\n'.join(lines)
    
    def get_cached_result(self, code):
        """Get cached optimization result for code"""
        code_hash = self._get_code_hash(code)
        if code_hash in self.cache:
            cached_result = self.cache[code_hash]
            logger.info(f"Found cached result for code hash: {code_hash}")
            return cached_result
        return None
    
    def cache_result(self, code, result):
        """Cache optimization result"""
        code_hash = self._get_code_hash(code)
        
        # Add timestamp and ensure consistent format
        cache_entry = {
            'result': result,
            'timestamp': datetime.now().isoformat(),
            'code_hash': code_hash
        }
        
        self.cache[code_hash] = cache_entry
        self._save_cache()
        logger.info(f"Cached result for code hash: {code_hash}")
    
    def is_code_already_optimized(self, code):
        """Check if code has been optimized before"""
        return self.get_cached_result(code) is not None
    
    def get_cache_stats(self):
        """Get cache statistics"""
        return {
            'total_cached_codes': len(self.cache),
            'cache_file_exists': os.path.exists(self.cache_file)
        }