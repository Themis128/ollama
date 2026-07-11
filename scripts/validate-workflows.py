#!/usr/bin/env python3
"""Validate GitHub workflow files."""

import yaml
from pathlib import Path
import sys

def validate_workflow(path: Path) -> bool:
    """Validate a workflow file."""
    try:
        with open(path) as f:
            workflow = yaml.safe_load(f)
        
        # Check required fields
        if 'jobs' not in workflow:
            print(f"❌ {path.name}: Missing 'jobs' key")
            return False
        
        # Validate each job
        for job_name, job in workflow['jobs'].items():
            if 'runs-on' not in job:
                print(f"⚠️  {path.name}: Job '{job_name}' missing 'runs-on'")
            if 'steps' not in job:
                print(f"❌ {path.name}: Job '{job_name}' missing 'steps'")
                return False
        
        print(f"✓ {path.name}: Valid workflow structure")
        return True
        
    except Exception as e:
        print(f"❌ {path.name}: {e}")
        return False

def main():
    workflows_dir = Path(".github/workflows")
    if not workflows_dir.exists():
        print("No .github/workflows directory found")
        return
    
    workflow_files = list(workflows_dir.glob("*.yml")) + list(workflows_dir.glob("*.yaml"))
    
    if not workflow_files:
        print("No workflow files found")
        return
    
    print(f"Validating {len(workflow_files)} workflow files...\n")
    
    passed = sum(validate_workflow(w) for w in workflow_files)
    
    print(f"\n{passed}/{len(workflow_files)} workflows validated")

if __name__ == "__main__":
    main()