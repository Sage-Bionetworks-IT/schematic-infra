CONTAINER_LOCATION_PATH_ID = "path://"


class ServiceProps:
    """
    ECS service properties

    container_name: the name of the container
    container_location:
      supports "path://" for building container from local (i.e. path://docker/MyContainer)
      supports docker registry references (i.e. ghcr.io/sage-bionetworks/schematic-thumbor:latest)
    container_port: the container application port
    container_memory: the container application memory
    container_env_vars: a json dictionary of environment variables to pass into the container
      i.e. {"EnvA": "EnvValueA", "EnvB": "EnvValueB"}
    container_secret_name: the secret's name in the AWS secrets manager
    auto_scale_min_capacity: the fargate auto scaling minimum capacity
    auto_scale_max_capacity: the fargate auto scaling maximum capacity
    """

    def __init__(
        self,
        container_name: str,
        container_location: str,
        container_port: int,
        container_memory: int = 512,
        container_env_vars: dict = None,
        container_secret_name: str = None,
        auto_scale_min_capacity: int = 1,
        auto_scale_max_capacity: int = 1,
    ) -> None:
        self.container_name = container_name
        self.container_port = container_port
        self.container_memory = container_memory
        if CONTAINER_LOCATION_PATH_ID in container_location:
            container_location = container_location.removeprefix(
                CONTAINER_LOCATION_PATH_ID
            )
        self.container_location = container_location
        if container_env_vars is None:
            self.container_env_vars = {}
        self.container_secret_name = container_secret_name
        self.auto_scale_min_capacity = auto_scale_min_capacity
        self.auto_scale_max_capacity = auto_scale_max_capacity
