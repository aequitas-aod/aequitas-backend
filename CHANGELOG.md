## [0.35.2](https://github.com/aequitas-aod/aequitas-backend/compare/v0.35.1...v0.35.2) (2025-04-04)

### Bug Fixes

* **inprocessing:** mock fauci results for demo ([2405b4b](https://github.com/aequitas-aod/aequitas-backend/commit/2405b4bbb7828f1bdd8887c500fbfa34076ae2ae))

## [0.35.1](https://github.com/aequitas-aod/aequitas-backend/compare/v0.35.0...v0.35.1) (2025-04-03)

### Dependency updates

* **deps:** update docker/setup-buildx-action action to v3.10.0 ([#113](https://github.com/aequitas-aod/aequitas-backend/issues/113)) ([06a992e](https://github.com/aequitas-aod/aequitas-backend/commit/06a992ef6e7e3ec8618b8bf7acd30323659c5304))
* **deps:** update docker/setup-qemu-action action to v3.6.0 ([#114](https://github.com/aequitas-aod/aequitas-backend/issues/114)) ([9e5107a](https://github.com/aequitas-aod/aequitas-backend/commit/9e5107aa98ef523364f473ad44e14c166c27de09))

### Bug Fixes

* **deps:** update dependency pydantic to v2.11.2 ([#110](https://github.com/aequitas-aod/aequitas-backend/issues/110)) ([778d1ee](https://github.com/aequitas-aod/aequitas-backend/commit/778d1ee5056dc79d7b8488afaf2c4d3653d5d7f3))

## [0.35.0](https://github.com/aequitas-aod/aequitas-backend/compare/v0.34.3...v0.35.0) (2025-04-02)

### Features

* **build:** add multiplatform image build ([e3bcaa4](https://github.com/aequitas-aod/aequitas-backend/commit/e3bcaa4ec80a0eb7c9385f77a191b81e126b05d9))
* **resources:** update test/polarization part of general graph ([f922c7d](https://github.com/aequitas-aod/aequitas-backend/commit/f922c7d1e49d1727016d07260556328f31c82e12))
* **storage:** add distinction between GraphAnswer and ProjectAnswer in neo4j db, improve ProjectQuestion insertion retrieving its id in queries ([99ec4b9](https://github.com/aequitas-aod/aequitas-backend/commit/99ec4b9c1de224a843e54331d4b50fd34467277c))
* **utils:** improve Neo4jDriver with results handling ([823e8e8](https://github.com/aequitas-aod/aequitas-backend/commit/823e8e870a4db0241f931605dec979de16aa4f09))

### Dependency updates

* **deps:** update bitnami/kafka docker tag to v4 ([#106](https://github.com/aequitas-aod/aequitas-backend/issues/106)) ([50756e9](https://github.com/aequitas-aod/aequitas-backend/commit/50756e9a67a49a09fb877e05d1bbac19e8b404f7))

### Bug Fixes

* **build:** fix kafka env configuration ([311afb2](https://github.com/aequitas-aod/aequitas-backend/commit/311afb2d288f4073d56721db2f354a829feb1bca))
* **build:** fix kafka version to not migrate to Kraft ([c5ab68f](https://github.com/aequitas-aod/aequitas-backend/commit/c5ab68fd562e56f1ec9f4f97d0fd395cfb826241))
* **build:** trigger new release ([697a2f6](https://github.com/aequitas-aod/aequitas-backend/commit/697a2f6c01faf1a0a8b0b6fa2da9873ab1b5e615))
* **deps:** update dependency coverage to v7.8.0 ([#112](https://github.com/aequitas-aod/aequitas-backend/issues/112)) ([8514156](https://github.com/aequitas-aod/aequitas-backend/commit/8514156da67bb1fda6eeb1a216d71664be4f3178))
* **release:** fix docker buildx setup and release ([c18c8c0](https://github.com/aequitas-aod/aequitas-backend/commit/c18c8c025b939b098e0a0fdc82f51f86154999da))
* **storage:** fix ProjectQuestion insertion with multiple projects in db, replace deprecated ID function of neo4j ([9a26ea5](https://github.com/aequitas-aod/aequitas-backend/commit/9a26ea5c075d31bd006081edb70a2ca5bf21e30e))

### General maintenance

* **release:** 0.35.0 [skip ci] ([b5f0abd](https://github.com/aequitas-aod/aequitas-backend/commit/b5f0abdecfd166b0b3ff1b324604fe25795871e2)), closes [#106](https://github.com/aequitas-aod/aequitas-backend/issues/106) [#112](https://github.com/aequitas-aod/aequitas-backend/issues/112) [#106](https://github.com/aequitas-aod/aequitas-backend/issues/106) [#112](https://github.com/aequitas-aod/aequitas-backend/issues/112) [#106](https://github.com/aequitas-aod/aequitas-backend/issues/106) [#106](https://github.com/aequitas-aod/aequitas-backend/issues/106)
* **release:** 0.35.0 [skip ci] ([4f665ca](https://github.com/aequitas-aod/aequitas-backend/commit/4f665caeb1a6f47651c01008bbe3d70252ff7465)), closes [#106](https://github.com/aequitas-aod/aequitas-backend/issues/106) [#112](https://github.com/aequitas-aod/aequitas-backend/issues/112) [#106](https://github.com/aequitas-aod/aequitas-backend/issues/106)
* **release:** 0.35.0 [skip ci] ([9d14f97](https://github.com/aequitas-aod/aequitas-backend/commit/9d14f974cff8fa778b3d70564812c72d0387052b)), closes [#106](https://github.com/aequitas-aod/aequitas-backend/issues/106)
* **release:** 0.35.0 [skip ci] ([7c602b0](https://github.com/aequitas-aod/aequitas-backend/commit/7c602b06b3d92290a2c93268c4ffd67633d2a305))

## [0.35.0](https://github.com/aequitas-aod/aequitas-backend/compare/v0.34.3...v0.35.0) (2025-03-31)

### Features

* **build:** add multiplatform image build ([e3bcaa4](https://github.com/aequitas-aod/aequitas-backend/commit/e3bcaa4ec80a0eb7c9385f77a191b81e126b05d9))
* **resources:** update test/polarization part of general graph ([f922c7d](https://github.com/aequitas-aod/aequitas-backend/commit/f922c7d1e49d1727016d07260556328f31c82e12))
* **storage:** add distinction between GraphAnswer and ProjectAnswer in neo4j db, improve ProjectQuestion insertion retrieving its id in queries ([99ec4b9](https://github.com/aequitas-aod/aequitas-backend/commit/99ec4b9c1de224a843e54331d4b50fd34467277c))
* **utils:** improve Neo4jDriver with results handling ([823e8e8](https://github.com/aequitas-aod/aequitas-backend/commit/823e8e870a4db0241f931605dec979de16aa4f09))

### Dependency updates

* **deps:** update bitnami/kafka docker tag to v4 ([#106](https://github.com/aequitas-aod/aequitas-backend/issues/106)) ([50756e9](https://github.com/aequitas-aod/aequitas-backend/commit/50756e9a67a49a09fb877e05d1bbac19e8b404f7))

### Bug Fixes

* **build:** fix kafka env configuration ([311afb2](https://github.com/aequitas-aod/aequitas-backend/commit/311afb2d288f4073d56721db2f354a829feb1bca))
* **build:** fix kafka version to not migrate to Kraft ([c5ab68f](https://github.com/aequitas-aod/aequitas-backend/commit/c5ab68fd562e56f1ec9f4f97d0fd395cfb826241))
* **build:** trigger new release ([697a2f6](https://github.com/aequitas-aod/aequitas-backend/commit/697a2f6c01faf1a0a8b0b6fa2da9873ab1b5e615))
* **deps:** update dependency coverage to v7.8.0 ([#112](https://github.com/aequitas-aod/aequitas-backend/issues/112)) ([8514156](https://github.com/aequitas-aod/aequitas-backend/commit/8514156da67bb1fda6eeb1a216d71664be4f3178))
* **storage:** fix ProjectQuestion insertion with multiple projects in db, replace deprecated ID function of neo4j ([9a26ea5](https://github.com/aequitas-aod/aequitas-backend/commit/9a26ea5c075d31bd006081edb70a2ca5bf21e30e))

### General maintenance

* **release:** 0.35.0 [skip ci] ([4f665ca](https://github.com/aequitas-aod/aequitas-backend/commit/4f665caeb1a6f47651c01008bbe3d70252ff7465)), closes [#106](https://github.com/aequitas-aod/aequitas-backend/issues/106) [#112](https://github.com/aequitas-aod/aequitas-backend/issues/112) [#106](https://github.com/aequitas-aod/aequitas-backend/issues/106)
* **release:** 0.35.0 [skip ci] ([9d14f97](https://github.com/aequitas-aod/aequitas-backend/commit/9d14f974cff8fa778b3d70564812c72d0387052b)), closes [#106](https://github.com/aequitas-aod/aequitas-backend/issues/106)
* **release:** 0.35.0 [skip ci] ([7c602b0](https://github.com/aequitas-aod/aequitas-backend/commit/7c602b06b3d92290a2c93268c4ffd67633d2a305))

## [0.35.0](https://github.com/aequitas-aod/aequitas-backend/compare/v0.34.3...v0.35.0) (2025-03-31)

### Features

* **build:** add multiplatform image build ([e3bcaa4](https://github.com/aequitas-aod/aequitas-backend/commit/e3bcaa4ec80a0eb7c9385f77a191b81e126b05d9))
* **storage:** add distinction between GraphAnswer and ProjectAnswer in neo4j db, improve ProjectQuestion insertion retrieving its id in queries ([99ec4b9](https://github.com/aequitas-aod/aequitas-backend/commit/99ec4b9c1de224a843e54331d4b50fd34467277c))
* **utils:** improve Neo4jDriver with results handling ([823e8e8](https://github.com/aequitas-aod/aequitas-backend/commit/823e8e870a4db0241f931605dec979de16aa4f09))

### Dependency updates

* **deps:** update bitnami/kafka docker tag to v4 ([#106](https://github.com/aequitas-aod/aequitas-backend/issues/106)) ([50756e9](https://github.com/aequitas-aod/aequitas-backend/commit/50756e9a67a49a09fb877e05d1bbac19e8b404f7))

### Bug Fixes

* **build:** fix kafka env configuration ([311afb2](https://github.com/aequitas-aod/aequitas-backend/commit/311afb2d288f4073d56721db2f354a829feb1bca))
* **build:** fix kafka version to not migrate to Kraft ([c5ab68f](https://github.com/aequitas-aod/aequitas-backend/commit/c5ab68fd562e56f1ec9f4f97d0fd395cfb826241))
* **build:** trigger new release ([697a2f6](https://github.com/aequitas-aod/aequitas-backend/commit/697a2f6c01faf1a0a8b0b6fa2da9873ab1b5e615))
* **deps:** update dependency coverage to v7.8.0 ([#112](https://github.com/aequitas-aod/aequitas-backend/issues/112)) ([8514156](https://github.com/aequitas-aod/aequitas-backend/commit/8514156da67bb1fda6eeb1a216d71664be4f3178))
* **storage:** fix ProjectQuestion insertion with multiple projects in db, replace deprecated ID function of neo4j ([9a26ea5](https://github.com/aequitas-aod/aequitas-backend/commit/9a26ea5c075d31bd006081edb70a2ca5bf21e30e))

### General maintenance

* **release:** 0.35.0 [skip ci] ([9d14f97](https://github.com/aequitas-aod/aequitas-backend/commit/9d14f974cff8fa778b3d70564812c72d0387052b)), closes [#106](https://github.com/aequitas-aod/aequitas-backend/issues/106)
* **release:** 0.35.0 [skip ci] ([7c602b0](https://github.com/aequitas-aod/aequitas-backend/commit/7c602b06b3d92290a2c93268c4ffd67633d2a305))

## [0.35.0](https://github.com/aequitas-aod/aequitas-backend/compare/v0.34.3...v0.35.0) (2025-03-30)

### Features

* **build:** add multiplatform image build ([e3bcaa4](https://github.com/aequitas-aod/aequitas-backend/commit/e3bcaa4ec80a0eb7c9385f77a191b81e126b05d9))
* **storage:** add distinction between GraphAnswer and ProjectAnswer in neo4j db, improve ProjectQuestion insertion retrieving its id in queries ([99ec4b9](https://github.com/aequitas-aod/aequitas-backend/commit/99ec4b9c1de224a843e54331d4b50fd34467277c))
* **utils:** improve Neo4jDriver with results handling ([823e8e8](https://github.com/aequitas-aod/aequitas-backend/commit/823e8e870a4db0241f931605dec979de16aa4f09))

### Dependency updates

* **deps:** update bitnami/kafka docker tag to v4 ([#106](https://github.com/aequitas-aod/aequitas-backend/issues/106)) ([50756e9](https://github.com/aequitas-aod/aequitas-backend/commit/50756e9a67a49a09fb877e05d1bbac19e8b404f7))

### Bug Fixes

* **build:** fix kafka env configuration ([311afb2](https://github.com/aequitas-aod/aequitas-backend/commit/311afb2d288f4073d56721db2f354a829feb1bca))
* **build:** fix kafka version to not migrate to Kraft ([c5ab68f](https://github.com/aequitas-aod/aequitas-backend/commit/c5ab68fd562e56f1ec9f4f97d0fd395cfb826241))
* **build:** trigger new release ([697a2f6](https://github.com/aequitas-aod/aequitas-backend/commit/697a2f6c01faf1a0a8b0b6fa2da9873ab1b5e615))
* **storage:** fix ProjectQuestion insertion with multiple projects in db, replace deprecated ID function of neo4j ([9a26ea5](https://github.com/aequitas-aod/aequitas-backend/commit/9a26ea5c075d31bd006081edb70a2ca5bf21e30e))

### General maintenance

* **release:** 0.35.0 [skip ci] ([7c602b0](https://github.com/aequitas-aod/aequitas-backend/commit/7c602b06b3d92290a2c93268c4ffd67633d2a305))

## [0.35.0](https://github.com/aequitas-aod/aequitas-backend/compare/v0.34.3...v0.35.0) (2025-03-30)

### Features

* **build:** add multiplatform image build ([e3bcaa4](https://github.com/aequitas-aod/aequitas-backend/commit/e3bcaa4ec80a0eb7c9385f77a191b81e126b05d9))
* **storage:** add distinction between GraphAnswer and ProjectAnswer in neo4j db, improve ProjectQuestion insertion retrieving its id in queries ([99ec4b9](https://github.com/aequitas-aod/aequitas-backend/commit/99ec4b9c1de224a843e54331d4b50fd34467277c))
* **utils:** improve Neo4jDriver with results handling ([823e8e8](https://github.com/aequitas-aod/aequitas-backend/commit/823e8e870a4db0241f931605dec979de16aa4f09))

### Bug Fixes

* **build:** fix kafka env configuration ([311afb2](https://github.com/aequitas-aod/aequitas-backend/commit/311afb2d288f4073d56721db2f354a829feb1bca))
* **build:** fix kafka version to not migrate to Kraft ([c5ab68f](https://github.com/aequitas-aod/aequitas-backend/commit/c5ab68fd562e56f1ec9f4f97d0fd395cfb826241))
* **storage:** fix ProjectQuestion insertion with multiple projects in db, replace deprecated ID function of neo4j ([9a26ea5](https://github.com/aequitas-aod/aequitas-backend/commit/9a26ea5c075d31bd006081edb70a2ca5bf21e30e))

## [0.34.3](https://github.com/aequitas-aod/aequitas-backend/compare/v0.34.2...v0.34.3) (2025-03-21)

### Dependency updates

* **deps:** update actions/setup-node action to v4.3.0 ([#101](https://github.com/aequitas-aod/aequitas-backend/issues/101)) ([9d309f2](https://github.com/aequitas-aod/aequitas-backend/commit/9d309f298d7bec3438e2610b1f0fc9d658769dfe))

### Bug Fixes

* **deps:** update dependency coverage to v7.7.1 ([#102](https://github.com/aequitas-aod/aequitas-backend/issues/102)) ([0f5aa1e](https://github.com/aequitas-aod/aequitas-backend/commit/0f5aa1ef2fca50d09f227dfae06320f831f20006))

## [0.34.2](https://github.com/aequitas-aod/aequitas-backend/compare/v0.34.1...v0.34.2) (2025-03-17)

### Dependency updates

* **deps:** update dependency poethepoet to v0.33.1 ([#99](https://github.com/aequitas-aod/aequitas-backend/issues/99)) ([681d8e0](https://github.com/aequitas-aod/aequitas-backend/commit/681d8e0600b66c3316e25d60229e31169ba4478a))
* **deps:** update dependency python to 3.13 ([#98](https://github.com/aequitas-aod/aequitas-backend/issues/98)) ([da3175c](https://github.com/aequitas-aod/aequitas-backend/commit/da3175c25e82caed1934d6666980f08ee3e3050e))

### Bug Fixes

* **deps:** update dependency coverage to v7.7.0 ([#100](https://github.com/aequitas-aod/aequitas-backend/issues/100)) ([7029d76](https://github.com/aequitas-aod/aequitas-backend/commit/7029d76253eb13a75da0d0d458ef6897f1dd1d09))

## [0.34.1](https://github.com/aequitas-aod/aequitas-backend/compare/v0.34.0...v0.34.1) (2025-03-10)

### Bug Fixes

* **resources:** update Detection question description ([108b022](https://github.com/aequitas-aod/aequitas-backend/commit/108b022f43290f8f1443cfaf2c00478499b4cc93))

## [0.34.0](https://github.com/aequitas-aod/aequitas-backend/compare/v0.33.2...v0.34.0) (2025-03-07)

### Features

* **projects:** add update context key without re-update whole context ([743f642](https://github.com/aequitas-aod/aequitas-backend/commit/743f6426d9441ab239e64132c62893ab5086c764))

## [0.33.2](https://github.com/aequitas-aod/aequitas-backend/compare/v0.33.1...v0.33.2) (2025-03-07)

### Bug Fixes

* **build:** fix backend url in docker compose ([16d26ea](https://github.com/aequitas-aod/aequitas-backend/commit/16d26ea7ba49fd4476c48575cbb4bc37f7581ec9))

## [0.33.1](https://github.com/aequitas-aod/aequitas-backend/compare/v0.33.0...v0.33.1) (2025-03-06)

### Dependency updates

* **deps:** update neo4j docker tag to v2025 ([#96](https://github.com/aequitas-aod/aequitas-backend/issues/96)) ([12df575](https://github.com/aequitas-aod/aequitas-backend/commit/12df5750cd209035e4e031d9bf5048ad460e0ac4))

### Bug Fixes

* **automation:** modify svg creations with new attribute, modify relative tests ([c92c662](https://github.com/aequitas-aod/aequitas-backend/commit/c92c662793fb3dc2fe78fa2d1f1e9c5a8e9cc823))
* **build:** fix neo4j image version ([48f78f0](https://github.com/aequitas-aod/aequitas-backend/commit/48f78f04642f2486e1b0357ebbab44613e6acdbd))

### Refactoring

* update questions yaml ([9ffa1b3](https://github.com/aequitas-aod/aequitas-backend/commit/9ffa1b34b94f42335075824712fd1eec895e60ce))

## [0.33.0](https://github.com/aequitas-aod/aequitas-backend/compare/v0.32.11...v0.33.0) (2025-03-03)

### Features

* update questions and answers descriptions ([c6aec09](https://github.com/aequitas-aod/aequitas-backend/commit/c6aec095d7cc097fe0791f534f2c316c87a60973))

### Dependency updates

* **deps:** update dependency poethepoet to v0.33.0 ([#95](https://github.com/aequitas-aod/aequitas-backend/issues/95)) ([56ce1a7](https://github.com/aequitas-aod/aequitas-backend/commit/56ce1a790e2c89663c5a4d0347d682b9262df0d1))

### Build and continuous integration

* fix neo4j version ([e70f841](https://github.com/aequitas-aod/aequitas-backend/commit/e70f841ab6ba5731b97ce577f0b01ace64284513))

## [0.32.11](https://github.com/aequitas-aod/aequitas-backend/compare/v0.32.10...v0.32.11) (2025-02-28)

### Bug Fixes

* **deps:** update dependency matplotlib to v3.10.1 ([#94](https://github.com/aequitas-aod/aequitas-backend/issues/94)) ([c73becb](https://github.com/aequitas-aod/aequitas-backend/commit/c73becb38c5de6007f841ae2ee1c1bade419c382))

## [0.32.10](https://github.com/aequitas-aod/aequitas-backend/compare/v0.32.9...v0.32.10) (2025-02-24)

### Bug Fixes

* **deps:** update dependency flask-cors to v5.0.1 ([#93](https://github.com/aequitas-aod/aequitas-backend/issues/93)) ([b92549e](https://github.com/aequitas-aod/aequitas-backend/commit/b92549eaaf823ecf4e16faba2f856648e9cdf4ef))

## [0.32.9](https://github.com/aequitas-aod/aequitas-backend/compare/v0.32.8...v0.32.9) (2025-02-21)

### Dependency updates

* **deps:** update dependency poetry to v2.1.0 ([#91](https://github.com/aequitas-aod/aequitas-backend/issues/91)) ([5a1b8b5](https://github.com/aequitas-aod/aequitas-backend/commit/5a1b8b516979f051b955af11683b1d722f652233))
* **deps:** update dependency poetry to v2.1.1 ([#92](https://github.com/aequitas-aod/aequitas-backend/issues/92)) ([ca38451](https://github.com/aequitas-aod/aequitas-backend/commit/ca384511f1ab6fb9e3d73e706bd5470e50735421))
* **deps:** update node.js to 22.14 ([#90](https://github.com/aequitas-aod/aequitas-backend/issues/90)) ([de9c690](https://github.com/aequitas-aod/aequitas-backend/commit/de9c69098e422bbb49eefd8bcf71b1c55fdef732))

### Documentation

* fix api specifications and architecture diagram ([2556627](https://github.com/aequitas-aod/aequitas-backend/commit/255662764a4123842257e5727729f5a7b1e8eaba))

### Build and continuous integration

* fix coverage report command to exclude test package ([4b215be](https://github.com/aequitas-aod/aequitas-backend/commit/4b215be01acf822168e4cec535b25187ad1974c1))

## [0.32.8](https://github.com/aequitas-aod/aequitas-backend/compare/v0.32.7...v0.32.8) (2025-02-11)

### Bug Fixes

* **deps:** update dependency coverage to v7.6.12 ([#89](https://github.com/aequitas-aod/aequitas-backend/issues/89)) ([c508602](https://github.com/aequitas-aod/aequitas-backend/commit/c508602445b1a08724484bd970c12dcd189a1641))

## [0.32.7](https://github.com/aequitas-aod/aequitas-backend/compare/v0.32.6...v0.32.7) (2025-02-10)

### Bug Fixes

* **deps:** update dependency neo4j to v5.28.1 ([#88](https://github.com/aequitas-aod/aequitas-backend/issues/88)) ([3ed44df](https://github.com/aequitas-aod/aequitas-backend/commit/3ed44df5e92421eeeea24d8a701eccb2b673b42f))

## [0.32.6](https://github.com/aequitas-aod/aequitas-backend/compare/v0.32.5...v0.32.6) (2025-02-08)

### Bug Fixes

* **deps:** update dependency coverage to v7.6.11 ([#87](https://github.com/aequitas-aod/aequitas-backend/issues/87)) ([d8ba392](https://github.com/aequitas-aod/aequitas-backend/commit/d8ba39241caede947a5f7d316dd2309d4bab645d))

## [0.32.5](https://github.com/aequitas-aod/aequitas-backend/compare/v0.32.4...v0.32.5) (2025-02-05)

### Dependency updates

* **deps:** update actions/setup-node action to v4.2.0 ([#84](https://github.com/aequitas-aod/aequitas-backend/issues/84)) ([44dfb8d](https://github.com/aequitas-aod/aequitas-backend/commit/44dfb8d9717e5b72a3fa07488db37ba9680c7437))
* **deps:** update dependency black to v25 ([#85](https://github.com/aequitas-aod/aequitas-backend/issues/85)) ([1c8ca48](https://github.com/aequitas-aod/aequitas-backend/commit/1c8ca4857b5bd17356edbb3b208b65c2d5bd3284))
* **deps:** update dependency poethepoet to v0.32.2 ([#83](https://github.com/aequitas-aod/aequitas-backend/issues/83)) ([e1b4f08](https://github.com/aequitas-aod/aequitas-backend/commit/e1b4f08f8b97becb5a909eda156279bde7cf8038))

### Bug Fixes

* **deps:** update dependency neo4j to v5.28.0 ([#86](https://github.com/aequitas-aod/aequitas-backend/issues/86)) ([2c5a244](https://github.com/aequitas-aod/aequitas-backend/commit/2c5a244bbc30f69a62615d679dbdd9c56d449437))

## [0.32.4](https://github.com/aequitas-aod/aequitas-backend/compare/v0.32.3...v0.32.4) (2025-01-26)

### Bug Fixes

* change columns names in preprocessed_lfr_results ([f87d0aa](https://github.com/aequitas-aod/aequitas-backend/commit/f87d0aad38ae78051ad389096c34cdf6315bac28))

## [0.32.3](https://github.com/aequitas-aod/aequitas-backend/compare/v0.32.2...v0.32.3) (2025-01-26)

### Bug Fixes

* use insecure flask command instead of waitress-serve ([6eaead7](https://github.com/aequitas-aod/aequitas-backend/commit/6eaead7b6bec9fa7f1cd3c2a5d604c4711bbd59e))

## [0.32.2](https://github.com/aequitas-aod/aequitas-backend/compare/v0.32.1...v0.32.2) (2025-01-25)

### Bug Fixes

* add predictions_head and fix hyperparameters in flow ([763b292](https://github.com/aequitas-aod/aequitas-backend/commit/763b29254d8491faf7b43064ef9d84c4b91a7473))
* format code and modify docker compose ([5c2428f](https://github.com/aequitas-aod/aequitas-backend/commit/5c2428f62b9f44d758eefede591a72e2db12d97b))
* mock lfr result in case of ULL ([b7c3184](https://github.com/aequitas-aod/aequitas-backend/commit/b7c31841dd881839cd13fb183ca4a42f697b5d13))

## [0.32.1](https://github.com/aequitas-aod/aequitas-backend/compare/v0.32.0...v0.32.1) (2025-01-25)

### Bug Fixes

* fix delete all questions, improve dockerfile and setup script, do not run script during tests ([1a2b6b8](https://github.com/aequitas-aod/aequitas-backend/commit/1a2b6b85d83aff46965d85439dcfb7ffcd089631))

## [0.32.0](https://github.com/aequitas-aod/aequitas-backend/compare/v0.31.0...v0.32.0) (2025-01-25)

### Features

* add script for setup db from server ([3696635](https://github.com/aequitas-aod/aequitas-backend/commit/3696635ebd7e40a855d3d05a013e84d03159c45a))
* **graph:** add delete all questions feature ([0b0119f](https://github.com/aequitas-aod/aequitas-backend/commit/0b0119fe9d76ada8157235c127599d7d19c13e74))
* support creation of project with custom code ([49e83ae](https://github.com/aequitas-aod/aequitas-backend/commit/49e83ae702295b08ced0a312c560014dec6b621b))

### Bug Fixes

* init file generation with just general context, setup script filling db with questions ([035b82a](https://github.com/aequitas-aod/aequitas-backend/commit/035b82a764eb5dddb3be3be3a885e26eb74b2e9b))
* setup db script ([279cfe0](https://github.com/aequitas-aod/aequitas-backend/commit/279cfe07d6cf95b8db8ba622b7073fbc2e6ca962))

### Refactoring

* improve use of pythonize ([9c2e7f3](https://github.com/aequitas-aod/aequitas-backend/commit/9c2e7f3844796ec9e52e9f62387ec76f17d38cd1))

## [0.31.0](https://github.com/aequitas-aod/aequitas-backend/compare/v0.30.3...v0.31.0) (2025-01-24)

### Features

* bunch of fixes to keys generation ([#82](https://github.com/aequitas-aod/aequitas-backend/issues/82)). Now preprocessing is actually supported ([ce9c750](https://github.com/aequitas-aod/aequitas-backend/commit/ce9c75043ada8b9e37dc5c4b035bb818b05da671))

## [0.30.3](https://github.com/aequitas-aod/aequitas-backend/compare/v0.30.2...v0.30.3) (2025-01-24)

### Bug Fixes

* **automation:** fix NaN value in proxy suggestions generation ([a0aeab8](https://github.com/aequitas-aod/aequitas-backend/commit/a0aeab8f5275368f9e8a5b93c4346e4dbca1ea48))

## [0.30.2](https://github.com/aequitas-aod/aequitas-backend/compare/v0.30.1...v0.30.2) (2025-01-24)

### Bug Fixes

* change code of Custom answer ([81724f6](https://github.com/aequitas-aod/aequitas-backend/commit/81724f68b136c72722c69f268ee184f5548de93c))

## [0.30.1](https://github.com/aequitas-aod/aequitas-backend/compare/v0.30.0...v0.30.1) (2025-01-24)

### Bug Fixes

* **deps:** update dependency pydantic to v2.10.6 ([#81](https://github.com/aequitas-aod/aequitas-backend/issues/81)) ([9a64d16](https://github.com/aequitas-aod/aequitas-backend/commit/9a64d16f90f22c76e6bbdceef905c5b3fd649674))

## [0.30.0](https://github.com/aequitas-aod/aequitas-backend/compare/v0.29.2...v0.30.0) (2025-01-23)

### Features

* handle no proceprocessing case ([f81838e](https://github.com/aequitas-aod/aequitas-backend/commit/f81838ea3c49eaaa8887bee5c8de1fff91cf24ec))

## [0.29.2](https://github.com/aequitas-aod/aequitas-backend/compare/v0.29.1...v0.29.2) (2025-01-23)

### Bug Fixes

* **automation:** fix target features suggestion ([3222818](https://github.com/aequitas-aod/aequitas-backend/commit/3222818b33c94200df9abef820da466a90e05e6c))

## [0.29.1](https://github.com/aequitas-aod/aequitas-backend/compare/v0.29.0...v0.29.1) (2025-01-23)

### Bug Fixes

* **resources:** fix name of a SPD fairness metric ([be6abc7](https://github.com/aequitas-aod/aequitas-backend/commit/be6abc75bc685915277f62ccd6335e406d3e141f))

## [0.29.0](https://github.com/aequitas-aod/aequitas-backend/compare/v0.28.4...v0.29.0) (2025-01-23)

### Features

* inprocessing and testing ([89c0b37](https://github.com/aequitas-aod/aequitas-backend/commit/89c0b37ed93b4da6990484da30ad18b4c0a33814))

## [0.28.4](https://github.com/aequitas-aod/aequitas-backend/compare/v0.28.3...v0.28.4) (2025-01-23)

### Bug Fixes

* **resources:** fix LFR hyperparameters ([5d0839d](https://github.com/aequitas-aod/aequitas-backend/commit/5d0839db7248adf197ef19ab37c242e225c84a75))

## [0.28.3](https://github.com/aequitas-aod/aequitas-backend/compare/v0.28.2...v0.28.3) (2025-01-23)

### Dependency updates

* **deps:** update npm to v11 ([#78](https://github.com/aequitas-aod/aequitas-backend/issues/78)) ([df588ff](https://github.com/aequitas-aod/aequitas-backend/commit/df588ff41f62d88db3769de48727020061a49d4f))

### Bug Fixes

* **automation:** handle infinity value in _pythonize function ([9ad7247](https://github.com/aequitas-aod/aequitas-backend/commit/9ad7247d8a8392be8178c370274e2af85c9a9b07))

## [0.28.2](https://github.com/aequitas-aod/aequitas-backend/compare/v0.28.1...v0.28.2) (2025-01-22)

### Bug Fixes

* **ci:** semantic-release-configuration ([2915ea0](https://github.com/aequitas-aod/aequitas-backend/commit/2915ea0d3f11493ea9a6a248e0bbe50f1f179d6c))
