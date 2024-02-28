# OSML Tile Server Test

This package contains the integration tests for OSML Tile Server application

### Table of Contents
* [Getting Started](#getting-started)
    * [Prerequisites](#prerequisites)
    * [Installation Guide](#installation-guide)
    * [Documentation](#documentation)
    * [Running Tests in Docker](#running-tests-in-docker)
    * [Running LoadTest](#running-loadtest)
* [Support & Feedback](#support--feedback)
* [Security](#security)
* [License](#license)


## Getting Started
### Prerequisites

First, ensure you have installed the following tools locally

1. [aws cli](https://docs.aws.amazon.com/cli/latest/userguide/install-cliv2.html)
2. [docker](https://nodejs.org/en)
3. [tox](https://tox.wiki/en/latest/installation.html)

### Installation Guide

1. Clone `osml-tile-server-test` package into your desktop

```sh
git clone https://github.com/aws-solutions-library-samples/osml-tile-server-test.git
```

1. Run `tox` to create a virtual environment

```sh
cd osml-tile-server-test
tox
```

### Documentation

You can find documentation for this library in the `./doc` directory. Sphinx is used to construct a searchable HTML
version of the API documents.

```shell
tox -e docs
```

### Running Test in Docker
Arguments can be passed in to docker run to set the endpoint, test type, source bucket, and source image.
For example, the container can be built and run as follows:

```
docker build . -t tile-server-test:latest
docker run --name osml-tile-server-test tile-server-test:latest --endpoint <Endpoint URL> --test_type integ --source_image_bucket <S3 bucket> --source_image_key <S3 Image Key> -v
```

### Running LoadTest

(In progress)


## Support & Feedback

To post feedback, submit feature ideas, or report bugs, please use the [Issues](https://github.com/aws-solutions-library-samples/osml-tile-server-test/issues) section of this GitHub repo.

If you are interested in contributing to OversightML Model Runner, see the [CONTRIBUTING](CONTRIBUTING.md) guide.

## Security

See [CONTRIBUTING](CONTRIBUTING.md) for more information.

## License

MIT No Attribution Licensed. See [LICENSE](LICENSE).
