var config = require("semantic-release-preconfigured-conventional-commits")

var imageTag = process.env.IMAGE_TAG;
var dockerSetupBuildx = "docker buildx create --use";
var dockerBuildLatestImage = `docker buildx build --platform linux/amd64,linux/arm64 -t ${imageTag} .`
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
      "publishCmd": dockerSetupBuildx + "\n"
        + dockerBuildLatestImage + "\n"
        + dockerTagVersionedImage + "\n"
        + dockerPushLatestImage + "\n"
        + dockerPushVersionedImage  + "\n",
    }
  ]
);

module.exports = config;