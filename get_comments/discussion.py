import os
import requests
import json
import config
import logging

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

cfg = config.load()
owner = cfg['discussion']['github_user']
repo_name = cfg['discussion']['github_repo']
category_id = cfg['discussion']['category_id']
limit = cfg['discussion'].get('limit', 10)
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

# 输出到 JSON 文件
output_file = os.path.join(output_dir, 'latest_discussion.json')
with open(output_file, 'w') as f:
    json.dump(comments_and_replies, f, indent=2)
    logging.info(f"Comments have been saved to {output_file}")