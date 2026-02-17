#!/usr/bin/env python3
"""
Improved extraction script for Memory Vault AI history.
Filters out truncated sentences, removes generic items,
and focuses on LESSONS and high-confidence DECISIONS.
"""

import json
import re
import os
from datetime import datetime
from pathlib import Path


def is_complete_sentence(text):
    """Check if text appears to be a complete sentence."""
    # Check if it ends with proper punctuation
    if not text.strip().endswith(('.', '!', '?', '."', '."')):
        return False
    
    # Check if it's likely truncated (too short or ends abruptly)
    words = text.split()
    if len(words) < 3:
        return False
    
    # Check for common truncation indicators
    if text.strip().endswith('...') or text.strip().endswith('…'):
        return False
        
    return True


def is_generic_item(text):
    """Check if item is generic/uninformative."""
    generic_patterns = [
        r'(?i)preference:\s*your help',
        r'(?i)help me with',
        r'(?i)can you help me',
        r'(?i)i need help',
        r'(?i)please assist',
        r'(?i)could you',
        r'(?i)would you',
        r'(?i)thank you',
        r'(?i)hello',
        r'(?i)hi there'
    ]
    
    for pattern in generic_patterns:
        if re.search(pattern, text):
            return True
    return False


def extract_project_tags(text):
    """Extract project tags from text."""
    tags = []
    project_names = ['brinc', 'cerebro', 'mana', 'tinker', 'master', 'personal']
    
    for name in project_names:
        if f'#{name}' in text.lower() or f' {name} ' in text.lower():
            tags.append(name)
    
    return tags


def categorize_content(text):
    """Categorize content as LESSON, DECISION, or OTHER."""
    text_lower = text.lower()
    
    lesson_indicators = ['lesson', 'learned', 'realized', 'discovered', 'found that', 'understood', 'insight', 'should ', 'need to', 'important to', 'key takeaway']
    decision_indicators = ['decided', 'will ', 'going to', 'chose', 'selected', 'picked', 'opted for', 'decision:', 'plan to', 'aim to']
    
    if any(indicator in text_lower for indicator in lesson_indicators):
        return 'LESSON'
    elif any(indicator in text_lower for indicator in decision_indicators):
        return 'DECISION'
    else:
        return 'OTHER'


def process_json_file(file_path):
    """Process a JSON file and extract quality facts."""
    print(f"Processing file: {file_path}")
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        extracted_items = []
        
        # Handle different possible structures
        if isinstance(data, list):
            items = data
        elif isinstance(data, dict) and 'items' in data:
            items = data['items']
        elif isinstance(data, dict) and 'conversations' in data:
            items = data['conversations']
        else:
            items = [data] if isinstance(data, dict) else []
        
        for item in items:
            # Extract text content depending on structure
            text_content = ""
            
            if isinstance(item, str):
                text_content = item
            elif isinstance(item, dict):
                # Try common keys where content might be stored
                text_content = (
                    item.get('text', '') or 
                    item.get('content', '') or 
                    item.get('message', '') or 
                    item.get('summary', '') or
                    str(item)
                )
            
            if not text_content.strip():
                continue
                
            # Filter for quality
            if not is_complete_sentence(text_content):
                continue
            
            if is_generic_item(text_content):
                continue
            
            # Categorize and tag
            category = categorize_content(text_content)
            tags = extract_project_tags(text_content)
            
            # Only keep medium or high confidence items (based on categorization)
            if category in ['LESSON', 'DECISION']:
                extracted_items.append({
                    'text': text_content,
                    'category': category,
                    'tags': tags,
                    'confidence': 'high' if category in ['LESSON', 'DECISION'] else 'medium',
                    'source_file': os.path.basename(file_path)
                })
        
        return extracted_items
    
    except Exception as e:
        print(f"Error processing {file_path}: {str(e)}")
        return []


def main():
    vault_path = Path('/data/shared/memory-vault')
    ai_history_path = vault_path / 'ai-history'
    
    if not ai_history_path.exists():
        print(f"AI history path does not exist: {ai_history_path}")
        return
    
    # Find all JSON files in the processed directories
    json_files = []
    for platform_dir in ai_history_path.iterdir():
        if platform_dir.is_dir():
            processed_dir = platform_dir / 'processed'
            if processed_dir.exists():
                json_files.extend(processed_dir.glob('items-*.json'))
    
    print(f"Found {len(json_files)} JSON files to process")
    
    all_extracted_items = []
    
    for json_file in json_files:
        items = process_json_file(json_file)
        all_extracted_items.extend(items)
    
    # Group by project tags
    grouped_items = {}
    for item in all_extracted_items:
        tags = item['tags'] or ['unassigned']
        for tag in tags:
            if tag not in grouped_items:
                grouped_items[tag] = []
            grouped_items[tag].append(item)
    
    # Write to output file
    output_date = datetime.now().strftime('%Y-%m-%d')
    output_path = vault_path / 'knowledge' / 'resources' / f'extraction-candidates-{output_date}.md'
    
    # Create directories if they don't exist
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(f"# Extraction Candidates - {datetime.now().strftime('%B %d, %Y')}\n\n")
        
        for tag, items in grouped_items.items():
            f.write(f"## {tag.title()} ({len(items)} items)\n\n")
            
            for i, item in enumerate(items, 1):
                f.write(f"{i}. **[{item['category']}]** {item['text']}\n")
                f.write(f"   - Source: `{item['source_file']}`\n")
                f.write(f"   - Confidence: {item['confidence']}\n\n")
    
    print(f"Extraction completed. Results saved to: {output_path}")
    print(f"Total items extracted: {len(all_extracted_items)}")
    print(f"Grouped by {len(grouped_items)} tags: {list(grouped_items.keys())}")


if __name__ == '__main__':
    main()