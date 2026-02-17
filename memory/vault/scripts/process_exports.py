#!/usr/bin/env python3
"""
Process AI Conversation Exports for Memory Vault
Extracts valuable knowledge from ChatGPT, Claude, and Grok exports.
"""

import json
import os
import re
import uuid
from datetime import datetime
from pathlib import Path
from collections import defaultdict
from typing import Optional

# Configuration
BASE_DIR = Path(__file__).parent.parent
AI_BACKUP_DIR = BASE_DIR / "AI Backup"
OUTPUT_DIR = BASE_DIR / "processed-exports"

# File paths for each source
CHATGPT_FILE = AI_BACKUP_DIR / "25c2f2a764c3a34eef5ea4b6c3d2f7fe3007911f242994fa68ab9abe48159f5d-2026-02-01-12-19-40-bbaeae2d634640468510e1331b01122a (1)" / "conversations.json"
GROK_FILE = AI_BACKUP_DIR / "5b00e771-cf0a-4ce2-8d42-eb5c5c0f007f" / "ttl" / "30d" / "export_data" / "6f8c4a19-66f6-4907-9b97-9b120300a801" / "prod-grok-backend.json"
CLAUDE_FILE = AI_BACKUP_DIR / "data-2026-02-01-12-23-20-batch-0000" / "conversations.json"

# Known projects for categorization (order matters - more specific first)
PROJECTS = {
    "mana": ["mana capital", "solartia", "difako", "capital call", "private equity", "lbo", "leveraged buyout"],
    "cerebro": ["cerebro"],
    "tinker": ["tinker labs", "tinker lab"],
    "brinc": ["brinc", "accelerator program", "ndc philippines", "national development"],
    "master": ["molty", "openclaw", "claude code", "ai assistant"],
    "personal": ["fitness", "family trip", "health", "airbnb", "renovation", "personal travel"],
}

# Sensitive content patterns - only flag ACTUAL sensitive data, not mentions
SENSITIVE_PATTERNS = [
    # Actual credential patterns (keys, tokens with values)
    r'(?:api[_\s]?key|secret[_\s]?key|access[_\s]?token|bearer)\s*[:=]\s*["\']?[a-zA-Z0-9_\-]{20,}',
    r'sk-[a-zA-Z0-9]{20,}',  # OpenAI keys
    r'ghp_[a-zA-Z0-9]{20,}',  # GitHub tokens
    r'(?:password|pwd)\s*[:=]\s*["\']?[^\s"\']{6,}',  # Actual passwords with values

    # Personal ID numbers (actual numbers, not just mentions)
    r'\b\d{3}[-\s]?\d{2}[-\s]?\d{4}\b',  # SSN format
    r'passport\s*(?:number|#|no\.?)?\s*[:=]?\s*[A-Z0-9]{6,}',  # Passport with number

    # Financial account numbers
    r'(?:account|acct)\s*(?:number|#|no\.?)?\s*[:=]?\s*\d{8,}',  # Account numbers
    r'\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b',  # Credit card format
    r'(?:routing|aba)\s*(?:number|#)?\s*[:=]?\s*\d{9}',  # Routing numbers

    # Private keys (actual key content)
    r'-----BEGIN\s+(?:RSA\s+)?PRIVATE\s+KEY-----',
    r'-----BEGIN\s+OPENSSH\s+PRIVATE\s+KEY-----',
]


