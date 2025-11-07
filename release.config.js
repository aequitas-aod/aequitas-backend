var config = require("semantic-release-preconfigured-conventional-commits")

const imageTag = process.env.IMAGE_TAG;

config.preset = 'conventionalcommits';
config.tagFormat = 'v${version}';
config.plugins.push(
  "@semantic-release/github",
  "@semantic-release/git",
  [
    '@semantic-release/exec',
    {
      "publishCmd": `docker build \
        -t ${imageTag}:latest \
        -t ${imageTag}:\${nextRelease.version} \
        --push .`,
    }
  ]
);

module.exports = config;