## 1.0.0

#### Added:

- Database abstraction layer with thread-safe operations, in-memory fallback, retry logic, and health monitoring.
- Modbus manager with circuit breaker pattern, cached fallback, batch synchronization, and error isolation.
- Configuration system supporting file and environment variables, validation, type safety, and hot-reload.
- Structured logging infrastructure with JSON support, multiple handlers, rotation, and request/response tracking.
- Production-ready server setup using Gunicorn with gevent workers, health checks, and non-root user support.
- Main application entry point `main.py` integrating Flask app, CORS, rate limiting, blueprints, and graceful shutdown.
- API blueprint for zone management and other endpoints with proper error handling and input validation.
- Swagger documentation, request logging middleware, and API key authentication support.
- Dockerfile enhancements including multi-stage build, dependencies installation, health checks, and production command.
- Unit and integration testing strategy with examples and Prometheus metrics for observability.

#### Changed:

- Refactored codebase to a modular architecture with blueprints, separate modules, and clean project layout.
- Replaced Flask development server with Gunicorn for production deployments.
- Updated README and documentation to reflect v2 architecture, quick start guides, and migration instructions.
- Reorganized configuration and environment variable handling with `.env.example`.

#### Removed:

- Legacy code from v1 and CI/CD changelog update step.

## 0.2.7

#### Added:

- Extracted project version dynamically from Git tags with a fallback to v0.0.0.
- Implemented unit testing using Python’s unittest framework.
- Added debug steps for version extraction and Docker login validation.

#### Changed:

- Updated GitHub Actions workflow to run unit tests before building Docker images.
- Enhanced Docker Hub authentication by using GitHub Secrets.

#### Removed:

- Removed the changelog update step from the CI/CD workflow for simplification.

## 0.2.6

- Fix POST endpoint set zone op_status temperature target, typos

## 0.2.5

- Fix POST endpoint set zone op_status temperature target

## 0.2.4

- Consolidate usage of singular v plural

## 0.2.3

- Consolidate meaning of state v status

## 0.2.2

- Remove shadowing of binary status for pumps, dehumidifiers running status

## 0.2.1

- Fix ported go -> python KNX DPT9001 pack function to accommodate for python 256 int to byte mapping

## 0.2.0

- First release of at least working addon

## 0.1.0

- Initial release
