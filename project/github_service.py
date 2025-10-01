"""
GitHub API Service Module for fetching repository information dynamically.
"""

import requests
import logging
from typing import List, Dict, Optional
from django.conf import settings

logger = logging.getLogger(__name__)


class GitHubService:
    """Service class to handle GitHub API operations for project details."""
    
    def __init__(self):
        self.org_name = getattr(settings, 'GITHUB_ORG_NAME', 'ContriHUB')
        self.api_token = getattr(settings, 'GITHUB_API_TOKEN', '')
        self.base_url = 'https://api.github.com'
        
    def get_headers(self) -> Dict[str, str]:
        """Get headers for GitHub API requests."""
        headers = {
            'Accept': 'application/vnd.github.v3+json',
            'User-Agent': 'ContriHUB-24-Django-App'
        }
        
        # Add authentication if token is available
        if self.api_token:
            headers['Authorization'] = f'token {self.api_token}'
            
        return headers
    
    def get_repository_details(self, repo_name: str) -> Optional[Dict]:
        """
        Fetch repository details from GitHub API.
        
        Args:
            repo_name (str): Name of the repository
            
        Returns:
            dict: Repository details or None if error
        """
        url = f"{self.base_url}/repos/{self.org_name}/{repo_name}"
        headers = self.get_headers()
        
        try:
            # Use direct requests instead of safe_hit_url for better error handling
            response = requests.get(url, headers=headers, timeout=10)
            
            # Check for rate limiting
            if response.status_code == 403:
                rate_limit_remaining = response.headers.get('X-RateLimit-Remaining', '0')
                logger.warning(f"GitHub API rate limit exceeded. Remaining: {rate_limit_remaining}")
                # Return fallback data for rate limiting
                return self._create_fallback_data(repo_name)
            
            # Check for not found
            if response.status_code == 404:
                logger.warning(f"Repository {repo_name} not found in {self.org_name}")
                return self._create_fallback_data(repo_name)
            
            # Check for successful response
            if response.status_code == 200:
                repo_data = response.json()
                
                # Extract required information
                project_info = {
                    'name': repo_data.get('name', repo_name),
                    'full_name': repo_data.get('full_name', f"{self.org_name}/{repo_name}"),
                    'description': repo_data.get('description') or 'No description available',
                    'html_url': repo_data.get('html_url', f"https://github.com/{self.org_name}/{repo_name}"),
                    'owner': {
                        'login': repo_data.get('owner', {}).get('login', self.org_name),
                        'html_url': repo_data.get('owner', {}).get('html_url', f"https://github.com/{self.org_name}")
                    },
                    'language': repo_data.get('language', 'Unknown'),
                    'topics': repo_data.get('topics', []),
                    'stars': repo_data.get('stargazers_count', 0),
                    'forks': repo_data.get('forks_count', 0),
                    'created_at': repo_data.get('created_at'),
                    'updated_at': repo_data.get('updated_at'),
                    'default_branch': repo_data.get('default_branch', 'main')
                }
                
                logger.info(f"Successfully fetched data for {repo_name}: {project_info.get('description', 'No description')[:50]}...")
                return project_info
            else:
                logger.error(f"GitHub API returned status {response.status_code} for {repo_name}")
                return self._create_fallback_data(repo_name)
                
        except Exception as e:
            logger.error(f"Exception while fetching repository {repo_name}: {str(e)}")
            return self._create_fallback_data(repo_name)
    
    def _create_fallback_data(self, repo_name: str) -> Dict:
        """Create fallback data when GitHub API fails."""
        return {
            'name': repo_name,
            'full_name': f"{self.org_name}/{repo_name}",
            'description': f'A project from {self.org_name} organization',
            'html_url': f"https://github.com/{self.org_name}/{repo_name}",
            'owner': {
                'login': self.org_name,
                'html_url': f"https://github.com/{self.org_name}"
            },
            'language': 'Unknown',
            'topics': [],
            'stars': 0,
            'forks': 0,
            'created_at': None,
            'updated_at': None,
            'default_branch': 'main'
        }
    
    def get_repository_contributors(self, repo_name: str, max_contributors: int = 5) -> List[Dict]:
        """
        Fetch repository contributors from GitHub API.
        
        Args:
            repo_name (str): Name of the repository
            max_contributors (int): Maximum number of contributors to fetch
            
        Returns:
            list: List of contributor information
        """
        url = f"{self.base_url}/repos/{self.org_name}/{repo_name}/contributors"
        headers = self.get_headers()
        
        try:
            response = requests.get(url, headers=headers, timeout=10)
            
            if response.status_code == 200:
                contributors_data = response.json()
                
                contributors = []
                for contributor in contributors_data[:max_contributors]:
                    contributor_info = {
                        'login': contributor.get('login', 'Unknown'),
                        'html_url': contributor.get('html_url', '#'),
                        'avatar_url': contributor.get('avatar_url', ''),
                        'contributions': contributor.get('contributions', 0)
                    }
                    contributors.append(contributor_info)
                
                return contributors
            else:
                logger.warning(f"Failed to fetch contributors for {repo_name}: HTTP {response.status_code}")
                return [{'login': 'ContriHUB Team', 'html_url': f'https://github.com/{self.org_name}', 'avatar_url': '', 'contributions': 0}]
                
        except Exception as e:
            logger.error(f"Exception while fetching contributors for {repo_name}: {str(e)}")
            return [{'login': 'ContriHUB Team', 'html_url': f'https://github.com/{self.org_name}', 'avatar_url': '', 'contributions': 0}]
    
    def get_projects_data(self, project_names: List[str]) -> List[Dict]:
        """
        Fetch data for multiple projects from GitHub API.
        
        Args:
            project_names (list): List of project/repository names
            
        Returns:
            list: List of project data dictionaries
        """
        projects_data = []
        
        for project_name in project_names:
            logger.info(f"Fetching data for project: {project_name}")
            
            # Get repository details
            repo_details = self.get_repository_details(project_name)
            
            if repo_details:
                # Get contributors (mentors)
                contributors = self.get_repository_contributors(project_name)
                
                # Combine the data
                project_data = {
                    **repo_details,
                    'contributors': contributors,
                    'mentors': contributors[:3],  # Consider first 3 contributors as mentors
                }
                
                projects_data.append(project_data)
            else:
                # This should not happen now since get_repository_details always returns data
                logger.warning(f"No data returned for project: {project_name}")
        
        return projects_data


def get_github_service() -> GitHubService:
    """Factory function to get GitHub service instance."""
    return GitHubService()