class ConversationProcessor:
    """Base class for processing conversations from different platforms."""

    def __init__(self, source: str):
        self.source = source
        self.items = []
        self.summaries = defaultdict(list)  # month -> list of conversation summaries
        self.stats = {
            "total": 0,
            "processed": 0,
            "skipped": 0,
            "items_extracted": 0,
            "sensitive_flagged": 0
        }

    def is_trivial(self, title: str, messages: list) -> bool:
        """Check if a conversation is too trivial to process."""
        # Skip very short conversations
        if len(messages) < 3:
            return True

        # Skip export/test conversations
        trivial_patterns = [
            r'^export', r'^test', r'^hello$', r'^hi$', r'^hey$',
            r'^\s*$', r'^untitled', r'^new chat'
        ]
        title_lower = title.lower() if title else ""
        for pattern in trivial_patterns:
            if re.match(pattern, title_lower):
                return True

        # Calculate total text length
        total_text = sum(len(m.get('content', '')) for m in messages)
        if total_text < 100:
            return True

        return False

    def detect_sensitive(self, text: str) -> bool:
        """Check if text contains sensitive information."""
        text_lower = text.lower()
        for pattern in SENSITIVE_PATTERNS:
            if re.search(pattern, text_lower):
                return True
        return False

    def categorize(self, title: str, content: str) -> tuple[str, list[str]]:
        """Determine which project/area this conversation relates to."""
        combined = f"{title} {content}".lower()

        matches = []
        for project, keywords in PROJECTS.items():
            for keyword in keywords:
                if keyword in combined:
                    matches.append(project)
                    break

        if matches:
            return matches[0], matches
        return "general", []

    def extract_insights(self, messages: list, title: str) -> list[dict]:
        """Extract insights from conversation messages."""
        insights = []
        full_text = "\n".join([m.get('content', '') for m in messages])

        # Get date from first message
        source_date = messages[0].get('timestamp', datetime.now().isoformat())
        is_sensitive = self.detect_sensitive(full_text)
        category, related = self.categorize(title, full_text)

        # Look for decision patterns
        decision_patterns = [
            r"(?:decided|decision|chose|choosing|went with|going with|settled on|picked)\s+(?:to\s+)?([^.!?\n]+)",
            r"(?:let'?s|we'?ll|I'?ll)\s+(?:go with|use|try)\s+([^.!?\n]+)",
        ]
        for pattern in decision_patterns:
            matches = re.findall(pattern, full_text, re.IGNORECASE)
            for match in matches[:2]:  # Limit to 2 per pattern
                if len(match) > 20:  # Meaningful content
                    insights.append({
                        "id": str(uuid.uuid4()),
                        "type": "decision",
                        "content": f"Decided: {match.strip()[:200]}",
                        "context": title,
                        "source": self.source,
                        "sourceDate": source_date,
                        "confidence": "medium",
                        "tags": [category],
                        "relatedTo": related,
                        "sensitive": is_sensitive,
                        "extractedAt": datetime.now().isoformat()
                    })

        # Look for lesson/insight patterns
        lesson_patterns = [
            r"(?:learned|realized|discovered|found out|turns out)\s+(?:that\s+)?([^.!?\n]+)",
            r"(?:key\s+(?:insight|takeaway|lesson)|important\s+(?:thing|point))(?:\s+is)?:?\s*([^.!?\n]+)",
        ]
        for pattern in lesson_patterns:
            matches = re.findall(pattern, full_text, re.IGNORECASE)
            for match in matches[:2]:
                if len(match) > 20:
                    insights.append({
                        "id": str(uuid.uuid4()),
                        "type": "lesson",
                        "content": f"Learned: {match.strip()[:200]}",
                        "context": title,
                        "source": self.source,
                        "sourceDate": source_date,
                        "confidence": "medium",
                        "tags": [category],
                        "relatedTo": related,
                        "sensitive": is_sensitive,
                        "extractedAt": datetime.now().isoformat()
                    })

        # Look for preference patterns
        preference_patterns = [
            r"(?:I\s+(?:prefer|like|love|hate|dislike|want|need))\s+([^.!?\n]+)",
            r"(?:my\s+(?:preference|favorite|style))\s+(?:is|would be)\s+([^.!?\n]+)",
        ]
        for pattern in preference_patterns:
            matches = re.findall(pattern, full_text, re.IGNORECASE)
            for match in matches[:2]:
                if len(match) > 10:
                    insights.append({
                        "id": str(uuid.uuid4()),
                        "type": "preference",
                        "content": f"Preference: {match.strip()[:200]}",
                        "context": title,
                        "source": self.source,
                        "sourceDate": source_date,
                        "confidence": "medium",
                        "tags": [category],
                        "relatedTo": related,
                        "sensitive": is_sensitive,
                        "extractedAt": datetime.now().isoformat()
                    })

        # Look for technique/how-to patterns
        technique_patterns = [
            r"(?:here'?s?\s+how|the\s+way\s+to|steps?\s+to|to\s+do\s+this)[:\s]+([^.!?\n]+)",
            r"(?:you\s+can|you\s+should|try\s+(?:using|this))[:\s]+([^.!?\n]+)",
        ]
        for pattern in technique_patterns:
            matches = re.findall(pattern, full_text, re.IGNORECASE)
            for match in matches[:2]:
                if len(match) > 20:
                    insights.append({
                        "id": str(uuid.uuid4()),
                        "type": "technique",
                        "content": f"Technique: {match.strip()[:200]}",
                        "context": title,
                        "source": self.source,
                        "sourceDate": source_date,
                        "confidence": "medium",
                        "tags": [category],
                        "relatedTo": related,
                        "sensitive": is_sensitive,
                        "extractedAt": datetime.now().isoformat()
                    })

        # Look for idea/plan patterns
        idea_patterns = [
            r"(?:idea|plan|goal|want to|going to|will)\s+(?:is\s+)?(?:to\s+)?([^.!?\n]+)",
            r"(?:might|could|should)\s+(?:try|consider|look into)\s+([^.!?\n]+)",
        ]
        for pattern in idea_patterns:
            matches = re.findall(pattern, full_text, re.IGNORECASE)
            for match in matches[:1]:  # Ideas can be noisy, limit to 1
                if len(match) > 20:
                    insights.append({
                        "id": str(uuid.uuid4()),
                        "type": "idea",
                        "content": f"Idea: {match.strip()[:200]}",
                        "context": title,
                        "source": self.source,
                        "sourceDate": source_date,
                        "confidence": "low",
                        "tags": [category],
                        "relatedTo": related,
                        "sensitive": is_sensitive,
                        "extractedAt": datetime.now().isoformat()
                    })

        if is_sensitive:
            self.stats["sensitive_flagged"] += len(insights)

        return insights

    def generate_conversation_summary(self, title: str, date: str, messages: list, insights: list) -> dict:
        """Generate a summary for a single conversation."""
        # Get user messages for context
        user_messages = [m['content'] for m in messages if m.get('role') == 'user'][:3]
        summary_text = " | ".join([msg[:100] for msg in user_messages])

        category, related = self.categorize(title, summary_text)

        return {
            "title": title,
            "date": date,
            "summary": summary_text[:300] if summary_text else "No summary available",
            "insights_count": len(insights),
            "category": category,
            "related": related,
            "sensitive": any(i.get('sensitive') for i in insights)
        }

    def write_outputs(self):
        """Write all outputs to files."""
        output_base = OUTPUT_DIR / "ai-history" / self.source / "processed"

        # Group items by month
        items_by_month = defaultdict(list)
        for item in self.items:
            try:
                date = datetime.fromisoformat(item['sourceDate'].replace('Z', '+00:00'))
                month_key = date.strftime("%Y-%m")
            except:
                month_key = "unknown"
            items_by_month[month_key].append(item)

        # Write monthly JSON files
        for month, month_items in items_by_month.items():
            json_file = output_base / f"items-{month}.json"
            with open(json_file, 'w', encoding='utf-8') as f:
                json.dump({"items": month_items}, f, indent=2, ensure_ascii=False)
            print(f"  Written: {json_file.name} ({len(month_items)} items)")

        # Write monthly summary files
        for month, convos in self.summaries.items():
            md_file = output_base / f"summary-{month}.md"
            with open(md_file, 'w', encoding='utf-8') as f:
                f.write(f"# {self.source.title()} Conversations Summary - {month}\n\n")
                f.write(f"## Overview\n")
                f.write(f"Processed {len(convos)} conversations this month.\n\n")

                # Group by category
                by_category = defaultdict(list)
                for c in convos:
                    by_category[c['category']].append(c)

                f.write("## Key Themes\n")
                for cat, items in by_category.items():
                    f.write(f"- {cat.title()}: {len(items)} conversations\n")
                f.write("\n")

                f.write("## Notable Conversations\n\n")
                for conv in convos[:20]:  # Limit to 20 per month
                    sensitive_flag = " [SENSITIVE]" if conv.get('sensitive') else ""
                    f.write(f"### {conv['title']}{sensitive_flag}\n")
                    f.write(f"**Date:** {conv['date']}\n")
                    f.write(f"**Summary:** {conv['summary']}\n")
                    if conv['insights_count'] > 0:
                        f.write(f"**Insights extracted:** {conv['insights_count']}\n")
                    if conv['related']:
                        f.write(f"**Related to:** {', '.join(conv['related'])}\n")
                    f.write("\n---\n\n")

            print(f"  Written: {md_file.name}")

    def print_stats(self):
        """Print processing statistics."""
        print(f"\n{self.source.upper()} Processing Complete:")
        print(f"  Total conversations: {self.stats['total']}")
        print(f"  Processed: {self.stats['processed']}")
        print(f"  Skipped (trivial): {self.stats['skipped']}")
        print(f"  Items extracted: {self.stats['items_extracted']}")
        print(f"  Sensitive flagged: {self.stats['sensitive_flagged']}")


