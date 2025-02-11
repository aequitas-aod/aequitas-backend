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
