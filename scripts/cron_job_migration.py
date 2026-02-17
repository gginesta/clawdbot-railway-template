#!/usr/bin/env python3
import json
import os
from typing import Dict, Any

class CronJobMigrator:
    def __init__(self, config_path: str):
        with open(config_path, 'r') as f:
            self.config = json.load(f)
        
        self.model_mapping = {
            'google/gemini-2.5-flash': 'openrouter/google/gemini-2.5-flash',
            'anthropic/claude-sonnet-4-0': 'openrouter/anthropic/claude-sonnet-4-0',
            'qwen-portal/coder-model': 'openrouter/qwen-portal/coder-model'
        }
        
        self.log_entries = []

    def log(self, message: str):
        """Log migration actions."""
        self.log_entries.append(message)
        print(message)

    def update_model_path(self, model: str) -> str:
        """Update model path to full OpenRouter format."""
        return self.model_mapping.get(model, model)

    def migrate_job(self, job: Dict[str, Any]) -> Dict[str, Any]:
        """Migrate a single cron job."""
        updated_job = job.copy()
        
        # Ensure isolated session
        if updated_job.get('sessionTarget') != 'isolated':
            self.log(f"🔄 Migrating job {job['id']} to isolated session")
            updated_job['sessionTarget'] = 'isolated'
        
        # Update payload
        if 'payload' in updated_job:
            # Ensure agentTurn payload
            if updated_job['payload'].get('kind') != 'agentTurn':
                self.log(f"🔄 Updating payload kind for job {job['id']} to agentTurn")
                updated_job['payload']['kind'] = 'agentTurn'
            
            # Update model path
            if 'model' in updated_job['payload']:
                original_model = updated_job['payload']['model']
                updated_model = self.update_model_path(original_model)
                if original_model != updated_model:
                    self.log(f"🔄 Updating model for job {job['id']}: {original_model} → {updated_model}")
                    updated_job['payload']['model'] = updated_model
            
            # Ensure timeout
            if not updated_job['payload'].get('timeoutSeconds'):
                self.log(f"🔄 Adding default timeout for job {job['id']}")
                updated_job['payload']['timeoutSeconds'] = 180
        
        # Ensure delivery configuration
        if not updated_job.get('delivery'):
            self.log(f"🔄 Adding default delivery for job {job['id']}")
            updated_job['delivery'] = {
                'mode': 'announce',
                'channel': 'discord',
                'to': 'channel:1468164160398557216'
            }
        
        # Ensure timezone
        if 'schedule' in updated_job and not updated_job['schedule'].get('tz'):
            self.log(f"🔄 Adding default timezone for job {job['id']}")
            updated_job['schedule']['tz'] = 'Asia/Hong_Kong'
        
        return updated_job

    def migrate_all_jobs(self):
        """Migrate all cron jobs."""
        migrated_jobs = []
        for job in self.config['jobs']:
            migrated_job = self.migrate_job(job)
            migrated_jobs.append(migrated_job)
        
        self.config['jobs'] = migrated_jobs

    def save_config(self, output_path: str):
        """Save updated configuration."""
        with open(output_path, 'w') as f:
            json.dump(self.config, f, indent=2)
        
        # Log migration summary
        self.log("\n🏁 Migration Summary:")
        self.log(f"Total Jobs Migrated: {len(self.config['jobs'])}")

def main():
    input_path = '/data/.openclaw/cron/jobs.json'
    output_path = '/data/.openclaw/cron/jobs_migrated.json'
    
    migrator = CronJobMigrator(input_path)
    migrator.migrate_all_jobs()
    migrator.save_config(output_path)
    
    # Optional: Write log to file
    with open('/data/workspace/logs/cron_migration.log', 'w') as log_file:
        log_file.write('\n'.join(migrator.log_entries))

if __name__ == '__main__':
    main()