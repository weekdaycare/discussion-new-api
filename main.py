import os
import requests
import json
import logging

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def load_config():
    repo_user, repo_name = os.getenv('GITHUB_REPO', '/').split('/')
    return {
        'issue': {
            'enable': os.getenv('ISSUE_ENABLE', 'true').lower() == 'true',
            'github_user': repo_user,
            'github_repo': repo_name,
            'limit': int(os.getenv('LIMIT', 10))
        },
        'discussion': {
            'enable': os.getenv('DISCUSSION_ENABLE', 'true').lower() == 'true',
            'github_user': repo_user,
            'github_repo': repo_name,
            'category_id': os.getenv('CATEGORY_ID'),
            'limit': int(os.getenv('LIMIT', 10))
        }
    }

def fetch_comments(url, headers, limit):
    logging.info(f"Fetching comments from {url}")
    response = requests.get(url, headers=headers)
    
    if response.status_code != 200:
        logging.error(f"Query failed with status code {response.status_code}: {response.text}")
        return []
    
    return response.json()[:limit]

def save_to_file(data, filename):
    output_dir = 'output'
    os.makedirs(output_dir, exist_ok=True)
    output_file = os.path.join(output_dir, filename)
    with open(output_file, 'w') as f:
        json.dump(data, f, indent=2)
    logging.info(f"Comments have been saved to {output_file}")

def fetch_issue_comments(cfg):
    owner, repo_name, limit = cfg['issue'].values()
    token = os.getenv('GITHUB_TOKEN')
    url = f"https://api.github.com/repos/{owner}/{repo_name}/issues/comments"
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github.v3+json"
    }

    data = fetch_comments(url, headers, limit)
    comments_and_replies = [
        {
            'body': comment['body'],
            'createdAt': comment['created_at'],
            'url': comment['html_url'],
            'author': {
                'login': comment['user']['login'],
                'avatarUrl': comment['user']['avatar_url']
            }
        }
        for comment in data
    ]

    comments_and_replies.sort(key=lambda x: x['createdAt'], reverse=True)
    save_to_file(comments_and_replies, 'latest_issues.json')

def fetch_discussion_comments(cfg):
    owner, repo_name, category_id, limit = cfg['discussion'].values()
    token = os.getenv('GITHUB_TOKEN')
    query = f"""
    query {{
      repository(owner: "{owner}", name: "{repo_name}") {{
        discussions(last: 100, categoryId: "{category_id}") {{
          nodes {{
            comments(last: {limit}) {{
              nodes {{
                body
                createdAt
                url
                author {{
                  login
                  avatarUrl
                }}
                replies(last: {limit}) {{
                  nodes {{
                    body
                    createdAt
                    author {{
                      login
                      avatarUrl
                    }}
                  }}
                }}
              }}
            }}
          }}
        }}
      }}
    }}
    """

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    logging.info("Fetching comments from discussion")
    response = requests.post('https://api.github.com/graphql', json={'query': query}, headers=headers)

    if response.status_code != 200:
        logging.error(f"Query failed with status code {response.status_code}: {response.text}")
        return

    data = response.json()
    comments_and_replies = []

    for discussion in data['data']['repository']['discussions']['nodes']:
        for comment in discussion['comments']['nodes']:
            comments_and_replies.append({
                'body': comment['body'],
                'createdAt': comment['createdAt'],
                'url': comment['url'],
                'author': comment['author']
            })
            comments_and_replies.extend({
                'body': reply['body'],
                'createdAt': reply['createdAt'],
                'url': comment['url'],
                'author': reply['author']
            } for reply in comment['replies']['nodes'])

    comments_and_replies.sort(key=lambda x: x['createdAt'], reverse=True)
    save_to_file(comments_and_replies[:limit], 'latest_discussion.json')

def main():
    cfg = load_config()
    if cfg['issue']['enable']:
        fetch_issue_comments(cfg)
    if cfg['discussion']['enable']:
        fetch_discussion_comments(cfg)
    if not cfg['issue']['enable'] and not cfg['discussion']['enable']:
        logging.warning("Both issue and discussion fetching are disabled.")

if __name__ == "__main__":
    main()
