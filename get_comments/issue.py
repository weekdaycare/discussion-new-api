import os
import requests
import json
import config
import logging

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

cfg = config.load()
owner = cfg['issue']['github_user']
repo_name = cfg['issue']['github_repo']
limit = cfg['issue'].get('limit', 10)
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

data = response.json()

# 提取评论数据
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

# 按创建时间排序
comments_and_replies.sort(key=lambda x: x['createdAt'], reverse=True)

output_dir = 'output'
os.makedirs(output_dir, exist_ok=True)

# 输出到 JSON 文件
output_file = os.path.join(output_dir, 'latest_issues.json')
with open(output_file, 'w') as f:
    json.dump(comments_and_replies, f, indent=2)
    logging.info(f"Comments have been saved to {output_file}")

