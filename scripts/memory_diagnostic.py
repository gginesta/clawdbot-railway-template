#!/usr/bin/env python3
import os
import sys
import json
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/data/workspace/logs/memory_diagnostic.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

def check_qmd_config():
    """Check QMD configuration in OpenClaw config."""
    try:
        with open('/data/.openclaw/openclaw.json', 'r') as f:
            config = json.load(f)
        
        qmd_config = config.get('memory', {}).get('qmd', {})
        logger.info("QMD Configuration:")
        for key, value in qmd_config.items():
            logger.info(f"{key}: {value}")
        
        return qmd_config
    except Exception as e:
        logger.error(f"Error reading QMD config: {e}")
        return None

def test_memory_search():
    """Test memory search functionality."""
    try:
        import subprocess
        
        # Test basic memory search
        test_queries = [
            "OpenClaw configuration",
            "PARA curation",
            "memory framework",
            "recent changes"
        ]
        
        logger.info("Running memory search tests...")
        for query in test_queries:
            logger.info(f"Searching for: '{query}'")
            result = subprocess.run(
                ['memory_search', query], 
                capture_output=True, 
                text=True, 
                timeout=10
            )
            
            logger.info(f"Search results for '{query}':")
            logger.info(result.stdout)
            
            if result.stderr:
                logger.warning(f"Stderr for '{query}': {result.stderr}")
    
    except Exception as e:
        logger.error(f"Memory search test failed: {e}")

def scan_memory_directories():
    """Scan memory directories for recent changes."""
    memory_dirs = [
        '/data/workspace/memory',
        '/data/workspace/memory/archive',
        '/data/.openclaw/memory'
    ]
    
    logger.info("Scanning memory directories...")
    for directory in memory_dirs:
        if not os.path.exists(directory):
            logger.warning(f"Directory not found: {directory}")
            continue
        
        logger.info(f"Scanning {directory}")
        for root, dirs, files in os.walk(directory):
            for file in files:
                full_path = os.path.join(root, file)
                try:
                    stat = os.stat(full_path)
                    modified = datetime.fromtimestamp(stat.st_mtime)
                    logger.info(f"File: {full_path}")
                    logger.info(f"  Modified: {modified}")
                    logger.info(f"  Size: {stat.st_size} bytes")
                except Exception as e:
                    logger.error(f"Error accessing {full_path}: {e}")

def main():
    logger.info("Starting Memory Diagnostic")
    
    check_qmd_config()
    test_memory_search()
    scan_memory_directories()
    
    logger.info("Memory Diagnostic Complete")

if __name__ == '__main__':
    main()