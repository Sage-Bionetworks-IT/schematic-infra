import aws_cdk as cdk

from src.network_stack import NetworkStack
from src.ecs_stack import EcsStack
from src.service_stack import LoadBalancedServiceStack
from src.load_balancer_stack import LoadBalancerStack
from src.service_props import ServiceProps
import src.utils as utils

cdk_app = cdk.App()

# get the environment
environment = utils.get_environment()
stack_name_prefix = f"schematic-{environment}"
image_version = "0.0.11"

# get VARS from cdk.json
env_vars = cdk_app.node.try_get_context(environment)
fully_qualified_domain_name = env_vars["FQDN"]
subdomain, domain = fully_qualified_domain_name.split(".", 1)
vpc_cidr = env_vars["VPC_CIDR"]
certificate_arn = env_vars["CERTIFICATE_ARN"]

# get secrets from cdk.json or aws parameter store
secrets = utils.get_secrets(cdk_app)

network_stack = NetworkStack(cdk_app, f"{stack_name_prefix}-network", vpc_cidr)

ecs_stack = EcsStack(
    cdk_app, f"{stack_name_prefix}-ecs", network_stack.vpc, fully_qualified_domain_name
)
ecs_stack.add_dependency(network_stack)

# From AWS docs https://docs.aws.amazon.com/AmazonECS/latest/developerguide/service-connect-concepts-deploy.html
# The public discovery and reachability should be created last by AWS CloudFormation, including the frontend
# client service. The services need to be created in this order to prevent an time period when the frontend
# client service is running and available the public, but a backend isn't.
load_balancer_stack = LoadBalancerStack(
    cdk_app, f"{stack_name_prefix}-load-balancer", network_stack.vpc
)

apex_service_props = ServiceProps(
    "schematic-apex",
    8000,
    200,
    f"ghcr.io/sage-bionetworks/schematic-apex:{image_version}",
    {
        "API_DOCS_HOST": "schematic-api-docs",
        "API_DOCS_PORT": "8010",
        "API_GATEWAY_HOST": "schematic-api-gateway",
        "API_GATEWAY_PORT": "8082",
        "APP_HOST": "schematic-app",
        "APP_PORT": "4200",
        "THUMBOR_HOST": "schematic-thumbor",
        "THUMBOR_PORT": "8889",
        "ZIPKIN_HOST": "schematic-zipkin",
        "ZIPKIN_PORT": "9411",
    },
)

app_service_stack = LoadBalancedServiceStack(
    cdk_app,
    f"{stack_name_prefix}-app",
    network_stack.vpc,
    ecs_stack.cluster,
    apex_service_props,
    load_balancer_stack.alb,
    certificate_arn,
    health_check_path="/health",
    health_check_interval=5,
)
app_service_stack.add_dependency(load_balancer_stack)

cdk_app.synth()
