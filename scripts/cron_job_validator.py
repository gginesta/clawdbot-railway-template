#!/usr/bin/env python3
import json
import sys
import re
from typing import Dict, Any

class CronJobValidator:
    def __init__(self, config_path: str):
        with open(config_path, 'r') as f:
            self.jobs = json.load(f)['jobs']
        
        self.errors = []
    
    def validate_session_target(self, job: Dict[str, Any]) -> bool:
        """Ensure job runs in isolated session."""
        if job.get('sessionTarget') != 'isolated':
            self.errors.append(f"Job {job['id']} is NOT in isolated session!")
            return False
        return True
    
    def validate_delivery(self, job: Dict[str, Any]) -> bool:
        """Check delivery configuration."""
        delivery = job.get('delivery', {})
        if not delivery or delivery.get('mode') not in ['announce', 'none']:
            self.errors.append(f"Job {job['id']} has invalid delivery configuration!")
            return False
        
        # Validate channel and target for announce mode
        if delivery.get('mode') == 'announce':
            if not delivery.get('channel'):
                self.errors.append(f"Announce job {job['id']} missing delivery channel!")
                return False
            if not delivery.get('to'):
                self.errors.append(f"Announce job {job['id']} missing delivery target!")
                return False
        
        return True
    
    def validate_payload(self, job: Dict[str, Any]) -> bool:
        """Validate payload configuration."""
        payload = job.get('payload', {})
        
        # Ensure payload kind is agentTurn
        if payload.get('kind') != 'agentTurn':
            self.errors.append(f"Job {job['id']} should use 'agentTurn' payload kind!")
            return False
        
        # Validate model (full path, not alias)
        model = payload.get('model', '')
        if not re.match(r'^[\w-]+/[\w-]+/[\w-]+', model):
            self.errors.append(f"Job {job['id']} uses invalid model format: {model}")
            return False
        
        # Check timeout
        timeout = payload.get('timeoutSeconds', 0)
        if timeout <= 0 or timeout > 3600:  # Max 1 hour
            self.errors.append(f"Job {job['id']} has invalid timeout: {timeout}")
            return False
        
        return True
    
    def validate_schedule(self, job: Dict[str, Any]) -> bool:
        """Validate job scheduling configuration."""
        schedule = job.get('schedule', {})
        
        # Ensure timezone is specified
        if not schedule.get('tz'):
            self.errors.append(f"Job {job['id']} missing timezone!")
            return False
        
        # Validate schedule kind
        if schedule.get('kind') not in ['cron', 'at', 'every']:
            self.errors.append(f"Job {job['id']} has invalid schedule kind!")
            return False
        
        return True
    
    def validate_all_jobs(self) -> bool:
        """Run comprehensive validation on all jobs."""
        all_valid = True
        for job in self.jobs:
            job_valid = (
                self.validate_session_target(job) and
                self.validate_delivery(job) and
                self.validate_payload(job) and
                self.validate_schedule(job)
            )
            all_valid &= job_valid
        
        return all_valid
    
    def report(self):
        """Generate validation report."""
        if not self.errors:
            print("✅ All cron jobs passed validation!")
        else:
            print("❌ Cron Job Validation Errors:")
            for error in self.errors:
                print(f"  - {error}")

def main():
    validator = CronJobValidator('/data/.openclaw/cron/jobs.json')
    is_valid = validator.validate_all_jobs()
    validator.report()
    
    sys.exit(0 if is_valid else 1)

if __name__ == '__main__':
    main()