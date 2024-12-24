import os

def load():
    return {
        'issue': {
            'enable': os.getenv('ISSUE_ENABLE', 'true').lower() == 'true',
            'github_user', 'github_repo' = os.getenv('GITHUB_REPO').split('/')
            'limit': int(os.getenv('LIMIT', 10))
        },
        'discussion': {
            'enable': os.getenv('DISCUSSION_ENABLE', 'true').lower() == 'true',
            'github_user', 'github_repo' = os.getenv('GITHUB_REPO').split('/')
            'category_id': os.getenv('CATEGORY_ID'),
            'limit': int(os.getenv('LIMIT', 10))
        }
    }
