#!/usr/bin/env python3
import os
import json
from datetime import datetime

class MemoryVaultExplorer:
    def __init__(self, vault_path='/data/shared/memory-vault'):
        self.vault_path = vault_path
        
    def explore_knowledge_graph(self):
        """Explore the PARA-based Knowledge Graph."""
        knowledge_path = os.path.join(self.vault_path, 'knowledge')
        print("🧠 Knowledge Graph (PARA) Structure")
        print("==================================")
        
        layers = ['projects', 'areas', 'resources', 'archives']
        
        for layer in layers:
            layer_path = os.path.join(knowledge_path, layer)
            print(f"\n📁 {layer.capitalize()}:")
            
            if not os.path.exists(layer_path):
                print(f"   ❌ {layer} directory not found")
                continue
            
            items = os.listdir(layer_path)
            print(f"   Total Items: {len(items)}")
            
            # Show first few items
            for item in items[:5]:
                print(f"   - {item}")
            
            if len(items) > 5:
                print(f"   ... and {len(items) - 5} more")

    def check_daily_notes(self):
        """Check daily notes structure and recent entries."""
        daily_path = os.path.join(self.vault_path, 'daily')
        print("\n📅 Daily Notes Structure")
        print("=======================")
        
        years = sorted(os.listdir(daily_path))
        print(f"Years covered: {years}")
        
        for year in years[-2:]:  # Last two years
            year_path = os.path.join(daily_path, year)
            months = sorted(os.listdir(year_path))
            
            print(f"\nYear: {year}")
            for month in months[-3:]:  # Last three months
                month_path = os.path.join(year_path, month)
                notes = sorted(os.listdir(month_path))
                
                print(f"  Month: {month}")
                print(f"  Total Notes: {len(notes)}")
                
                # Show last three notes
                for note in notes[-3:]:
                    note_path = os.path.join(month_path, note)
                    stat = os.stat(note_path)
                    print(f"    - {note} (Size: {stat.st_size} bytes)")

    def explore_ai_history(self):
        """Explore AI conversation history archives."""
        ai_history_path = os.path.join(self.vault_path, 'ai-history')
        print("\n🤖 AI Conversation History")
        print("==========================")
        
        platforms = ['chatgpt', 'claude', 'grok']
        
        for platform in platforms:
            platform_path = os.path.join(ai_history_path, platform)
            
            print(f"\n📱 {platform.capitalize()}:")
            
            if not os.path.exists(platform_path):
                print(f"   ❌ No archives found for {platform}")
                continue
            
            archives = os.listdir(platform_path)
            print(f"   Total Archives: {len(archives)}")
            
            # Show first few archives
            for archive in archives[:5]:
                print(f"   - {archive}")
            
            if len(archives) > 5:
                print(f"   ... and {len(archives) - 5} more")

    def run_diagnostic(self):
        """Run comprehensive Memory Vault diagnostic."""
        self.explore_knowledge_graph()
        self.check_daily_notes()
        self.explore_ai_history()

def main():
    explorer = MemoryVaultExplorer()
    explorer.run_diagnostic()

if __name__ == '__main__':
    main()