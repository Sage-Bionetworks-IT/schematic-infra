import aws_cdk as cdk

from os import environ
from src.network_stack import NetworkStack
from src.ecs_stack import EcsStack
from src.service_stack import LoadBalancedServiceStack
from src.load_balancer_stack import LoadBalancerStack
from src.service_props import ServiceProps

# get the environment and set environment specific variables
VALID_ENVIRONMENTS = ["dev", "stage", "prod"]
environment = environ.get("ENV")
match environment:
    case "prod":
        environment_variables = {
            "VPC_CIDR": "10.254.194.0/24",
            "FQDN": "prod.schematic.io",
            "CERTIFICATE_ARN": "arn:aws:acm:us-east-1:878654265857:certificate/d11fba3c-1957-48ba-9be0-8b1f460ee970",
            "TAGS": {"CostCenter": "NO PROGRAM / 000000"},
        }
    case "stage":
        environment_variables = {
            "VPC_CIDR": "10.254.193.0/24",
            "FQDN": "stage.schematic.io",
            "CERTIFICATE_ARN": "arn:aws:acm:us-east-1:878654265857:certificate/d11fba3c-1957-48ba-9be0-8b1f460ee970",
            "TAGS": {"CostCenter": "NO PROGRAM / 000000"},
        }
    case "dev":
        environment_variables = {
            "VPC_CIDR": "10.254.192.0/24",
            "FQDN": "dev.schematic.io",
            "CERTIFICATE_ARN": "arn:aws:acm:us-east-1:631692904429:certificate/0e9682f6-3ffa-46fb-9671-b6349f5164d6",
            "TAGS": {"CostCenter": "NO PROGRAM / 000000"},
        }
    case _:
        valid_envs_str = ",".join(VALID_ENVIRONMENTS)
        raise SystemExit(
            f"Must set environment variable `ENV` to one of {valid_envs_str}"
        )

stack_name_prefix = f"schematic-{environment}"
environment_tags = environment_variables["TAGS"]

# Define stacks
cdk_app = cdk.App()

# recursively apply tags to all stack resources
if environment_tags:
    for key, value in environment_tags.items():
        cdk.Tags.of(cdk_app).add(key, value)

network_stack = NetworkStack(
    cdk_app, f"{stack_name_prefix}-network", environment_variables["VPC_CIDR"]
)

ecs_stack = EcsStack(
    cdk_app,
    f"{stack_name_prefix}-ecs",
    network_stack.vpc,
    environment_variables["FQDN"],
)

# From AWS docs https://docs.aws.amazon.com/AmazonECS/latest/developerguide/service-connect-concepts-deploy.html
# The public discovery and reachability should be created last by AWS CloudFormation, including the frontend
# client service. The services need to be created in this order to prevent an time period when the frontend
# client service is running and available the public, but a backend isn't.
load_balancer_stack = LoadBalancerStack(
    cdk_app, f"{stack_name_prefix}-load-balancer", network_stack.vpc
)

app_service_props = ServiceProps(
    "schematic-app",
    "ghcr.io/sage-bionetworks/schematic:v0.1.90-beta",
    443,
    container_memory=1024,
    container_secret_name=f"{stack_name_prefix}-DockerFargateStack/{environment}/ecs",
)

app_service_stack = LoadBalancedServiceStack(
    cdk_app,
    f"{stack_name_prefix}-app",
    network_stack.vpc,
    ecs_stack.cluster,
    app_service_props,
    load_balancer_stack.alb,
    environment_variables["CERTIFICATE_ARN"],
    health_check_path="/health",
    health_check_interval=5,
)

# Generate stacks
cdk_app.synth()
