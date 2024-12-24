import os
import requests
import json
import logging

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def load_config():
    return {
        'issue': {
            'enable': os.getenv('ISSUE_ENABLE', 'true').lower() == 'true',
            'github_user': os.getenv('GITHUB_REPO').split('/')[0],
            'github_repo': os.getenv('GITHUB_REPO').split('/')[1],
            'limit': int(os.getenv('LIMIT', 10))
        },
        'discussion': {
            'enable': os.getenv('DISCUSSION_ENABLE', 'true').lower() == 'true',
            'github_user': os.getenv('GITHUB_REPO').split('/')[0],
            'github_repo': os.getenv('GITHUB_REPO').split('/')[1],
            'category_id': os.getenv('CATEGORY_ID'),
            'limit': int(os.getenv('LIMIT', 10))
        }
    }

def fetch_issue_comments(cfg):
    owner = cfg['issue']['github_user']
    repo_name = cfg['issue']['github_repo']
    limit = cfg['issue']['limit']
    token = os.getenv('GITHUB_TOKEN')

    url = f"https://api.github.com/repos/{owner}/{repo_name}/issues/comments"
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github.v3+json"
    }

    logging.info(f"Fetching comments from {url}")
    response = requests.get(url, headers=headers)

    if response.status_code != 200:
        logging.error(f"Query failed with status code {response.status_code}: {response.text}")
        return

    data = response.json()
    comments_and_replies = []
    for comment in data[:limit]:
        comment_data = {
            'body': comment['body'],
            'createdAt': comment['created_at'],
            'url': comment['html_url'],
            'author': {
                'login': comment['user']['login'],
                'avatarUrl': comment['user']['avatar_url']
            }
        }
        comments_and_replies.append(comment_data)

    comments_and_replies.sort(key=lambda x: x['createdAt'], reverse=True)

    output_dir = 'output'
    os.makedirs(output_dir, exist_ok=True)
    output_file = os.path.join(output_dir, 'latest_issues.json')
    with open(output_file, 'w') as f:
        json.dump(comments_and_replies, f, indent=2)
        logging.info(f"Comments have been saved to {output_file}")

def fetch_discussion_comments(cfg):
    owner = cfg['discussion']['github_user']
    repo_name = cfg['discussion']['github_repo']
    category_id = cfg['discussion']['category_id']
    limit = cfg['discussion']['limit']
    token = os.getenv('GITHUB_TOKEN')

    query = """
    query {
      repository(owner: "%s", name: "%s") {
        discussions(last: 100, categoryId: "%s") {
          nodes {
            id
            title
            comments(last: %d) {
              nodes {
                id
                body
                createdAt
                url
                author {
                  login
                  avatarUrl
                }
                replies(last: %d) {
                  nodes {
                    body
                    createdAt
                    author {
                      login
                      avatarUrl
                    }
                  }
                }
              }
            }
          }
        }
      }
    }
    """ % (owner, repo_name, category_id, limit, limit)

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
            comment_data = {
                'body': comment['body'],
                'createdAt': comment['createdAt'],
                'url': comment['url'],
                'author': comment['author']
            }
            comments_and_replies.append(comment_data)

            for reply in comment['replies']['nodes']:
                reply_data = {
                    'body': reply['body'],
                    'createdAt': reply['createdAt'],
                    'url': comment['url'],
                    'author': reply['author']
                }
                comments_and_replies.append(reply_data)

    comments_and_replies.sort(key=lambda x: x['createdAt'], reverse=True)
    comments_and_replies = comments_and_replies[:limit]

    output_dir = 'output'
    os.makedirs(output_dir, exist_ok=True)
    output_file = os.path.join(output_dir, 'latest_discussion.json')
    with open(output_file, 'w') as f:
        json.dump(comments_and_replies, f, indent=2)
        logging.info(f"Comments have been saved to {output_file}")

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
