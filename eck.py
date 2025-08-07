from kubernetes import client, config
import sys

try:
    config.load_kube_config() #load the kube config file
    print("✅ Kubernetes config loaded successfully!")
except config.config_exception.ConfigException as e:
    print("❌ Kubernetes cluster not configured!")
    print("\n🔧 To fix this:")
    print("1. Open Docker Desktop → Settings → Kubernetes → Enable Kubernetes")
    print("2. OR set up minikube: brew install minikube && minikube start")
    print("3. OR connect to an existing cluster")
    print(f"\nError details: {e}")
    sys.exit(1)

api_client = client.ApiClient() #create an api client

deployment = client.V1Deployment(
    metadata=client.V1ObjectMeta(name="my-flask-app"),
    spec=client.V1DeploymentSpec(
        replicas=1,
        selector=client.V1LabelSelector(
            match_labels={"app": "my-flask-app"}
        ),
        template=client.V1PodTemplateSpec(
            metadata=client.V1ObjectMeta(
                labels={"app": "my-flask-app"}
            ),
            spec=client.V1PodSpec(
                containers=[
                    client.V1Container(
                        name="my-flask-container",
                        image="919994927167.dkr.ecr.us-east-1.amazonaws.com/my-ecr-repo:latest",
                        ports=[client.V1ContainerPort(container_port=8080)]
                    )
                ]
            )
        )
    )
)

api_instance = client.AppsV1Api(api_client)

try:
    api_instance.create_namespaced_deployment(
        body=deployment,
        namespace="default"
    )
    print("✅ Deployment created successfully!")
except Exception as e:
    print(f"❌ Failed to create deployment: {e}")

#define the service
service = client.V1Service(
    metadata=client.V1ObjectMeta(name="my-flask-service"),
    spec=client.V1ServiceSpec(
        selector={"app": "my-flask-app"},
        ports=[client.V1ServicePort(port=8080)],
        type="LoadBalancer"
    )
)

try:
    api_instance_core = client.CoreV1Api(api_client)
    api_instance_core.create_namespaced_service(body=service, namespace="default")
    print("✅ Service created successfully!")
    print("\n🎉 Flask app deployed to Kubernetes!")
    print("Run 'kubectl get pods' to see your deployment")
except Exception as e:
    print(f"❌ Failed to create service: {e}")