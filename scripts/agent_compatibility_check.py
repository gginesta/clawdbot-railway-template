#!/usr/bin/env python3
import json
import subprocess
import sys
from typing import List, Dict

class AgentCompatibilityChecker:
    def __init__(self):
        self.agents = [
            {"id": "molty", "workspace": "/data/workspace"},
            {"id": "raphael", "workspace": "/data/shared/brinc"},
            {"id": "leonardo", "workspace": "/data/shared/cerebro"}
        ]
        self.compatibility_results = {}

    def check_workspace_exists(self, agent: Dict[str, str]) -> bool:
        """Check if agent's workspace exists."""
        try:
            result = subprocess.run(
                ['test', '-d', agent['workspace']], 
                capture_output=True, 
                text=True
            )
            return result.returncode == 0
        except Exception as e:
            print(f"Error checking {agent['id']} workspace: {e}")
            return False

    def check_qmd_availability(self, agent: Dict[str, str]) -> bool:
        """Verify QMD is available in agent's environment."""
        try:
            result = subprocess.run(
                ['which', 'qmd'], 
                capture_output=True, 
                text=True,
                cwd=agent['workspace']
            )
            return result.returncode == 0
        except Exception as e:
            print(f"Error checking QMD for {agent['id']}: {e}")
            return False

    def check_cron_config_compatibility(self, agent: Dict[str, str]) -> bool:
        """Verify cron job configuration compatibility."""
        try:
            # Simulate running the validator in the agent's context
            result = subprocess.run(
                [sys.executable, '/data/workspace/scripts/cron_job_validator.py'], 
                capture_output=True, 
                text=True,
                cwd=agent['workspace']
            )
            return result.returncode == 0
        except Exception as e:
            print(f"Error validating cron config for {agent['id']}: {e}")
            return False

    def run_compatibility_checks(self):
        """Run comprehensive compatibility checks."""
        for agent in self.agents:
            agent_checks = {
                "workspace_exists": self.check_workspace_exists(agent),
                "qmd_available": self.check_qmd_availability(agent),
                "cron_config_compatible": self.check_cron_config_compatibility(agent)
            }
            
            # Determine overall compatibility
            agent_checks['fully_compatible'] = all(agent_checks.values())
            
            self.compatibility_results[agent['id']] = agent_checks

    def generate_report(self):
        """Generate a comprehensive compatibility report."""
        print("🤖 TMNT Squad Agent Compatibility Report")
        print("=====================================")
        
        for agent_id, results in self.compatibility_results.items():
            print(f"\n📋 Agent: {agent_id}")
            print(f"Workspace Exists: {'✅' if results['workspace_exists'] else '❌'}")
            print(f"QMD Available: {'✅' if results['qmd_available'] else '❌'}")
            print(f"Cron Config Compatible: {'✅' if results['cron_config_compatible'] else '❌'}")
            print(f"Fully Compatible: {'✅' if results['fully_compatible'] else '❌'}")
        
        return all(
            agent_results['fully_compatible'] 
            for agent_results in self.compatibility_results.values()
        )

def main():
    checker = AgentCompatibilityChecker()
    checker.run_compatibility_checks()
    is_fully_compatible = checker.generate_report()
    
    sys.exit(0 if is_fully_compatible else 1)

if __name__ == '__main__':
    main()