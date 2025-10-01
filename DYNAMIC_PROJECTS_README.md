# Dynamic Project Details Fetching from GitHub API

## Overview

This implementation adds dynamic project details fetching from the GitHub API to replace the hardcoded project information on the `/projects` page. The system automatically fetches project information from the ContriHUB GitHub organization and displays it with enhanced UI components.

## Features Implemented

### 1. Environment Variable Configuration
- **PROJECT_NAMES**: Comma-separated list of project names to fetch from GitHub
- **GITHUB_ORG_NAME**: GitHub organization name (default: "ContriHUB")
- **GITHUB_API_TOKEN**: Optional GitHub API token for higher rate limits

### 2. GitHub API Service
- Fetches repository details including name, description, stars, forks, language
- Retrieves contributor information to identify mentors
- Handles API rate limiting and error scenarios
- Provides fallback data when GitHub API is unavailable

### 3. Dynamic Template Rendering
- Modern card-based layout with enhanced styling
- Displays project statistics (stars, forks, language)
- Shows contributor/mentor information with GitHub links
- Responsive design with hover effects
- Error handling display

### 4. Enhanced Error Handling
- Graceful fallback when GitHub API is unavailable
- Logging for debugging and monitoring
- User-friendly error messages

## Files Modified/Created

### Modified Files:
1. **`contrihub/settings.py`**
   - Added PROJECT_NAMES, GITHUB_ORG_NAME, GITHUB_API_TOKEN configuration

2. **`project/views.py`**
   - Updated home view to use GitHub API service
   - Added error handling and fallback mechanism

3. **`sample_env_file.txt`**
   - Added documentation for new environment variables

### Created Files:
1. **`project/github_service.py`**
   - GitHub API service class with methods for fetching repository data
   - Contributor information retrieval
   - Error handling and logging

2. **`project/templates/projects_dynamic.html`**
   - Dynamic template for rendering GitHub API data
   - Enhanced UI with project statistics and mentor information
   - Responsive design with modern styling

3. **`test_github_service.py`**
   - Test suite for validating GitHub service functionality
   - Fallback mechanism testing

## Configuration

### Environment Variables Setup

Add the following to your `.env` file:

```env
# Project names for dynamic GitHub API fetching
PROJECT_NAMES=ContriHUB-24,CodeSangam,MovieScreen,EyeProtection,Congestion-Control-Simulator

# GitHub API Configuration for dynamic project fetching
GITHUB_ORG_NAME=ContriHUB
GITHUB_API_TOKEN=your_github_token_here_optional
```

### Required Environment Variables:
- **PROJECT_NAMES**: Required. Comma-separated list of project names
- **GITHUB_ORG_NAME**: Optional (default: "ContriHUB")
- **GITHUB_API_TOKEN**: Optional (recommended for higher rate limits)

## Usage

### 1. Set Environment Variables
Configure the `PROJECT_NAMES` environment variable with the projects you want to display:

```bash
PROJECT_NAMES="ContriHUB-24,CodeSangam,MovieScreen,EyeProtection"
```

### 2. Access the Projects Page
Visit `/project/` to see the dynamically fetched project information.

### 3. GitHub API Token (Optional but Recommended)
Set `GITHUB_API_TOKEN` for higher GitHub API rate limits:
- Without token: 60 requests per hour
- With token: 5,000 requests per hour

## API Information Fetched

For each project, the system fetches:

### Repository Details:
- **Name**: Repository name
- **Description**: Repository description/about section
- **URL**: GitHub repository URL
- **Language**: Primary programming language
- **Stars**: Number of stars
- **Forks**: Number of forks
- **Topics**: Repository topics/tags

### Contributor Information:
- **Contributors**: List of repository contributors
- **Mentors**: Top 3 contributors (considered as mentors)
- **Contribution counts**: Number of contributions per contributor

## Error Handling

### GitHub API Failures:
1. **Network Issues**: Automatic fallback to basic project information
2. **Rate Limiting**: Graceful degradation with error message
3. **Repository Not Found**: Fallback data with GitHub URL
4. **Authentication Issues**: Continue with reduced functionality

### Fallback Mechanism:
When GitHub API fails, the system provides:
- Project name from environment variable
- Generic description
- GitHub URL constructed from organization and project name
- Default mentor information

## Testing

### Manual Testing:
1. Run the test script: `python test_github_service.py`
2. Check Django server: `python manage.py runserver`
3. Visit `/project/` to verify dynamic data loading

### Test Scenarios:
- ✅ GitHub API available and working
- ✅ GitHub API rate limited
- ✅ GitHub API unavailable
- ✅ Invalid project names
- ✅ Missing environment variables

## Performance Considerations

### Caching (Future Enhancement):
- Consider implementing Django cache for GitHub API responses
- Cache duration: 1-2 hours for repository data
- Invalidate cache when PROJECT_NAMES changes

### Rate Limiting:
- GitHub API limits: 60/hour without token, 5000/hour with token
- Consider implementing request batching for large project lists
- Monitor API usage to avoid hitting limits

## Security Considerations

### GitHub API Token:
- Store in environment variables, never in code
- Use tokens with minimal required permissions (public repository access)
- Rotate tokens periodically

### Input Validation:
- PROJECT_NAMES are sanitized before API calls
- GitHub API responses are validated before display

## Future Enhancements

### Potential Improvements:
1. **Caching**: Implement Django cache for API responses
2. **Background Jobs**: Use Celery for asynchronous API fetching
3. **Admin Interface**: Django admin interface for managing project lists
4. **Analytics**: Track project view statistics
5. **Search/Filter**: Add project search and filtering capabilities
6. **Real-time Updates**: WebSocket integration for live project updates

### Additional GitHub Data:
- Issue counts and labels
- Recent commits and activity
- Release information
- Project health metrics

## Troubleshooting

### Common Issues:

1. **"No projects available"**
   - Check PROJECT_NAMES environment variable
   - Verify project names exist in GitHub organization
   - Check network connectivity

2. **"Unable to fetch latest project data"**
   - GitHub API rate limit exceeded
   - Network connectivity issues
   - Invalid GitHub API token

3. **Projects showing basic information only**
   - Fallback mode activated due to API issues
   - Check logs for specific error messages

### Logging:
Check Django logs for detailed error information:
```python
import logging
logger = logging.getLogger(__name__)
```

## Migration from Hardcoded Projects

### Before (Hardcoded):
- Static HTML with manually entered project information
- Manual updates required for new projects
- Inconsistent project information format

### After (Dynamic):
- Automatic fetching from GitHub API
- Consistent project information format
- Real-time updates from GitHub
- Enhanced UI with statistics and contributor information

The system maintains backward compatibility and provides fallback mechanisms to ensure the projects page always displays useful information, even when GitHub API is unavailable.