#!/usr/bin/env python3
"""
Script to explore the memory vault directory structure
"""

import os
from pathlib import Path

def explore_directory(path, prefix=''):
    """Recursively explore directory and print structure"""
    path = Path(path)
    
    if not path.exists():
        print(f"Directory does not exist: {path}")
        return
    
    print(f"{prefix}{path.name}/")
    prefix += "  "
    
    for item in sorted(path.iterdir()):
        if item.is_dir():
            print(f"{prefix}{item.name}/")
            explore_directory(item, prefix + "  ")
        else:
            print(f"{prefix}{item.name}")

# Explore the memory vault structure
print("Exploring /data/shared/memory-vault structure:")
explore_directory('/data/shared/memory-vault')