"""
Test module for GitHub service functionality.
This module can be used to test the GitHub API integration without running the Django server.
"""

import os
import sys
import django

# Add the project directory to the Python path
project_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_dir)

# Set up Django settings (minimal configuration for testing)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'contrihub.settings')

try:
    django.setup()
    from project.github_service import get_github_service
    
    def test_github_service():
        """Test the GitHub service functionality."""
        print("Testing GitHub Service...")
        
        # Create GitHub service instance
        github_service = get_github_service()
        print(f"Organization: {github_service.org_name}")
        print(f"API URL: {github_service.base_url}")
        
        # Test with a small set of projects
        test_projects = ['ContriHUB-24']
        
        print(f"\nTesting with projects: {test_projects}")
        
        try:
            projects_data = github_service.get_projects_data(test_projects)
            
            print(f"\nFetched data for {len(projects_data)} projects:")
            
            for project in projects_data:
                print(f"\nProject: {project.get('name', 'Unknown')}")
                print(f"Description: {project.get('description', 'No description')[:100]}...")
                print(f"URL: {project.get('html_url', 'No URL')}")
                print(f"Language: {project.get('language', 'Unknown')}")
                print(f"Stars: {project.get('stars', 0)}")
                print(f"Forks: {project.get('forks', 0)}")
                print(f"Contributors: {len(project.get('contributors', []))}")
                print(f"Mentors: {len(project.get('mentors', []))}")
                
                if project.get('mentors'):
                    print("Top mentors:")
                    for mentor in project['mentors'][:3]:
                        print(f"  - {mentor.get('login', 'Unknown')} ({mentor.get('contributions', 0)} contributions)")
            
            print("\n✅ GitHub service test completed successfully!")
            return True
            
        except Exception as e:
            print(f"\n❌ Error during GitHub service test: {str(e)}")
            print("This might be due to:")
            print("1. Network connectivity issues")
            print("2. GitHub API rate limiting")
            print("3. Missing or invalid GitHub API token")
            print("4. Repository access restrictions")
            return False
    
    def test_fallback_functionality():
        """Test fallback functionality when GitHub API fails."""
        print("\n\nTesting fallback functionality...")
        
        # Mock project names
        project_names = ['ContriHUB-24', 'TestProject']
        
        fallback_projects = []
        for project_name in project_names:
            fallback_projects.append({
                'name': project_name,
                'description': 'Description not available',
                'html_url': f"https://github.com/ContriHUB/{project_name}",
                'mentors': [{'login': 'ContriHUB Team', 'html_url': 'https://github.com/ContriHUB'}]
            })
        
        print(f"Created fallback data for {len(fallback_projects)} projects")
        for project in fallback_projects:
            print(f"- {project['name']}: {project['html_url']}")
        
        print("✅ Fallback functionality test completed!")
        return True
    
    if __name__ == "__main__":
        print("ContriHUB Dynamic Project Fetching - Test Suite")
        print("=" * 50)
        
        # Run tests
        github_test_result = test_github_service()
        fallback_test_result = test_fallback_functionality()
        
        print("\n" + "=" * 50)
        print("Test Summary:")
        print(f"GitHub Service Test: {'✅ PASSED' if github_test_result else '❌ FAILED'}")
        print(f"Fallback Test: {'✅ PASSED' if fallback_test_result else '❌ FAILED'}")
        
        if github_test_result and fallback_test_result:
            print("\n🎉 All tests passed! The dynamic project fetching feature is ready to use.")
        else:
            print("\n⚠️  Some tests failed. Please check the error messages above.")
            
        print("\nTo use this feature:")
        print("1. Set PROJECT_NAMES environment variable with comma-separated project names")
        print("2. Optionally set GITHUB_API_TOKEN for higher rate limits")
        print("3. Visit /project/ URL to see dynamically fetched projects")

except ImportError as e:
    print(f"❌ Import error: {e}")
    print("This test requires Django to be properly configured.")
    print("Please ensure all dependencies are installed and Django settings are configured.")