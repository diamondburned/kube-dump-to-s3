# kube-dump-to-s3

Docker container + CLI tool that wraps around
[kube-dump](https://github.com/WoozyMasta/kube-dump) to allow for easy
exporting backup outputs to S3 buckets.

## Building

You can either build with Nix or with Docker. The following command will use
Nix if detected, otherwise falling back to Docker.

Note that the build output hash will be different for both builders, but the
underlying program will be the same. It is recommended to stick to the same
builder for reproducibility.

```sh
make docker-build
```

## Running

You can run from Docker, from Nix or directly:

```sh
# Docker
docker run kube-dump-to-s3:latest --help

# Nix Flakes
nix run '.#' -- --help

# Directly
python3 -m kube_dump_to_s3 --help
```

The following flags (environment variables if all-caps) are required:

```
--debug bool          Debug mode (logging + keep export dir) (default: False)
--use_zstd bool       Compress the final tarball with zstd (otherwise, tar will be used) (default: True)
--kubeconfig str      Path to the kubeconfig file (required)
--namespaces {list[str],None}
                      List of namespaces to dump (none = all namespaces) (default: None)
--cluster bool        Include cluster-wide resources (default: True)
--s3_prefix str       Prefix for the S3 keys (default: kube-dump)
--s3_bucket str       S3 bucket name (required)
--s3_region str       AWS region (required)
--s3_endpoint str     S3 endpoint URL (required)
--secrets_dir str     Directory for secrets (want files: s3_access_key, s3_secret_key) (default: /run/secrets)
```

Inside `secrets_dir`, you will need 2 files:

- `s3_access_key`: Your S3 access key
- `s3_secret_key`: Your S3 secret key

It is recommended to use secret volume mounts in Kubernetes for these files to
avoid storing them publicly.

## Publishing

This repository is automatically published to [GitHub Docker Registry](https://ghcr.io).
You may also publish it internally via:

```sh
IMAGE_REPOSITORY="your-registry.example.com/your-repo" make docker-push
```