class ChatGPTProcessor(ConversationProcessor):
    """Process ChatGPT exports."""

    def __init__(self):
        super().__init__("chatgpt")

    def extract_messages(self, mapping: dict) -> list[dict]:
        """Extract messages from ChatGPT's tree structure."""
        messages = []

        def traverse(node_id):
            if node_id not in mapping:
                return
            node = mapping[node_id]
            msg = node.get('message')
            if msg and msg.get('content', {}).get('parts'):
                parts = msg['content']['parts']
                content = ' '.join([p for p in parts if isinstance(p, str)])
                if content.strip():
                    messages.append({
                        'role': msg.get('author', {}).get('role', 'unknown'),
                        'content': content,
                        'timestamp': msg.get('create_time')
                    })
            for child_id in node.get('children', []):
                traverse(child_id)

        # Find root and traverse
        for node_id, node in mapping.items():
            if node.get('parent') is None:
                traverse(node_id)
                break

        return messages

    def process(self):
        """Process all ChatGPT conversations."""
        print(f"\nProcessing ChatGPT conversations from {CHATGPT_FILE}...")

        with open(CHATGPT_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)

        self.stats['total'] = len(data)

        for conv in data:
            title = conv.get('title', 'Untitled')
            create_time = conv.get('create_time', 0)
            mapping = conv.get('mapping', {})

            # Extract messages
            messages = self.extract_messages(mapping)

            # Skip trivial
            if self.is_trivial(title, messages):
                self.stats['skipped'] += 1
                continue

            self.stats['processed'] += 1

            # Format date
            try:
                date = datetime.fromtimestamp(create_time)
                date_str = date.strftime("%Y-%m-%d")
                month_key = date.strftime("%Y-%m")
            except:
                date_str = "unknown"
                month_key = "unknown"

            # Add timestamp to messages
            for msg in messages:
                if not msg.get('timestamp'):
                    msg['timestamp'] = date_str
                elif isinstance(msg['timestamp'], (int, float)):
                    msg['timestamp'] = datetime.fromtimestamp(msg['timestamp']).isoformat()

            # Extract insights
            insights = self.extract_insights(messages, title)
            self.items.extend(insights)
            self.stats['items_extracted'] += len(insights)

            # Generate summary
            summary = self.generate_conversation_summary(title, date_str, messages, insights)
            self.summaries[month_key].append(summary)

        self.write_outputs()
        self.print_stats()


