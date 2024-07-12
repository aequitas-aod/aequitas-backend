# Aequitas - Backend

Web service implementing the Aequitas context service.

## Prerequisites

- Python 3.10+

## Getting Started

### Installation

- Run `pip install -r requirements.txt` to install poetry package manager.
- Run `poetry install` to install the project dependencies. Poetry will create a virtual environment that will be used
  to handle project dependencies.

### Running the service

- Run `docker compose up -d` to start the database.
- Starting the web server:
  - `poe dev --port 4005` to run the service in the development mode.
  - `poe serve --port 4005` to run the service in the production mode.
- Interact with the service through the [Aequitas Frontend](https://github.com/aequitas-aod/aequitas-frontend/tree/feature/admin-view)


## Dependencies Management

The purpose of [requirements](requirements.txt) file is just offering a quick way to install poetry.
Actual dependencies are managed by poetry itself.

You can add new dependencies to the project by running `poetry add <package-name>`. This will add the
package to the `pyproject.toml` file and install it in the virtual environment.

## Testing

In order to run the whole test suite:

```bash
poe test
```

If you want to run just unit tests:

```bash
poe unit-test
```

Or just integration tests:

```bash
poe intergation-test
```

## Code Style

This project uses [black](https://github.com/psf/black) code formatter.

### Check code style

```bash
poe format-check
```

### Format code

```bash
poe format
```
