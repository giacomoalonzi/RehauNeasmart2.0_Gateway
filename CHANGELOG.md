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
