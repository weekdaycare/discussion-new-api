## 说明

为基于 issue 或者 discussion 的评论组件提供最新评论 `json` 文件。


## 工作流示例

```yaml
name: Fetch Comments on Events

on:
  issue_comment:
    types: [created, edited, deleted]
  discussion_comment:
    types: [created, edited, deleted]

jobs:
  fetch_comments:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout repository
        uses: actions/checkout@v3

      - name: Fetch Comments
        uses: weekdaycare/issue-discussion-generator@v1.0
        with:
          discussion_enable: # 'true'
          issue_enbale: # 'true'
          category_id: 'DIC_kwDONhvWjc4ClfPP' # 使用 discussion 的填写
          limit: '20' # 默认为 10
          github_token: ${{ secrets.GITHUB_TOKEN }}
          github_repo: ${{ github.repository }}

      - name: Git config
        run: |
          git config --global user.name 'github-actions[bot]'
          git config --global user.email 'github-actions[bot]@users.noreply.github.com'
  
      - name: Commit changes
        run: |
          cd output
          git add .
          git commit -m "📬 $(date +"%Y年%m月%d日-%H时%M分") GitHub Action 推送"
          git push --force https://x-access-token:${{ secrets.GITHUB_TOKEN }}@github.com/${{ github.repository }}.git HEAD:comment
```

> `category_id` :你可以在 https://giscus.app/ 中找到 `data-category-id` 注意是 ID 不是名称！

## 输出

输出文件在 `output` 分支中

```json
[
  {
    "body": "comments",
    "createdAt": "2024-09-10T08:56:49Z",
    "url": "https://github.com/user/repo/issues/xxx",
    "author": {
      "login": "commenter",
      "avatarUrl": "https://comment_avatar_url"
    }
  },
  ...
]
```