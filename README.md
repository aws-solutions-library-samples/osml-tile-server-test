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

### Running Tests

#### In AWS Lambda
The Tile Server Test package is designed to be deployed as an AWS Lambda Container.
The [osml-cdk-constructs](https://github.com/aws-solutions-library-samples/osml-cdk-constructs)
package contains the required resources, and example stacks can be found in the associated
[AWS Guidance Repository](https://github.com/aws-solutions-library-samples/guidance-for-processing-overhead-imagery-on-aws).
When deployed in this manner, the Tile Server integration tests can be initiated by running ```npm run integ:tile-server```
from the guidance repository.

#### In Docker
For testing and development purposes, the Tile Server tests can be executed locally in Docker.
Arguments can be passed to docker run to configure the endpoint, test type, source bucket, and source image.
If testing against a local tile server, ```--network host``` may need to be added as a ```docker run``` flag.

Example Build:
```sh
docker build . -t tile-server-test:latest
```
Example Integration test:
```sh
docker run --name osml-tile-server-test --rm tile-server-test:latest --endpoint <Endpoint URL> --test_type integ --source_image_bucket <S3 bucket> --source_image_key <S3 Image Key> -v
```
Example Locust Load test (Default UI address is http://localhost:8089):
```sh
docker run --name osml-tile-server-test --rm tile-server-test:latest --endpoint <Endpoint URL> --test_type load --source_image_bucket <S3 bucket> --locust_image_keys <S3 Image Key>,<S3 Image Key> -v
```
Other optional load test flags are:

- ```--locust_headless <true/false>``` Disable the web interface, and start the test immediately. Default: False
- ```--locust_users <number>``` Load Test: Peak number of concurrent Locust users.
- ```--locust_run_time <string>``` Stop after the specified amount of time, e.g. (300s, 20m, 3h, 1h30m, etc.)
- ```--locust_spawn_rate <string>``` Rate to spawn users at (users per second).



## Support & Feedback

To post feedback, submit feature ideas, or report bugs, please use the [Issues](https://github.com/aws-solutions-library-samples/osml-tile-server-test/issues) section of this GitHub repo.

If you are interested in contributing to OversightML Model Runner, see the [CONTRIBUTING](CONTRIBUTING.md) guide.

## Security

See [CONTRIBUTING](CONTRIBUTING.md) for more information.

## License

MIT No Attribution Licensed. See [LICENSE](LICENSE).
