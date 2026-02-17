#!/usr/bin/env python3
import os
import sys
import json
import logging
from datetime import datetime, timedelta

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/data/workspace/logs/para_curation.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

def validate_file_size(path, max_kb=10):
    """Check if file size is within allowed limit."""
    try:
        size_kb = os.path.getsize(path) / 1024
        return size_kb <= max_kb
    except Exception as e:
        logger.error(f"File size check failed for {path}: {e}")
        return False

def contains_sensitive_info(content):
    """Basic check for sensitive information."""
    sensitive_patterns = [
        'api_key', 'password', 'secret', 'token', 
        'credentials', 'private', 'confidential'
    ]
    content_lower = content.lower()
    return any(pattern in content_lower for pattern in sensitive_patterns)

def migrate_content(source_path, dest_path):
    """
    Migrate content with validation and logging.
    
    Args:
        source_path (str): Source file path
        dest_path (str): Destination file path
    
    Returns:
        bool: Migration success status
    """
    try:
        # Read source
        with open(source_path, 'r') as f:
            content = f.read()
        
        # Validate content
        if contains_sensitive_info(content):
            logger.warning(f"Sensitive info detected in {source_path}. Migration aborted.")
            return False
        
        # Size check
        if not validate_file_size(source_path):
            logger.warning(f"File {source_path} exceeds size limit. Migration aborted.")
            return False
        
        # Create destination directory if not exists
        os.makedirs(os.path.dirname(dest_path), exist_ok=True)
        
        # Write to destination
        with open(dest_path, 'w') as f:
            f.write(content)
        
        logger.info(f"Successfully migrated {source_path} to {dest_path}")
        return True
    
    except Exception as e:
        logger.error(f"Migration failed for {source_path}: {e}")
        return False

def weekly_para_curation():
    """Main PARA curation workflow."""
    logger.info("Starting weekly PARA curation")
    
    # Define paths
    shared_projects_dir = '/data/shared/projects'
    memory_dir = '/data/workspace/memory'
    archive_dir = f'{memory_dir}/archive'
    
    # Ensure archive directory exists
    os.makedirs(archive_dir, exist_ok=True)
    
    # Scan and process files
    processed_files = []
    skipped_files = []
    
    try:
        for root, dirs, files in os.walk(shared_projects_dir):
            for file in files:
                if file.endswith('.md'):
                    full_path = os.path.join(root, file)
                    
                    # Archive old project files
                    file_age = datetime.now() - datetime.fromtimestamp(os.path.getmtime(full_path))
                    if file_age > timedelta(days=365):  # 1 year old
                        archive_path = os.path.join(archive_dir, os.path.relpath(full_path, shared_projects_dir))
                        
                        if migrate_content(full_path, archive_path):
                            processed_files.append(full_path)
                        else:
                            skipped_files.append(full_path)
        
        # Log results
        logger.info(f"PARA Curation Complete")
        logger.info(f"Processed Files: {len(processed_files)}")
        logger.info(f"Skipped Files: {len(skipped_files)}")
        
        # Optional: Create summary report
        report = {
            'timestamp': datetime.now().isoformat(),
            'processed_files': processed_files,
            'skipped_files': skipped_files
        }
        
        with open(f'{memory_dir}/para_curation_report.json', 'w') as f:
            json.dump(report, f, indent=2)
        
        return True
    
    except Exception as e:
        logger.error(f"PARA Curation failed: {e}")
        return False

def main():
    result = weekly_para_curation()
    sys.exit(0 if result else 1)

if __name__ == '__main__':
    main()