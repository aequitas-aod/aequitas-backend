var config = require("semantic-release-preconfigured-conventional-commits")

var imageTag = process.env.IMAGE_TAG;
var dockerBuildLatestImage = `docker build -t ${imageTag} .`
var dockerTagVersionedImage = `docker tag ${imageTag}:latest ${imageTag}:` + "${nextRelease.version}"
var dockerPushLatestImage = `docker push ${imageTag}:latest`
var dockerPushVersionedImage = `docker push ${imageTag}:` + "${nextRelease.version}"

config.preset = 'conventionalcommits';
config.tagFormat = 'v${version}';
config.plugins.push(
  "@semantic-release/github",
  "@semantic-release/git",
  [
    '@semantic-release/exec',
    {
      "publishCmd": dockerBuildLatestImage + "\n"
        + dockerTagVersionedImage + "\n"
        + dockerPushLatestImage + "\n"
        + dockerPushVersionedImage  + "\n",
    }
  ]
);

module.exports = config;