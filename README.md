## 说明

为基于 issue 或者 discussion 的评论组件提供最新评论 `json` 文件。

> 如果你抓取的不是本仓库的评论，请手动打开 Action 中的 `schedule` 工作流触发定时抓取。

## 配置

```yaml
# 基于 issue 的评论区如 beadur
issue:
  enable: # true
  github_user: "weekdaycare"
  github_repo: "weekdaycare.github.io"
  limit: 20 # 默认为 10

# 基于 disccusion 的评论区如 giscus
discussion:
  enable: # true
  github_user: "weekdaycare"
  github_repo: "blog-comments"
  category_id: "DIC_xxx" # https://giscus.app/zh-CN
  limit: 20 # 默认为 10
```

> `GITHUB_CATEGORY_ID` :你可以在 https://giscus.app/ 中找到 `data-category-id` 注意是 ID 不是名称！

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