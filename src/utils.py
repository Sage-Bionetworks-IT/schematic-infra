import boto3

from botocore.exceptions import ClientError
from os import environ


def get_environment() -> str:
    """
    The `ENV` environment variable's value represents the deployment
    environment (dev, stage, prod, etc..).  This method gets the `ENV`
    environment variable's value
    """
    VALID_ENVS = ["dev", "stage", "prod"]

    env_environment_var = environ.get("ENV")
    if env_environment_var is None:
        environment = "dev"  # default environment
    elif env_environment_var in VALID_ENVS:
        environment = env_environment_var
    else:
        valid_envs_str = ",".join(VALID_ENVS)
        raise SystemExit(
            f"Must set environment variable `ENV` to one of {valid_envs_str}"
        )

    return environment


def get_ssm_secret(param_store_ref: str) -> str:
    """
    Retrieve a secret from the AWS SSM parameter store.

    param_store_ref is a key/ssm param name for a secret.

    Example param_store_ref:
        "/app/dev/MARIADB_PASSWORD"

    Retrieve the value from the parameter "/app/dev/MARIADB_PASSWORD"
    in the AWS SSM parameter store
    """
    ssm = boto3.client("ssm")
    try:
        response = ssm.get_parameter(Name=param_store_ref, WithDecryption=True)
        value = response["Parameter"]["Value"]
    except ClientError as e:
        raise e

    return value
