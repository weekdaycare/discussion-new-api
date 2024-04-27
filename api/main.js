const fetch = require('node-fetch');
const token = process.env.GITHUB_TOKEN;
const apiUrl = 'https://api.github.com/graphql';

module.exports = async (req, res) => {
  const owner = process.env.GITHUB_REPO_OWNER;
  const repoName = process.env.GITHUB_REPO_NAME;
  const categoryId = process.env.GITHUB_CATEGORY_ID;
  const limit = process.env.LIMIT;

  const query = `
    query {
      repository(owner: "${owner}", name: "${repoName}") {
        discussions(last: 100, categoryId: "${categoryId}") {
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

  const response = await fetch(apiUrl, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      Authorization: `Bearer ${token}`
    },
    body: JSON.stringify({ query })
  });
  const data = await response.json();

  let comments = [];
  data.data.repository.discussions.nodes.forEach(discussion => {
    discussion.comments.nodes.forEach(comment => {
      comments.push(comment);
    });
  });

  comments.sort((a, b) => new Date(b.createdAt) - new Date(a.createdAt));
  comments = comments.slice(0, limit);
  res.status(200).json(comments);
};