class GrokProcessor(ConversationProcessor):
    """Process Grok exports."""

    def __init__(self):
        super().__init__("grok")

    def process(self):
        """Process all Grok conversations."""
        print(f"\nProcessing Grok conversations from {GROK_FILE}...")

        with open(GROK_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)

        conversations = data.get('conversations', [])
        self.stats['total'] = len(conversations)

        for conv_data in conversations:
            conv = conv_data.get('conversation', {})
            responses = conv_data.get('responses', [])

            title = conv.get('title', 'Untitled')
            create_time = conv.get('create_time', '')

            # Extract messages
            messages = []
            for resp_data in responses:
                resp = resp_data.get('response', {})
                messages.append({
                    'role': 'user' if resp.get('sender') == 'human' else 'assistant',
                    'content': resp.get('message', ''),
                    'timestamp': create_time
                })

            # Skip trivial
            if self.is_trivial(title, messages):
                self.stats['skipped'] += 1
                continue

            self.stats['processed'] += 1

            # Format date
            try:
                date = datetime.fromisoformat(create_time.replace('Z', '+00:00'))
                date_str = date.strftime("%Y-%m-%d")
                month_key = date.strftime("%Y-%m")
            except:
                date_str = "unknown"
                month_key = "unknown"

            # Extract insights
            insights = self.extract_insights(messages, title)
            self.items.extend(insights)
            self.stats['items_extracted'] += len(insights)

            # Generate summary
            summary = self.generate_conversation_summary(title, date_str, messages, insights)
            self.summaries[month_key].append(summary)

        self.write_outputs()
        self.print_stats()


