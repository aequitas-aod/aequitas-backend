import config from 'semantic-release-preconfigured-conventional-commits' assert { type: "json" };

const imageTag = process.env.IMAGE_TAG;
const dockerBuildLatestImage = `docker build -t ${imageTag} .`
const dockerTagVersionedImage = `docker tag ${imageTag}:latest ${imageTag}:` + "${nextRelease.version}"
const dockerPushLatestImage = `docker push ${imageTag}:latest`
const dockerPushVersionedImage = `docker push ${imageTag}:` + "${nextRelease.version}"

config.preset = 'conventionalcommits';
config.tagFormat = 'v${version}';
config.plugins.push(
  "@semantic-release/commit-analyzer",
  "@semantic-release/release-notes-generator",
  "@semantic-release/changelog",
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

export default config;