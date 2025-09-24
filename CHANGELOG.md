## [1.13.3](https://github.com/aequitas-aod/aequitas-backend/compare/v1.13.2...v1.13.3) (2025-09-24)

### Bug Fixes

* update stats key in order to keep updated sensitive and target features ([5b8d810](https://github.com/aequitas-aod/aequitas-backend/commit/5b8d8108c9799feda2bbfc6d2f5db4bf8c4398c0))

## [1.13.2](https://github.com/aequitas-aod/aequitas-backend/compare/v1.13.1...v1.13.2) (2025-09-24)

### Bug Fixes

* fix polarization results csv ([2865954](https://github.com/aequitas-aod/aequitas-backend/commit/2865954c41b88b2830ec1c7f731936f128cab7a2))

## [1.13.1](https://github.com/aequitas-aod/aequitas-backend/compare/v1.13.0...v1.13.1) (2025-09-24)

### Bug Fixes

* fix key generation in polarization removing incremental numbers, update report creation ([5385b8c](https://github.com/aequitas-aod/aequitas-backend/commit/5385b8c82aa89bdfe9e739b9a66f87fc8d677e21))

## [1.13.0](https://github.com/aequitas-aod/aequitas-backend/compare/v1.12.0...v1.13.0) (2025-09-23)

### Features

* add results for polarization of image dataset, update polarized datasets in questions ([3388988](https://github.com/aequitas-aod/aequitas-backend/commit/33889884bc4c0e9f44c2a4b66a2f76ba8e4f6cfe))

## [1.12.0](https://github.com/aequitas-aod/aequitas-backend/compare/v1.11.2...v1.12.0) (2025-09-22)

### Features

* update report with multiple stress tests ([45b9bee](https://github.com/aequitas-aod/aequitas-backend/commit/45b9beeea85259fe71abbb742f125234fcdb6dca))

## [1.11.2](https://github.com/aequitas-aod/aequitas-backend/compare/v1.11.1...v1.11.2) (2025-09-22)

### Dependency updates

* **deps:** update dependency poetry to v2.2.1 ([#171](https://github.com/aequitas-aod/aequitas-backend/issues/171)) ([bced1b4](https://github.com/aequitas-aod/aequitas-backend/commit/bced1b4c61e032c3b935cad5106e4f7f1bbc159d))

### Bug Fixes

* **deps:** update dependency coverage to v7.10.7 ([#172](https://github.com/aequitas-aod/aequitas-backend/issues/172)) ([1d9c7f3](https://github.com/aequitas-aod/aequitas-backend/commit/1d9c7f3dfe987ba51d886d6c1b6c233829beab6d))

## [1.11.1](https://github.com/aequitas-aod/aequitas-backend/compare/v1.11.0...v1.11.1) (2025-09-19)

### Dependency updates

* **deps:** update dependency black to v25.9.0 ([#169](https://github.com/aequitas-aod/aequitas-backend/issues/169)) ([c240c7c](https://github.com/aequitas-aod/aequitas-backend/commit/c240c7c694d15575c87c1233b95364e6c133560f))

### Bug Fixes

* **deps:** update dependency reportlab to v4.4.4 ([#170](https://github.com/aequitas-aod/aequitas-backend/issues/170)) ([29193e4](https://github.com/aequitas-aod/aequitas-backend/commit/29193e41d787111551c36464bebca26a9cd4c5e7))

## [1.11.0](https://github.com/aequitas-aod/aequitas-backend/compare/v1.10.0...v1.11.0) (2025-09-18)

### Features

* add incremental id for stress test again ([f51130b](https://github.com/aequitas-aod/aequitas-backend/commit/f51130b6caaef3a61fc9d7c4231aedd0977d8819))

## [1.10.0](https://github.com/aequitas-aod/aequitas-backend/compare/v1.9.2...v1.10.0) (2025-09-17)

### Features

* fix get project question by id, finish update project question ([17c2767](https://github.com/aequitas-aod/aequitas-backend/commit/17c2767b5e8a7b9fc3d546a35bc255e8079076d8))

### Dependency updates

* **deps:** update dependency poetry to v2.2.0 ([#168](https://github.com/aequitas-aod/aequitas-backend/issues/168)) ([ec5177a](https://github.com/aequitas-aod/aequitas-backend/commit/ec5177a946d073ea9c58df0f03231c484b3aef08))

### Bug Fixes

* fix update project question query ([5e4b780](https://github.com/aequitas-aod/aequitas-backend/commit/5e4b78090c57211d0405a680eaa2f0480b3e44cb))

### Performance improvements

* improve paths in queries ([d0ee81a](https://github.com/aequitas-aod/aequitas-backend/commit/d0ee81a3788236843ffefab7fe6913551f4ee6f2))

## [1.9.2](https://github.com/aequitas-aod/aequitas-backend/compare/v1.9.1...v1.9.2) (2025-09-14)

### Bug Fixes

* **deps:** update dependency pydantic to v2.11.9 ([#167](https://github.com/aequitas-aod/aequitas-backend/issues/167)) ([c2354a1](https://github.com/aequitas-aod/aequitas-backend/commit/c2354a1027da0537a82f625975627bcf0a6847b2))

## [1.9.1](https://github.com/aequitas-aod/aequitas-backend/compare/v1.9.0...v1.9.1) (2025-09-11)

### Bug Fixes

* fix test because current_dataset is no longer updated ([3897eac](https://github.com/aequitas-aod/aequitas-backend/commit/3897eaceb95bb32401e3e8a2ca2f1ea6527a1df2))

### Refactoring

* **automation:** remove update of current_dataset in PreProcessing ([565f3d3](https://github.com/aequitas-aod/aequitas-backend/commit/565f3d313498b85d526529656be2256b02b45c50))

## [1.9.0](https://github.com/aequitas-aod/aequitas-backend/compare/v1.8.7...v1.9.0) (2025-09-10)

### Features

* setup new metrics creation for polarization ([3fbbd12](https://github.com/aequitas-aod/aequitas-backend/commit/3fbbd12d76abb32363ca178c9ff69875139ac1e4))

## [1.8.7](https://github.com/aequitas-aod/aequitas-backend/compare/v1.8.6...v1.8.7) (2025-09-09)

### Bug Fixes

* remove mitigation answers in summary questions ([688e4ee](https://github.com/aequitas-aod/aequitas-backend/commit/688e4ee002a22224fa9b25a26788dfec619d3fd1))

## [1.8.6](https://github.com/aequitas-aod/aequitas-backend/compare/v1.8.5...v1.8.6) (2025-09-09)

### Dependency updates

* **deps:** update actions/checkout action to v5 ([#157](https://github.com/aequitas-aod/aequitas-backend/issues/157)) ([0b83516](https://github.com/aequitas-aod/aequitas-backend/commit/0b83516bdd771b04cf588bcda95c825e6f1c8211))
* **deps:** update actions/setup-python action to v6 ([#165](https://github.com/aequitas-aod/aequitas-backend/issues/165)) ([a7b7a60](https://github.com/aequitas-aod/aequitas-backend/commit/a7b7a606a4f9881daa5e1f0d14ac3058c6e852aa))
* **deps:** update dependency poethepoet to v0.37.0 ([#158](https://github.com/aequitas-aod/aequitas-backend/issues/158)) ([62728d2](https://github.com/aequitas-aod/aequitas-backend/commit/62728d21bf1cca568ed57ede841d2e8f18f68bc7))
* **deps:** update node.js to 22.19 ([#163](https://github.com/aequitas-aod/aequitas-backend/issues/163)) ([2e3c667](https://github.com/aequitas-aod/aequitas-backend/commit/2e3c6678db8688c9b6bcc935f460d59506bb9c36))

### Bug Fixes

* **deps:** update dependency scikit-learn to v1.7.2 ([#166](https://github.com/aequitas-aod/aequitas-backend/issues/166)) ([a666947](https://github.com/aequitas-aod/aequitas-backend/commit/a6669472ae9afe69d3c13d628729c6f0b9c77717))

## [1.8.5](https://github.com/aequitas-aod/aequitas-backend/compare/v1.8.4...v1.8.5) (2025-09-04)

### Bug Fixes

* **deps:** update dependency requests to v2.32.5 ([#159](https://github.com/aequitas-aod/aequitas-backend/issues/159)) ([8bb52da](https://github.com/aequitas-aod/aequitas-backend/commit/8bb52dad4f007228d008412abd4c6822eecca941))

## [1.8.4](https://github.com/aequitas-aod/aequitas-backend/compare/v1.8.3...v1.8.4) (2025-09-04)

### Bug Fixes

* **deps:** update dependency pandas to v2.3.2 ([#161](https://github.com/aequitas-aod/aequitas-backend/issues/161)) ([04323aa](https://github.com/aequitas-aod/aequitas-backend/commit/04323aa6a80c4c0dc1ca720165620ef95a1ee73d))

## [1.8.3](https://github.com/aequitas-aod/aequitas-backend/compare/v1.8.2...v1.8.3) (2025-09-04)

### Dependency updates

* **deps:** update actions/setup-node action to v5 ([#164](https://github.com/aequitas-aod/aequitas-backend/issues/164)) ([b0bf2ab](https://github.com/aequitas-aod/aequitas-backend/commit/b0bf2ab9bc4276f50bab225f62eaa093d431bde3))

### Bug Fixes

* **deps:** update dependency matplotlib to v3.10.6 ([#162](https://github.com/aequitas-aod/aequitas-backend/issues/162)) ([941e27c](https://github.com/aequitas-aod/aequitas-backend/commit/941e27c1f03b9031337a3faade7549caf62d4024))
* **report:** fix generation of report ([3d1430e](https://github.com/aequitas-aod/aequitas-backend/commit/3d1430e3371086feb3c65b166194263e2154ff4c))

## [1.8.2](https://github.com/aequitas-aod/aequitas-backend/compare/v1.8.1...v1.8.2) (2025-09-02)

### Bug Fixes

* **deps:** update dependency coverage to v7.10.6 ([#156](https://github.com/aequitas-aod/aequitas-backend/issues/156)) ([28fd8b1](https://github.com/aequitas-aod/aequitas-backend/commit/28fd8b1250254f72867abc2c3f1c806152674243))

## [1.8.1](https://github.com/aequitas-aod/aequitas-backend/compare/v1.8.0...v1.8.1) (2025-09-01)

### Bug Fixes

* **deps:** update dependency flask to v3.1.2 ([#160](https://github.com/aequitas-aod/aequitas-backend/issues/160)) ([b895c13](https://github.com/aequitas-aod/aequitas-backend/commit/b895c13499d63467655008a0a4d465e2238077c7))

## [1.8.0](https://github.com/aequitas-aod/aequitas-backend/compare/v1.7.5...v1.8.0) (2025-09-01)

### Features

* move polarization to ad-hoc script ([d49664b](https://github.com/aequitas-aod/aequitas-backend/commit/d49664b2f2bd78900557e3b247dea13ac45493ea))

### Dependency updates

* **deps:** update dependency poetry to v2.1.4 ([#155](https://github.com/aequitas-aod/aequitas-backend/issues/155)) ([59bbc73](https://github.com/aequitas-aod/aequitas-backend/commit/59bbc73a234ca34f75a057da1cad3d72d4914ebc))

### Bug Fixes

* fix timeout to retrieve keys form context ([7c49b73](https://github.com/aequitas-aod/aequitas-backend/commit/7c49b73ec3649b927a7bc17f72bf2730906cd65f))
* move polarization process afterwards ([a59b986](https://github.com/aequitas-aod/aequitas-backend/commit/a59b986bdc56206e842b88c87298bbf8b8483bb2))

## [1.7.5](https://github.com/aequitas-aod/aequitas-backend/compare/v1.7.4...v1.7.5) (2025-08-04)

### Bug Fixes

* fix questionnaire reactions trigger using question codes ([9efb759](https://github.com/aequitas-aod/aequitas-backend/commit/9efb759262a04454c2296e9d8377e0f37cab9d43))

## [1.7.4](https://github.com/aequitas-aod/aequitas-backend/compare/v1.7.3...v1.7.4) (2025-08-04)

### Dependency updates

* **deps:** update node.js to 22.18 ([#153](https://github.com/aequitas-aod/aequitas-backend/issues/153)) ([cdcc774](https://github.com/aequitas-aod/aequitas-backend/commit/cdcc77427fccce09a19779a543b67a587cd6284d))

### Bug Fixes

* **deps:** update dependency coverage to v7.10.2 ([#154](https://github.com/aequitas-aod/aequitas-backend/issues/154)) ([b38c30d](https://github.com/aequitas-aod/aequitas-backend/commit/b38c30d0038efb64997a4d0601b301fb5ddcfe1b))

## [1.7.3](https://github.com/aequitas-aod/aequitas-backend/compare/v1.7.2...v1.7.3) (2025-08-01)

### Bug Fixes

* **deps:** update dependency matplotlib to v3.10.5 ([#152](https://github.com/aequitas-aod/aequitas-backend/issues/152)) ([aaa3c26](https://github.com/aequitas-aod/aequitas-backend/commit/aaa3c26a142703ebf23d49347c5be55c9425a154))

## [1.7.2](https://github.com/aequitas-aod/aequitas-backend/compare/v1.7.1...v1.7.2) (2025-07-30)

### Bug Fixes

* **deps:** update dependency neo4j to v5.28.2 ([#151](https://github.com/aequitas-aod/aequitas-backend/issues/151)) ([69e96da](https://github.com/aequitas-aod/aequitas-backend/commit/69e96da0ce4ba8dd72d27177c51026fb25b5fa58))

## [1.7.1](https://github.com/aequitas-aod/aequitas-backend/compare/v1.7.0...v1.7.1) (2025-07-30)

### Bug Fixes

* fix import ([8c23912](https://github.com/aequitas-aod/aequitas-backend/commit/8c2391242615eb12314c29c4136004df83753578))

## [1.7.0](https://github.com/aequitas-aod/aequitas-backend/compare/v1.6.3...v1.7.0) (2025-07-30)

### Features

* add report creation ([15a52e3](https://github.com/aequitas-aod/aequitas-backend/commit/15a52e3c98cd0e3b76765c49d5da0dd1b423f1c6))

### Bug Fixes

* add detection graph to report ([9bca41e](https://github.com/aequitas-aod/aequitas-backend/commit/9bca41ebc9bfcf737075aa40ffc0aea981326f34))

### General maintenance

* add description to image preprocessing algorithm ([ccb3cf0](https://github.com/aequitas-aod/aequitas-backend/commit/ccb3cf06ba9a10fed818e4e55157af0caaf4468d))
* add metrics after mitigation in pdf report ([fa91480](https://github.com/aequitas-aod/aequitas-backend/commit/fa914808422f93947888042143e7274ba688605d))
* replace print with logger ([47a861e](https://github.com/aequitas-aod/aequitas-backend/commit/47a861e9ce6f3dfbb5c48c103ed2c25f6dbb9383))

## [1.6.3](https://github.com/aequitas-aod/aequitas-backend/compare/v1.6.2...v1.6.3) (2025-07-27)

### Bug Fixes

* **deps:** update dependency coverage to v7.10.1 ([#150](https://github.com/aequitas-aod/aequitas-backend/issues/150)) ([48e52b0](https://github.com/aequitas-aod/aequitas-backend/commit/48e52b0f2b94d41eb39989e7581d053043efa62a))

## [1.6.2](https://github.com/aequitas-aod/aequitas-backend/compare/v1.6.1...v1.6.2) (2025-07-25)

### Bug Fixes

* **deps:** update dependency coverage to v7.10.0 ([#149](https://github.com/aequitas-aod/aequitas-backend/issues/149)) ([78e7e41](https://github.com/aequitas-aod/aequitas-backend/commit/78e7e4158472115fd6ffb66de7a1638744748f45))

## [1.6.1](https://github.com/aequitas-aod/aequitas-backend/compare/v1.6.0...v1.6.1) (2025-07-24)

### Bug Fixes

* fix plot with wrong standard deviations ([a115796](https://github.com/aequitas-aod/aequitas-backend/commit/a115796421df91307f3602c9afdf95dcc3726c15))

## [1.6.0](https://github.com/aequitas-aod/aequitas-backend/compare/v1.5.2...v1.6.0) (2025-07-24)

### Features

* add polarization plots for skin disease dataset ([ffca903](https://github.com/aequitas-aod/aequitas-backend/commit/ffca903a7b72962b966026b8be28f73528deff84))

## [1.5.2](https://github.com/aequitas-aod/aequitas-backend/compare/v1.5.1...v1.5.2) (2025-07-24)

### Bug Fixes

* naming of StableDiffusionBasedDataAugmentation ([c9f78c6](https://github.com/aequitas-aod/aequitas-backend/commit/c9f78c6440db27135cdfa5fa0bc0b4ad72ff1c22))
* preprocessing metrics for stable diffusion ([2b8c50b](https://github.com/aequitas-aod/aequitas-backend/commit/2b8c50b9dd7e5730ecba1a27e8f05410a25399df))
* skin-desease dataset's size and rows metadata ([329251c](https://github.com/aequitas-aod/aequitas-backend/commit/329251cb0359ae401107c2d7477023b9ee01dbd7))

## [1.5.1](https://github.com/aequitas-aod/aequitas-backend/compare/v1.5.0...v1.5.1) (2025-07-24)

### Bug Fixes

* fix image dataset metadata ([c25d354](https://github.com/aequitas-aod/aequitas-backend/commit/c25d3547d2798f698a9e91d1d97782195303c2c6))
* regenerate context ([df6d3ab](https://github.com/aequitas-aod/aequitas-backend/commit/df6d3ab0370f0907b9dc234db850a21ffc3d1852))
* regenerate context ([073a8a0](https://github.com/aequitas-aod/aequitas-backend/commit/073a8a0c86f04e0457ca25d233cf81b6bf13ca04))

## [1.5.0](https://github.com/aequitas-aod/aequitas-backend/compare/v1.4.1...v1.5.0) (2025-07-24)

### Features

* add stable diffusion hyper-parameters ([1f8d941](https://github.com/aequitas-aod/aequitas-backend/commit/1f8d941feb38d99b0fc592d7b3e91147ee845182))
* support for skin disease usecase ([b5707b7](https://github.com/aequitas-aod/aequitas-backend/commit/b5707b7fc320c38da672bb5c27811bf470980c01))

## [1.4.1](https://github.com/aequitas-aod/aequitas-backend/compare/v1.4.0...v1.4.1) (2025-07-18)

### Dependency updates

* **deps:** update dependency python-on-whales to v0.78.0 ([#147](https://github.com/aequitas-aod/aequitas-backend/issues/147)) ([d5122e8](https://github.com/aequitas-aod/aequitas-backend/commit/d5122e884ff05ded788d75063276caab791f867f))

### Bug Fixes

* **deps:** update dependency scikit-learn to v1.7.1 ([#148](https://github.com/aequitas-aod/aequitas-backend/issues/148)) ([e735896](https://github.com/aequitas-aod/aequitas-backend/commit/e735896c95b28ed9953b7f93fc70d6f68f1e72a6))

## [1.4.0](https://github.com/aequitas-aod/aequitas-backend/compare/v1.3.0...v1.4.0) (2025-07-10)

### Features

* add adecco datasets ([c6474e1](https://github.com/aequitas-aod/aequitas-backend/commit/c6474e1bcd98f487b14d4748ec6b982a055e1ecb))
* add polarization stuffs in InProcessing and setup PolarizationProcessing ([152b3b3](https://github.com/aequitas-aod/aequitas-backend/commit/152b3b3dcbc5f98c0b07b454e0871bb32a99fefb))
* add polarized adecco dataset ([898b9df](https://github.com/aequitas-aod/aequitas-backend/commit/898b9df568b0312f106b1987980f754fccc646ef))

## [1.3.0](https://github.com/aequitas-aod/aequitas-backend/compare/v1.2.0...v1.3.0) (2025-07-09)

### Features

* **automation:** add test dataset selection reaction ([d2c9d91](https://github.com/aequitas-aod/aequitas-backend/commit/d2c9d9170e47cdc8fe51b1a9c83ea7b4332c073f))

## [1.2.0](https://github.com/aequitas-aod/aequitas-backend/compare/v1.1.0...v1.2.0) (2025-07-09)

### Features

* add mitigation algorithm for image dataset ([025829a](https://github.com/aequitas-aod/aequitas-backend/commit/025829abac222007b9f6e5958ff617ce2333f84e))
* **context:** add post-processing hyperparameters ([8d97a76](https://github.com/aequitas-aod/aequitas-backend/commit/8d97a76b6e7c7ff9aac4ebe749e14b6574e8328f))

### Refactoring

* update adecco dataset name ([83b3705](https://github.com/aequitas-aod/aequitas-backend/commit/83b3705cccf34f2ecd20755e332fbfaff802bb1c))

## [1.1.0](https://github.com/aequitas-aod/aequitas-backend/compare/v1.0.2...v1.1.0) (2025-07-09)

### Features

* **datasets:** add adecco dataset ([29a1d78](https://github.com/aequitas-aod/aequitas-backend/commit/29a1d78fd61c04d678acc4a6bc03f866d304a93e))

## [1.0.2](https://github.com/aequitas-aod/aequitas-backend/compare/v1.0.1...v1.0.2) (2025-07-08)

### Bug Fixes

* **deps:** update dependency pandas to v2.3.1 ([#146](https://github.com/aequitas-aod/aequitas-backend/issues/146)) ([51e3084](https://github.com/aequitas-aod/aequitas-backend/commit/51e30841dda7ce8d55afe31609999dcd9e4073eb))

## [1.0.1](https://github.com/aequitas-aod/aequitas-backend/compare/v1.0.0...v1.0.1) (2025-07-04)

### Bug Fixes

* **deps:** update dependency coverage to v7.9.2 ([#145](https://github.com/aequitas-aod/aequitas-backend/issues/145)) ([3b4b233](https://github.com/aequitas-aod/aequitas-backend/commit/3b4b233e6b17f88e0064785d583f22b2d22c11bb))

## [1.0.0](https://github.com/aequitas-aod/aequitas-backend/compare/v0.41.0...v1.0.0) (2025-07-04)

### ⚠ BREAKING CHANGES

* change quoteChar for csv data

### Dependency updates

* **deps:** update dependency poethepoet to v0.36.0 ([#144](https://github.com/aequitas-aod/aequitas-backend/issues/144)) ([fa68445](https://github.com/aequitas-aod/aequitas-backend/commit/fa68445027c858c9a0215a16f425709013e7a1bd))

### Refactoring

* change quoteChar for csv data ([c323e26](https://github.com/aequitas-aod/aequitas-backend/commit/c323e2659ea6b8babe427097476a59eabe91feb7))

## [0.41.0](https://github.com/aequitas-aod/aequitas-backend/compare/v0.40.3...v0.41.0) (2025-06-26)

### Features

* add akkodis results ([fb2ccf6](https://github.com/aequitas-aod/aequitas-backend/commit/fb2ccf634cd435bbf335b445e78e298ae88300e6))
* update akkodis dataset ([cd316a7](https://github.com/aequitas-aod/aequitas-backend/commit/cd316a791f33cfee5019c5f28f67e42d622bf83f))

### Dependency updates

* **deps:** update node.js to 22.17 ([#143](https://github.com/aequitas-aod/aequitas-backend/issues/143)) ([c440f97](https://github.com/aequitas-aod/aequitas-backend/commit/c440f97d6400b1a2a50b5bbf9419aaf7c23c0e5b))

### Bug Fixes

* fix akkodis dataset for demo ([92a4534](https://github.com/aequitas-aod/aequitas-backend/commit/92a45347699a6097467a0ddc8bd82ec2c954bf57))

### General maintenance

* fix formatting ([3a48b07](https://github.com/aequitas-aod/aequitas-backend/commit/3a48b075cd8e4b601a96acec0a2d8e5c3459acc5))

## [0.40.3](https://github.com/aequitas-aod/aequitas-backend/compare/v0.40.2...v0.40.3) (2025-06-24)

### Bug Fixes

* **deps:** update dependency python-dotenv to v1.1.1 ([#111](https://github.com/aequitas-aod/aequitas-backend/issues/111)) ([2191fe2](https://github.com/aequitas-aod/aequitas-backend/commit/2191fe2499217524973f25cebf92228edd4bda07))

## [0.40.2](https://github.com/aequitas-aod/aequitas-backend/compare/v0.40.1...v0.40.2) (2025-06-23)

### Bug Fixes

* **deps:** update dependency aequitas-fairlib to v2.8.2 ([#142](https://github.com/aequitas-aod/aequitas-backend/issues/142)) ([845ba03](https://github.com/aequitas-aod/aequitas-backend/commit/845ba03e757e7378d20e0b9863c38e2d84cfe661))

## [0.40.1](https://github.com/aequitas-aod/aequitas-backend/compare/v0.40.0...v0.40.1) (2025-06-21)

### Dependency updates

* **deps:** add aequitas-fairlib ([c367ad6](https://github.com/aequitas-aod/aequitas-backend/commit/c367ad61ffa42ec7151f7aa6cdb26c073aaca07c))

### Bug Fixes

* **deps:** update dependency aequitas-fairlib to v2.8.1 ([#141](https://github.com/aequitas-aod/aequitas-backend/issues/141)) ([d6679a1](https://github.com/aequitas-aod/aequitas-backend/commit/d6679a1d6e4ecc61cbd44a262be605b354013420))

## [0.40.0](https://github.com/aequitas-aod/aequitas-backend/compare/v0.39.7...v0.40.0) (2025-06-19)

### Features

* add Akkodis Dataset ([2dd604e](https://github.com/aequitas-aod/aequitas-backend/commit/2dd604e95d16ff6421887fc1a2b82abdc3c5b02c))

### Dependency updates

* **deps:** update docker/setup-buildx-action action to v3.11.1 ([#140](https://github.com/aequitas-aod/aequitas-backend/issues/140)) ([c449f7e](https://github.com/aequitas-aod/aequitas-backend/commit/c449f7ed2179626a80e0a5bd75a38ba54af4b9e6))

## [0.39.7](https://github.com/aequitas-aod/aequitas-backend/compare/v0.39.6...v0.39.7) (2025-06-18)

### Dependency updates

* **deps:** update docker/setup-buildx-action action to v3.11.0 ([#139](https://github.com/aequitas-aod/aequitas-backend/issues/139)) ([ecb81f3](https://github.com/aequitas-aod/aequitas-backend/commit/ecb81f3914cb9ed1baa8e0319352b3a31ccd2231))

### Bug Fixes

* change name of Ull dataset ([ad49f60](https://github.com/aequitas-aod/aequitas-backend/commit/ad49f608a103f61d8b48d8e1a98c80f59fd5e2eb))
* fix upload of csv with commas, fix ULL default dataset, fix flow of mitigation ([42ba6a0](https://github.com/aequitas-aod/aequitas-backend/commit/42ba6a08bf2671ba915299302d3ed7da335ad8b9))
* trigger new release ([cce6beb](https://github.com/aequitas-aod/aequitas-backend/commit/cce6beb54d92884e297d723f8f767015272e44d8))

### General maintenance

* **release:** 0.39.7 [skip ci] ([8414ad2](https://github.com/aequitas-aod/aequitas-backend/commit/8414ad208e039cfd8471ad89d589f4913b997a79)), closes [#139](https://github.com/aequitas-aod/aequitas-backend/issues/139)

## [0.39.7](https://github.com/aequitas-aod/aequitas-backend/compare/v0.39.6...v0.39.7) (2025-06-17)

### Dependency updates

* **deps:** update docker/setup-buildx-action action to v3.11.0 ([#139](https://github.com/aequitas-aod/aequitas-backend/issues/139)) ([ecb81f3](https://github.com/aequitas-aod/aequitas-backend/commit/ecb81f3914cb9ed1baa8e0319352b3a31ccd2231))

### Bug Fixes

* fix upload of csv with commas, fix ULL default dataset, fix flow of mitigation ([42ba6a0](https://github.com/aequitas-aod/aequitas-backend/commit/42ba6a08bf2671ba915299302d3ed7da335ad8b9))

## [0.39.6](https://github.com/aequitas-aod/aequitas-backend/compare/v0.39.5...v0.39.6) (2025-06-14)

### Bug Fixes

* **deps:** update dependency pydantic to v2.11.7 ([#138](https://github.com/aequitas-aod/aequitas-backend/issues/138)) ([98766d5](https://github.com/aequitas-aod/aequitas-backend/commit/98766d545cbc4c7d7bab81d04ca5b03c6aef7dba))

## [0.39.5](https://github.com/aequitas-aod/aequitas-backend/compare/v0.39.4...v0.39.5) (2025-06-14)

### Bug Fixes

* **deps:** update dependency coverage to v7.9.1 ([#137](https://github.com/aequitas-aod/aequitas-backend/issues/137)) ([6ba5458](https://github.com/aequitas-aod/aequitas-backend/commit/6ba54583261ae532210c397ef8f37ee105780cd6))

## [0.39.4](https://github.com/aequitas-aod/aequitas-backend/compare/v0.39.3...v0.39.4) (2025-06-13)

### Bug Fixes

* **deps:** update dependency pydantic to v2.11.6 ([#136](https://github.com/aequitas-aod/aequitas-backend/issues/136)) ([e4aa25d](https://github.com/aequitas-aod/aequitas-backend/commit/e4aa25d41360cdf1bcb95dfaabe6eff329bf5bd8))

## [0.39.3](https://github.com/aequitas-aod/aequitas-backend/compare/v0.39.2...v0.39.3) (2025-06-12)

### Bug Fixes

* **deps:** update dependency coverage to v7.9.0 ([#135](https://github.com/aequitas-aod/aequitas-backend/issues/135)) ([8dfd019](https://github.com/aequitas-aod/aequitas-backend/commit/8dfd0195667df85ad514d53746e60cb35625270d))

## [0.39.2](https://github.com/aequitas-aod/aequitas-backend/compare/v0.39.1...v0.39.2) (2025-06-11)

### Bug Fixes

* **deps:** update dependency flask-cors to v6.0.1 ([#134](https://github.com/aequitas-aod/aequitas-backend/issues/134)) ([a124457](https://github.com/aequitas-aod/aequitas-backend/commit/a124457e1761d173e6377e46e897a9c60fd63763))

## [0.39.1](https://github.com/aequitas-aod/aequitas-backend/compare/v0.39.0...v0.39.1) (2025-06-10)

### Bug Fixes

* fix concurrency problem adding threads to waitress command, fix neo4 env variable ([12fa973](https://github.com/aequitas-aod/aequitas-backend/commit/12fa97376c8b587bfed2d0c5084319ec1f3ab7af))

## [0.39.0](https://github.com/aequitas-aod/aequitas-backend/compare/v0.38.3...v0.39.0) (2025-06-10)

### Features

* add ULL in dataset selection ([11380f6](https://github.com/aequitas-aod/aequitas-backend/commit/11380f63ead271e8dd577a40bd5294588ab89cc0))

## [0.38.3](https://github.com/aequitas-aod/aequitas-backend/compare/v0.38.2...v0.38.3) (2025-06-10)

### Dependency updates

* **deps:** update dependency poethepoet to v0.35.0 ([#131](https://github.com/aequitas-aod/aequitas-backend/issues/131)) ([894e0bc](https://github.com/aequitas-aod/aequitas-backend/commit/894e0bcfea89d7ecdfa9f91b5addbba63b7c5d46))

### Bug Fixes

* **deps:** update dependency requests to v2.32.4 [security] ([#133](https://github.com/aequitas-aod/aequitas-backend/issues/133)) ([c545d52](https://github.com/aequitas-aod/aequitas-backend/commit/c545d52111921becd1488235cc1ab34151473228))

## [0.38.2](https://github.com/aequitas-aod/aequitas-backend/compare/v0.38.1...v0.38.2) (2025-06-07)

### Bug Fixes

* **deps:** update dependency scikit-learn to v1.7.0 ([#130](https://github.com/aequitas-aod/aequitas-backend/issues/130)) ([94460e3](https://github.com/aequitas-aod/aequitas-backend/commit/94460e3913115a27f0380ae902f4a47f4d2932a0))

## [0.38.1](https://github.com/aequitas-aod/aequitas-backend/compare/v0.38.0...v0.38.1) (2025-06-06)

### Bug Fixes

* **deps:** update dependency pandas to v2.3.0 ([#129](https://github.com/aequitas-aod/aequitas-backend/issues/129)) ([6855c3e](https://github.com/aequitas-aod/aequitas-backend/commit/6855c3e35187aff8baae99e312e554b0a47c6ada))

## [0.38.0](https://github.com/aequitas-aod/aequitas-backend/compare/v0.37.2...v0.38.0) (2025-05-29)

### Features

* **questionnaire:** add last question as placeholder and fix queries to support questions without answers ([2206dc6](https://github.com/aequitas-aod/aequitas-backend/commit/2206dc62db75a125394d05b38a10709666103ec8))

### Dependency updates

* **deps:** update dependency python-on-whales to v0.77.0 ([#109](https://github.com/aequitas-aod/aequitas-backend/issues/109)) ([85b225c](https://github.com/aequitas-aod/aequitas-backend/commit/85b225c9c618773db9e585c97e98a438a47fd944))
* **deps:** update node.js to 22.16 ([#127](https://github.com/aequitas-aod/aequitas-backend/issues/127)) ([dc96a4f](https://github.com/aequitas-aod/aequitas-backend/commit/dc96a4f0258bef17c89092f3c981f27a77afbec3))

### Bug Fixes

* **questionnaire:** fix get_nth_question when questionnaire is finished ([23726a9](https://github.com/aequitas-aod/aequitas-backend/commit/23726a9d425912dfa6d12bd785f7416cacd0b125))

### General maintenance

* **ws:** add check project exists in get questionnaire ([74d66e7](https://github.com/aequitas-aod/aequitas-backend/commit/74d66e7d222034f2e5ad3de71b93467dabd7479d))

### Refactoring

* change end of questionnaires ([e199959](https://github.com/aequitas-aod/aequitas-backend/commit/e1999597bda100471d96584c8bea1297a3c69612))

## [0.37.2](https://github.com/aequitas-aod/aequitas-backend/compare/v0.37.1...v0.37.2) (2025-05-28)

### Bug Fixes

* **deps:** update dependency pydantic to v2.11.5 ([#128](https://github.com/aequitas-aod/aequitas-backend/issues/128)) ([0649e0c](https://github.com/aequitas-aod/aequitas-backend/commit/0649e0c2c08bbf4a6286f6c985d16904d03894d6))

## [0.37.1](https://github.com/aequitas-aod/aequitas-backend/compare/v0.37.0...v0.37.1) (2025-05-28)

### Bug Fixes

* **deps:** update dependency coverage to v7.8.2 ([#126](https://github.com/aequitas-aod/aequitas-backend/issues/126)) ([b0d3207](https://github.com/aequitas-aod/aequitas-backend/commit/b0d3207fa018c6d8bf9d8b6e39016d72ed8ad024))

## [0.37.0](https://github.com/aequitas-aod/aequitas-backend/compare/v0.36.5...v0.37.0) (2025-05-27)

### Features

* add first question to detect dataset type ([3f34f2c](https://github.com/aequitas-aod/aequitas-backend/commit/3f34f2ced7f2fd5526051fdd2ec0c0373d00c751))
* add sample image dataset ([3a99778](https://github.com/aequitas-aod/aequitas-backend/commit/3a99778a7539dbd1078cb5d32ededa0500731173))
* **resources:** add Adversarial Debiasing algorithm ([0d51477](https://github.com/aequitas-aod/aequitas-backend/commit/0d51477b74479456f22eb5943a13305dc37ce25d))
* **resources:** divide dataset selection for tabular and image types ([3d9bf47](https://github.com/aequitas-aod/aequitas-backend/commit/3d9bf4783e272a1bc7fa5d6cb483adf8f127aeff))

### Bug Fixes

* fix dataset stats creation ([d2f4f55](https://github.com/aequitas-aod/aequitas-backend/commit/d2f4f55c0c64b8a8ba9da7023bb6c555d6e5fcf5))

## [0.36.5](https://github.com/aequitas-aod/aequitas-backend/compare/v0.36.4...v0.36.5) (2025-05-18)

### Bug Fixes

* **deps:** update dependency flask-cors to v6 [security] ([#125](https://github.com/aequitas-aod/aequitas-backend/issues/125)) ([ce6ca7e](https://github.com/aequitas-aod/aequitas-backend/commit/ce6ca7e9b6103271d02d5bb2a0dbd2f863fb653a))

## [0.36.4](https://github.com/aequitas-aod/aequitas-backend/compare/v0.36.3...v0.36.4) (2025-05-14)

### Bug Fixes

* **deps:** update dependency flask to v3.1.1 [security] ([#123](https://github.com/aequitas-aod/aequitas-backend/issues/123)) ([f260136](https://github.com/aequitas-aod/aequitas-backend/commit/f26013639ca45b73f0b83eec3926de02250a9309))

## [0.36.3](https://github.com/aequitas-aod/aequitas-backend/compare/v0.36.2...v0.36.3) (2025-05-09)

### Bug Fixes

* **deps:** update dependency matplotlib to v3.10.3 ([#121](https://github.com/aequitas-aod/aequitas-backend/issues/121)) ([d72fa6f](https://github.com/aequitas-aod/aequitas-backend/commit/d72fa6fd290c870aad29c2482995a1a98424c9d7))

## [0.36.2](https://github.com/aequitas-aod/aequitas-backend/compare/v0.36.1...v0.36.2) (2025-05-04)

### Dependency updates

* **deps:** update dependency poethepoet to v0.34.0 ([#118](https://github.com/aequitas-aod/aequitas-backend/issues/118)) ([247c9ae](https://github.com/aequitas-aod/aequitas-backend/commit/247c9ae9cb05936cae0ba4ab2f36b1e17cb1459c))
* **deps:** update dependency poetry to v2.1.3 ([#108](https://github.com/aequitas-aod/aequitas-backend/issues/108)) ([a765000](https://github.com/aequitas-aod/aequitas-backend/commit/a7650002e370ecb4d894e9274dd54c1102fb85e8))
* **deps:** update node.js to 22.15 ([#119](https://github.com/aequitas-aod/aequitas-backend/issues/119)) ([5ad3092](https://github.com/aequitas-aod/aequitas-backend/commit/5ad309237d581d4d565d2a762a1555a7e5fe497e))

### Bug Fixes

* **deps:** update dependency pydantic to v2.11.4 ([#120](https://github.com/aequitas-aod/aequitas-backend/issues/120)) ([371cbfc](https://github.com/aequitas-aod/aequitas-backend/commit/371cbfccfbc02c0d80b2ba5f804035d17db8f7bf))

## [0.36.1](https://github.com/aequitas-aod/aequitas-backend/compare/v0.36.0...v0.36.1) (2025-04-15)

### Dependency updates

* **deps:** update actions/setup-node action to v4.4.0 ([#117](https://github.com/aequitas-aod/aequitas-backend/issues/117)) ([200f752](https://github.com/aequitas-aod/aequitas-backend/commit/200f7524a75553ac9aef652d132e6736632cc8f4))

### Bug Fixes

* temporary fix for video demo ([7a70ece](https://github.com/aequitas-aod/aequitas-backend/commit/7a70eceedd7d74a351c05a11a5d5a45c58bde91b))
* trigger release ([1a88014](https://github.com/aequitas-aod/aequitas-backend/commit/1a88014d9b118e40dba3f16df47031dada03d0cc))

### General maintenance

* **release:** 0.36.1 [skip ci] ([930b356](https://github.com/aequitas-aod/aequitas-backend/commit/930b35653d9f81684409fab7574649cbb7f4fb03)), closes [#117](https://github.com/aequitas-aod/aequitas-backend/issues/117)

## [0.36.1](https://github.com/aequitas-aod/aequitas-backend/compare/v0.36.0...v0.36.1) (2025-04-15)

### Dependency updates

* **deps:** update actions/setup-node action to v4.4.0 ([#117](https://github.com/aequitas-aod/aequitas-backend/issues/117)) ([200f752](https://github.com/aequitas-aod/aequitas-backend/commit/200f7524a75553ac9aef652d132e6736632cc8f4))

### Bug Fixes

* temporary fix for video demo ([7a70ece](https://github.com/aequitas-aod/aequitas-backend/commit/7a70eceedd7d74a351c05a11a5d5a45c58bde91b))

## [0.36.0](https://github.com/aequitas-aod/aequitas-backend/compare/v0.35.6...v0.36.0) (2025-04-11)

### Features

* **infrastructure:** add endpoint to check if a project exists ([0d998b5](https://github.com/aequitas-aod/aequitas-backend/commit/0d998b5aa2df5484fb3b2cc1d649799972a481b5))

### Refactoring

* **repository:** improve check_project_exists query ([5422cf2](https://github.com/aequitas-aod/aequitas-backend/commit/5422cf22af39369304ca969db36a5dcb24258859))
* **repository:** improve method to check if a project exists ([5a4815d](https://github.com/aequitas-aod/aequitas-backend/commit/5a4815d28493e009a75dea69cbbe99bc8c985123))

## [0.35.6](https://github.com/aequitas-aod/aequitas-backend/compare/v0.35.5...v0.35.6) (2025-04-11)

### Bug Fixes

* **Neo4jDriver:** fix resource warning due to deprecated closing driver ([85cde9b](https://github.com/aequitas-aod/aequitas-backend/commit/85cde9bf10b6c9b58288edf289fed67f2f30597f))

## [0.35.5](https://github.com/aequitas-aod/aequitas-backend/compare/v0.35.4...v0.35.5) (2025-04-11)

### Bug Fixes

* **questionnaire:** fix project question insert/delete ([74bdb16](https://github.com/aequitas-aod/aequitas-backend/commit/74bdb16bc3b3ca0c4011d4ef209d91a6de97ae65))

## [0.35.4](https://github.com/aequitas-aod/aequitas-backend/compare/v0.35.3...v0.35.4) (2025-04-08)

### Bug Fixes

* **deps:** update dependency pydantic to v2.11.3 ([#116](https://github.com/aequitas-aod/aequitas-backend/issues/116)) ([bd8c6dd](https://github.com/aequitas-aod/aequitas-backend/commit/bd8c6dd5742fb67c56f3c706d69e7e2d9bbe27d3))

## [0.35.3](https://github.com/aequitas-aod/aequitas-backend/compare/v0.35.2...v0.35.3) (2025-04-04)

### Bug Fixes

* **build:** fix kafka version ([420ab93](https://github.com/aequitas-aod/aequitas-backend/commit/420ab93bf87acadd8c460f51ae7c14a19215e259))

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
