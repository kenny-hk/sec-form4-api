"""
Tests for GitHub Actions workflow files.
"""
import os
import yaml
import pytest
import sys

class TestWorkflows:
    
    def test_update_data_workflow(self):
        """Test the update_data.yml workflow file."""
        workflow_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            '.github', 'workflows', 'update_data.yml'
        )
        
        assert os.path.exists(workflow_path), "update_data.yml workflow file not found"
        
        with open(workflow_path, 'r') as f:
            workflow = yaml.safe_load(f)
        
        # Check basic structure
        assert 'name' in workflow
        assert 'on' in workflow
        assert 'jobs' in workflow
        
        # Check schedule
        assert 'schedule' in workflow['on']
        assert isinstance(workflow['on']['schedule'], list)
        assert len(workflow['on']['schedule']) > 0
        assert 'cron' in workflow['on']['schedule'][0]
        
        # Check manual trigger
        assert 'workflow_dispatch' in workflow['on']
        
        # Check job
        assert 'update_data' in workflow['jobs']
        job = workflow['jobs']['update_data']
        
        # Check runner
        assert 'runs-on' in job
        assert job['runs-on'] == 'ubuntu-latest'
        
        # Check steps
        assert 'steps' in job
        steps = job['steps']
        
        # Check for essential steps
        step_names = [step.get('name', '') for step in steps if 'name' in step]
        
        assert any('checkout' in name.lower() for name in step_names), "Repository checkout step missing"
        assert any('python' in name.lower() for name in step_names), "Python setup step missing"
        assert any('dependencies' in name.lower() for name in step_names), "Dependencies step missing"
        assert any('insider trading data' in name.lower() for name in step_names), "Data collection step missing"
        assert any('json' in name.lower() for name in step_names), "JSON export step missing"
        assert any('git' in name.lower() for name in step_names), "Git configuration step missing"
        assert any('commit' in name.lower() for name in step_names), "Commit step missing"
    
    def test_github_pages_workflow(self):
        """Test the github-pages.yml workflow file."""
        workflow_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            '.github', 'workflows', 'github-pages.yml'
        )
        
        assert os.path.exists(workflow_path), "github-pages.yml workflow file not found"
        
        with open(workflow_path, 'r') as f:
            workflow = yaml.safe_load(f)
        
        # Check basic structure
        assert 'name' in workflow
        assert 'on' in workflow
        assert 'jobs' in workflow
        
        # Check trigger
        assert 'push' in workflow['on']
        assert 'branches' in workflow['on']['push']
        assert 'main' in workflow['on']['push']['branches']
        
        # Check manual trigger
        assert 'workflow_dispatch' in workflow['on']
        
        # Check job
        assert 'deploy' in workflow['jobs']
        job = workflow['jobs']['deploy']
        
        # Check runner
        assert 'runs-on' in job
        assert job['runs-on'] == 'ubuntu-latest'
        
        # Check permissions
        assert 'permissions' in job
        permissions = job['permissions']
        assert permissions.get('pages') == 'write'
        assert permissions.get('id-token') == 'write'
        
        # Check environment
        assert 'environment' in job
        assert 'name' in job['environment']
        assert job['environment']['name'] == 'github-pages'
        
        # Check steps
        assert 'steps' in job
        steps = job['steps']
        
        # Check for essential steps
        step_ids = [step.get('id', '') for step in steps if 'id' in step]
        assert 'deployment' in step_ids, "GitHub Pages deployment step missing"
        
        step_names = [step.get('name', '') for step in steps if 'name' in step]
        assert any('checkout' in name.lower() for name in step_names), "Repository checkout step missing"
        assert any('pages' in name.lower() for name in step_names), "Pages setup step missing"
        assert any('upload' in name.lower() for name in step_names), "Upload artifact step missing"
        assert any('deploy' in name.lower() for name in step_names), "Deploy step missing"