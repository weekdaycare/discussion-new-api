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
                id
                body
                createdAt
                url
                author {
                  login
                  avatarUrl
                }
                replies(last: ${limit}) {
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

  let commentsAndReplies = [];
  data.data.repository.discussions.nodes.forEach(discussion => {
    discussion.comments.nodes.forEach(comment => {
      let commentData = {
        body: comment.body,
        createdAt: comment.createdAt,
        url: comment.url,
        author: comment.author
      };
      commentsAndReplies.push(commentData);

      // 为每个回复分配评论的 URL
      comment.replies.nodes.forEach(reply => {
        let replyData = {
          body: reply.body,
          createdAt: reply.createdAt,
          url: comment.url, // 使用评论的 URL
          author: reply.author
        };
        commentsAndReplies.push(replyData);
      });
    });
  });

  commentsAndReplies.sort((a, b) => new Date(b.createdAt) - new Date(a.createdAt));
  commentsAndReplies = commentsAndReplies.slice(0, limit);
  res.status(200).json(commentsAndReplies);
};
