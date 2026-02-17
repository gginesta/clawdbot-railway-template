#!/usr/bin/env python3
"""
Process sensitive items review decisions.
Run with --generate to create the review file.
Run without arguments to process review decisions.
"""

import json
import re
import sys
from pathlib import Path
from collections import defaultdict

BASE_DIR = Path(__file__).parent.parent
OUTPUT_DIR = BASE_DIR / "processed-exports"
REVIEW_FILE = OUTPUT_DIR / "SENSITIVE_REVIEW.md"


def get_all_sensitive_items():
    """Collect all sensitive items from all JSON files."""
    items = []

    for source in ['chatgpt', 'claude', 'grok']:
        source_dir = OUTPUT_DIR / "ai-history" / source / "processed"
        if not source_dir.exists():
            continue

        for json_file in sorted(source_dir.glob("items-*.json")):
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                for item in data.get('items', []):
                    if item.get('sensitive'):
                        item['_source_file'] = str(json_file)
                        items.append(item)

    return items


def generate_review_file():
    """Generate the review markdown file."""
    items = get_all_sensitive_items()

    # Group by source and month
    by_source = defaultdict(list)
    for item in items:
        source = item.get('source', 'unknown')
        by_source[source].append(item)

    with open(REVIEW_FILE, 'w', encoding='utf-8') as f:
        f.write("# Sensitive Items Review\n\n")
        f.write("Mark each item by changing `[ ]` to one of:\n")
        f.write("- `[safe]` - Not actually sensitive, clear the flag\n")
        f.write("- `[keep]` - Sensitive but keep (for personal use only)\n")
        f.write("- `[delete]` - Remove from outputs entirely\n\n")
        f.write("After reviewing, run: `python scripts/process_sensitive_review.py`\n\n")
        f.write(f"**Total items to review: {len(items)}**\n\n")
        f.write("---\n\n")

        for source, source_items in sorted(by_source.items()):
            f.write(f"## {source.upper()} ({len(source_items)} items)\n\n")

            for item in source_items:
                item_id = item.get('id', 'unknown')
                item_type = item.get('type', 'unknown')
                content = item.get('content', '')[:150].replace('\n', ' ')
                context = item.get('context', '')[:50]
                date = item.get('sourceDate', '')[:10]

                f.write(f"### [ ] `{item_id[:8]}`\n")
                f.write(f"**Type:** {item_type} | **Date:** {date} | **Context:** {context}\n\n")
                f.write(f"> {content}...\n\n")

    print(f"Generated review file: {REVIEW_FILE}")
    print(f"Total sensitive items: {len(items)}")
    print("\nOpen this file in Obsidian or any text editor.")
    print("Mark each item as [safe], [keep], or [delete], then run this script again.")


def process_review_decisions():
    """Process the review file and apply decisions."""
    if not REVIEW_FILE.exists():
        print("Review file not found. Run with --generate first.")
        return

    with open(REVIEW_FILE, 'r', encoding='utf-8') as f:
        content = f.read()

    # Parse decisions: ### [decision] `item_id`
    pattern = r'### \[(safe|keep|delete)\] `([a-f0-9]+)`'
    decisions = {}
    for match in re.finditer(pattern, content, re.IGNORECASE):
        decision = match.group(1).lower()
        item_id_prefix = match.group(2)
        decisions[item_id_prefix] = decision

    if not decisions:
        print("No decisions found. Mark items as [safe], [keep], or [delete].")
        print("Example: ### [safe] `abc12345`")
        return

    print(f"Found {len(decisions)} decisions:")
    print(f"  - safe: {sum(1 for d in decisions.values() if d == 'safe')}")
    print(f"  - keep: {sum(1 for d in decisions.values() if d == 'keep')}")
    print(f"  - delete: {sum(1 for d in decisions.values() if d == 'delete')}")

    # Process each JSON file
    stats = {'safe': 0, 'keep': 0, 'delete': 0, 'unchanged': 0}

    for source in ['chatgpt', 'claude', 'grok']:
        source_dir = OUTPUT_DIR / "ai-history" / source / "processed"
        if not source_dir.exists():
            continue

        for json_file in source_dir.glob("items-*.json"):
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)

            modified = False
            new_items = []

            for item in data.get('items', []):
                item_id = item.get('id', '')
                item_id_prefix = item_id[:8]

                if item_id_prefix in decisions:
                    decision = decisions[item_id_prefix]

                    if decision == 'delete':
                        stats['delete'] += 1
                        modified = True
                        continue  # Skip this item (delete it)
                    elif decision == 'safe':
                        item['sensitive'] = False
                        stats['safe'] += 1
                        modified = True
                    elif decision == 'keep':
                        item['sensitive_reviewed'] = True
                        stats['keep'] += 1
                        modified = True
                else:
                    stats['unchanged'] += 1

                new_items.append(item)

            if modified:
                data['items'] = new_items
                with open(json_file, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=2, ensure_ascii=False)
                print(f"  Updated: {json_file.name}")

    print(f"\nProcessing complete:")
    print(f"  - Cleared sensitive flag: {stats['safe']}")
    print(f"  - Kept as sensitive: {stats['keep']}")
    print(f"  - Deleted: {stats['delete']}")
    print(f"  - Unchanged: {stats['unchanged']}")


def main():
    if len(sys.argv) > 1 and sys.argv[1] == '--generate':
        generate_review_file()
    else:
        # Check if review file has decisions, otherwise generate
        if not REVIEW_FILE.exists():
            generate_review_file()
        else:
            process_review_decisions()


if __name__ == "__main__":
    main()
