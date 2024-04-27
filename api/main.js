const fetch = require('node-fetch');
const token = process.env.GITHUB_TOKEN;
const apiUrl = 'https://api.github.com/graphql';

module.exports = async (req, res) => {
  const owner = process.env.GITHUB_REPO_OWNER;
  const repoName = process.env.GITHUB_REPO_NAME;
  const categoryId = process.env.GITHUB_CATEGORY_ID;
  const limit = process.env.LIMIT;

  // 构建 GraphQL 查询
  const query = `
    query {
      repository(owner: "${owner}", name: "${repoName}") {
        discussions(last: 100, categoryId: "${categoryId}") { // 最高100条
          nodes {
            id
            title
            comments(last: ${limit}) {
              nodes {
                body
                createdAt
                url
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
  `;

  // 发送 GraphQL 请求
  const response = await fetch(apiUrl, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      Authorization: `Bearer ${token}`
    },
    body: JSON.stringify({ query })
  });
  const data = await response.json();

  // 提取所有评论节点
  let comments = [];
  data.data.repository.discussions.nodes.forEach(discussion => {
    discussion.comments.nodes.forEach(comment => {
      comments.push(comment);
    });
  });

  // 降序排序
  comments.sort((a, b) => new Date(b.createdAt) - new Date(a.createdAt));
  res.status(200).json(comments);
};