class ClaudeProcessor(ConversationProcessor):
    """Process Claude exports."""

    def __init__(self):
        super().__init__("claude")

    def process(self):
        """Process all Claude conversations."""
        print(f"\nProcessing Claude conversations from {CLAUDE_FILE}...")

        with open(CLAUDE_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)

        self.stats['total'] = len(data)

        for conv in data:
            title = conv.get('name', '')
            chat_messages = conv.get('chat_messages', [])
            create_time = conv.get('created_at', '')

            # If no title, use first message
            if not title and chat_messages:
                title = chat_messages[0].get('text', 'Untitled')[:60]

            # Extract messages
            messages = []
            for msg in chat_messages:
                messages.append({
                    'role': 'user' if msg.get('sender') == 'human' else 'assistant',
                    'content': msg.get('text', ''),
                    'timestamp': msg.get('created_at', create_time)
                })

            # Skip trivial
            if self.is_trivial(title, messages):
                self.stats['skipped'] += 1
                continue

            self.stats['processed'] += 1

            # Format date
            try:
                date = datetime.fromisoformat(create_time.replace('Z', '+00:00'))
                date_str = date.strftime("%Y-%m-%d")
                month_key = date.strftime("%Y-%m")
            except:
                date_str = "unknown"
                month_key = "unknown"

            # Extract insights
            insights = self.extract_insights(messages, title)
            self.items.extend(insights)
            self.stats['items_extracted'] += len(insights)

            # Generate summary
            summary = self.generate_conversation_summary(title, date_str, messages, insights)
            self.summaries[month_key].append(summary)

        self.write_outputs()
        self.print_stats()


def generate_final_report():
    """Generate a combined report of all processing."""
    report_file = OUTPUT_DIR / "PROCESSING_REPORT.md"

    all_items = []
    all_sensitive = []

    # Collect all items
    for source in ['chatgpt', 'claude', 'grok']:
        source_dir = OUTPUT_DIR / "ai-history" / source / "processed"
        if source_dir.exists():
            for json_file in source_dir.glob("items-*.json"):
                with open(json_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    items = data.get('items', [])
                    all_items.extend(items)
                    all_sensitive.extend([i for i in items if i.get('sensitive')])

    # Count by type
    by_type = defaultdict(int)
    by_category = defaultdict(int)
    for item in all_items:
        by_type[item.get('type', 'unknown')] += 1
        for tag in item.get('tags', []):
            by_category[tag] += 1

    with open(report_file, 'w', encoding='utf-8') as f:
        f.write("# AI Conversation Export Processing Report\n\n")
        f.write(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")

        f.write("## Summary\n\n")
        f.write(f"- **Total items extracted:** {len(all_items)}\n")
        f.write(f"- **Sensitive items flagged:** {len(all_sensitive)}\n\n")

        f.write("## Items by Type\n\n")
        f.write("| Type | Count |\n")
        f.write("|------|-------|\n")
        for type_name, count in sorted(by_type.items(), key=lambda x: -x[1]):
            f.write(f"| {type_name} | {count} |\n")
        f.write("\n")

        f.write("## Items by Category\n\n")
        f.write("| Category | Count |\n")
        f.write("|----------|-------|\n")
        for cat, count in sorted(by_category.items(), key=lambda x: -x[1]):
            f.write(f"| {cat} | {count} |\n")
        f.write("\n")

        if all_sensitive:
            f.write("## Sensitive Items for Review\n\n")
            f.write("The following items were flagged as potentially sensitive:\n\n")
            for item in all_sensitive[:50]:  # Limit display
                f.write(f"- **[{item.get('type')}]** {item.get('content')[:100]}...\n")
                f.write(f"  - Source: {item.get('source')}, Date: {item.get('sourceDate')}\n\n")

    print(f"\nFinal report written to: {report_file}")


def main():
    """Main entry point."""
    print("=" * 60)
    print("Memory Vault - AI Conversation Export Processor")
    print("=" * 60)

    # Process each source
    chatgpt = ChatGPTProcessor()
    chatgpt.process()

    claude = ClaudeProcessor()
    claude.process()

    grok = GrokProcessor()
    grok.process()

    # Generate final report
    generate_final_report()

    print("\n" + "=" * 60)
    print("Processing complete!")
    print("=" * 60)


if __name__ == "__main__":
    main()
