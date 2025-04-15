"""
Tests for GitHub Actions workflow files.
"""
import os
import yaml
import pytest
import sys
import re

class TestWorkflows:
    
    def _load_workflow_yaml(self, workflow_path):
        """Custom loader for GitHub Actions workflow YAML.
        
        GitHub Actions uses 'on' as a key which is a keyword in Python,
        so we need special handling.
        """
        # Read the file content
        with open(workflow_path, 'r') as f:
            content = f.read()
        
        # Replace 'on:' with 'trigger:' before parsing
        modified_content = re.sub(r'(\s+)on:', r'\1trigger:', content)
        yaml_content = yaml.safe_load(modified_content)
        
        # Validate the original file has expected sections
        assert 'name' in yaml_content
        assert 'trigger' in yaml_content  # This was originally 'on'
        assert 'jobs' in yaml_content
        
        return yaml_content
    
    def test_update_data_workflow(self):
        """Test the update_data.yml workflow file."""
        workflow_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            '.github', 'workflows', 'update_data.yml'
        )
        
        assert os.path.exists(workflow_path), "update_data.yml workflow file not found"
        
        # Simple file existence check
        with open(workflow_path, 'r') as f:
            content = f.read()
            assert 'name: Update Insider Trading Data' in content
            assert 'runs-on: ubuntu-latest' in content
            assert 'python InsiderTrading.py' in content
            assert 'python export_json.py' in content
            assert 'git add data/json/' in content
        
        # Check basic structure using regex
        schedule_pattern = re.compile(r'\s+schedule:[\s\S]*?cron:.*')
        assert schedule_pattern.search(content), "Schedule/cron not found"
        
        workflow_dispatch_pattern = re.compile(r'\s+workflow_dispatch:')
        assert workflow_dispatch_pattern.search(content), "workflow_dispatch not found"
        
        # Check step existence
        checkout_pattern = re.compile(r'\s+- name: Checkout repository')
        assert checkout_pattern.search(content), "Checkout step not found"
        
        python_pattern = re.compile(r'\s+- name: Set up Python')
        assert python_pattern.search(content), "Python setup step not found"
        
        dependencies_pattern = re.compile(r'\s+- name: Install dependencies')
        assert dependencies_pattern.search(content), "Dependencies step not found"
        
        data_pattern = re.compile(r'\s+- name: Collect insider trading data')
        assert data_pattern.search(content), "Data collection step not found"
        
        json_pattern = re.compile(r'\s+- name: Export data to JSON for API')
        assert json_pattern.search(content), "JSON export step not found"
    
    def test_github_pages_workflow(self):
        """Test the github-pages.yml workflow file."""
        workflow_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            '.github', 'workflows', 'github-pages.yml'
        )
        
        assert os.path.exists(workflow_path), "github-pages.yml workflow file not found"
        
        # Simple file existence check
        with open(workflow_path, 'r') as f:
            content = f.read()
            assert 'name: GitHub Pages' in content
            assert 'runs-on: ubuntu-latest' in content
            assert 'id-token: write' in content
            assert 'name: github-pages' in content
        
        # Check push configuration using regex
        push_pattern = re.compile(r'\s+push:[\s\S]*?branches:.*main')
        assert push_pattern.search(content), "Push to main branch config not found"
        
        # Check steps using regex
        checkout_pattern = re.compile(r'\s+- name: Checkout')
        assert checkout_pattern.search(content), "Checkout step not found"
        
        pages_pattern = re.compile(r'\s+- name: Setup Pages')
        assert pages_pattern.search(content), "Pages setup step not found"
        
        upload_pattern = re.compile(r'\s+- name: Upload artifact')
        assert upload_pattern.search(content), "Upload artifact step not found"
        
        deploy_pattern = re.compile(r'\s+- name: Deploy to GitHub Pages')
        assert deploy_pattern.search(content), "Deploy step not found"
        
        deployment_id_pattern = re.compile(r'\s+id: deployment')
        assert deployment_id_pattern.search(content), "Deployment ID not found"