import config
import subprocess
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

cfg = config.load()
issue_enabled = cfg['issue']['enable']
discussion_enabled = cfg['discussion']['enable']

if issue_enabled:
    logging.info("Fetching comments from Issues...")
    subprocess.run(['python', 'get_comments/issue.py'], check=True)

if discussion_enabled:
    logging.info("Fetching comments from Discussions...")
    subprocess.run(['python', 'get_comments/discussion.py'], check=True)

if not issue_enabled and not discussion_enabled:
    logging.warning("Both issue and discussion fetching are disabled.")