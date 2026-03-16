# Usage examples and connection guide for the VDCLOUD Lab Kubernetes cluster

## 1. Introduction

This guide provides detailed instructions for connecting to the VDCLOUD Lab infrastructure via VPN, installing the required tools, setting up a local workstation environment, and running Kubernetes (k8s) tasks. [Kubernetes (K8s)](https://kubernetes.io/) is an open-source platform for managing containerized applications at scale. Its purpose is to simplify application management, automation, and scaling.

You will also receive an email with two configuration files and a username for the infrastructure. In the guide below, wherever you see **<username>**, replace it with the username you received by email.

The material is available in the following repository:

https://github.com/ikons/cloud-uth

You can download it locally with the following command:

```bash
cd ~
git clone https://github.com/ikons/cloud-uth.git
```

This command will clone the entire repository to your computer. Because the repository may be updated regularly, make sure you keep it up to date by running:

```bash
cd cloud-uth
git pull
```

## 2. Installing the OpenVPN client, kubectl, and k9s

To connect to the infrastructure, install the [OpenVPN client](https://openvpn.net/community-downloads/).

After installing the client, import the `.ovpn` file that was sent to you by email and connect.

Install **kubectl**

`kubectl` is the command-line tool used to manage Kubernetes clusters. Install it with the following commands on a Linux machine or inside WSL:

```bash
# Install the basic packages required for accessing HTTPS repositories
sudo apt-get install -y apt-transport-https ca-certificates curl gnupg

# Download and store the public key for the Kubernetes repository
curl -fsSL https://pkgs.k8s.io/core:/stable:/v1.32/deb/Release.key | sudo gpg --dearmor -o /etc/apt/keyrings/kubernetes-apt-keyring.gpg

# Set the correct access permissions on the key file
sudo chmod 644 /etc/apt/keyrings/kubernetes-apt-keyring.gpg

# Add the Kubernetes repository to the apt sources list
echo 'deb [signed-by=/etc/apt/keyrings/kubernetes-apt-keyring.gpg] https://pkgs.k8s.io/core:/stable:/v1.32/deb/ /' | sudo tee /etc/apt/sources.list.d/kubernetes.list

# Set the correct access permissions on the repository file
sudo chmod 644 /etc/apt/sources.list.d/kubernetes.list

# Update the apt package list
sudo apt-get update

# Install kubectl
sudo apt-get install -y kubectl

# Create the ~/.kube directory where the config file is stored
mkdir ~/.kube
```

Place the `config` file that was sent to you by email at `~/.kube/config` so that `kubectl` can connect to the k8s infrastructure.

To do that, you need to copy the `config` file from the host computer filesystem where you originally downloaded it (that is, Windows) into the `~/.kube` directory inside your WSL Linux environment.

Assume that you downloaded the `config` file into the `Downloads` folder of your Windows user account.

To copy it to the correct location, run the following commands inside WSL Linux. Replace **<username>** with the Windows username of your own installation. For example, in my case it is `/mnt/c/Users/**ikons**/Downloads/config`.

```bash
# Go to the user's home directory
cd

# Create the .kube directory (if it does not already exist)
mkdir .kube

# Copy the config file from the Windows filesystem into WSL
cp /mnt/c/Users/<username>/Downloads/config ~/.kube/config
```

Another way to do this is through Windows Explorer by selecting the Linux folder.

**Installing k9s**

`k9s` is a tool for monitoring and managing Kubernetes clusters. Install it as follows:

```bash
wget https://github.com/derailed/k9s/releases/download/v0.40.10/k9s_linux_amd64.deb
sudo dpkg -i k9s_linux_amd64.deb
echo "export KUBE_EDITOR=nano" >> ~/.bashrc
```

The `k9s` tool also uses the same `~/.kube/config` configuration file.

**Monitoring execution with k9s**

To monitor the workload you just submitted, use `k9s`:

```bash
k9s
```

**Usage examples**

**Show pods**:

```bash
:pods
```

**View the logs of a pod**:

```bash
l
```

**Inspect the status of a pod**:

```bash
d
```

## 3. Writing manifests and running them with kubectl

**Manifests** are YAML files that describe Kubernetes resources. You can create and apply these files using the `kubectl apply` command.

Navigate to the example directory:

```bash
cd ~/cloud-uth/code/03_manifest
```

**Example pod manifest:**

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: nginx
spec:
  containers:
  - name: nginx
    image: nginx:latest
    ports:
    - containerPort: 80
```

To create the pod above:

```bash
kubectl apply -f nginx-pod.yaml
```

To verify that the pod was created successfully:

```bash
kubectl get pod nginx -o wide
```

You should see something similar to the following:

```
NAME    READY   STATUS    RESTARTS   AGE     IP               NODE              NOMINATED NODE   READINESS GATES

nginx   1/1     Running   0          7h34m   10.233.101.168   source-code-pc6   <none>           <none>
```

Using the pod IP address, you can open the pod in your browser and view the nginx hello-world page:

http://10.233.101.168

**🧹 Infrastructure cleanup**

Once you have verified that the `nginx` pod runs correctly and serves the default nginx page, you can remove it from your cluster with the following command:

```bash
# Delete the pod
kubectl delete -f nginx-pod.yaml
```

## 4. Container storage using StorageClasses, PersistentVolumeClaims, and PersistentVolumes

**Ephemeral storage:** By default, Kubernetes pods do not have persistent storage. If you store data inside a pod, that data will be lost as soon as the pod is deleted or restarted. This happens because the data is stored in the container filesystem, which is temporary.

**Persistent storage with PersistentVolumes (PVs), PersistentVolumeClaims (PVCs), and StorageClass:** Kubernetes introduces the concepts of PersistentVolumes (PVs) and PersistentVolumeClaims (PVCs) in order to provide persistent storage for pods.

- **Persistent Volume (PV):** A storage resource decoupled from pods and managed by the cluster administrator. PVs may be physical storage devices (such as disk volumes in cloud infrastructures) or abstractions that connect to other storage systems.
- **Persistent Volume Claim (PVC):** A way for a user to request a specific type or size of storage. PVCs are usually how pods gain access to a PV.
- **StorageClass:** By introducing StorageClasses, Kubernetes allows storage resources (PVs) to be provisioned dynamically according to PVC requirements. A StorageClass defines storage settings such as the storage type (for example, SSD or HDD) and other parameters such as the desired performance level.

For example, with the following command (run only with administrator privileges, not as a regular user):

```
ikons@source-code-master:~$ kubectl get storageclass

NAME                   PROVISIONER             RECLAIMPOLICY   VOLUMEBINDINGMODE      ALLOWVOLUMEEXPANSION   AGE
local-path (default)   rancher.io/local-path   Delete          WaitForFirstConsumer   false                  44d
```

we can check whether there is a storage class available to provide storage. The information shown here tells us that the Kubernetes cluster uses the `local-path` StorageClass, provided by the `rancher.io/local-path` provisioner, with a `Delete` reclaim policy. It also uses `WaitForFirstConsumer` for `volumeBindingMode`, which means the PV will only be created when a pod actually requests it.

Create a Persistent Volume Claim (PVC)

Navigate to the example directory:

```bash
cd ~/cloud-uth/code/04_pvc_pv
```

First, we need the YAML file for the PVC that will use the existing **local-path** StorageClass. The file `nginx-pvc.yaml` contains:

```yaml
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: nginx-pvc
spec:
  accessModes:
    - ReadWriteOnce
  resources:
    requests:
      storage: 1Gi
```

To create the PVC in your cluster, run:

```bash
kubectl apply -f nginx-pvc.yaml
```

This command creates a PVC requesting 1Gi of storage through the cluster's default StorageClass.

**Create the nginx pod that uses a PVC (persistent storage)**

First, we need a text file that will be placed in the directory served by nginx. This file should remain available even if the pod is deleted or restarted.

The file `index.html`, which will be placed under `/usr/share/nginx/html` for nginx to serve, contains the following (view it with `cat index.html`):

```bash
cat index.html
```

```html
<html>
  <head><title>Persistent Storage Example</title></head>
  <body>
    <h1>Welcome to Nginx with Persistent Volume!</h1>
    <p>This content is stored in a Persistent Volume and will persist even if the Pod is terminated.</p>
  </body>
</html>
```

After creating the PVC, we can create the pod that uses the Persistent Volume through the PVC and serves the `index.html` file. This is done with the `nginx-pod.yaml` file shown below:

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: nginx-pod
spec:
  containers:
    - name: nginx
      image: nginx:latest
      volumeMounts:
        - mountPath: /usr/share/nginx/html
          name: nginx-storage
  volumes:
    - name: nginx-storage
      persistentVolumeClaim:
        claimName: nginx-pvc
```

To create the nginx pod in your cluster, run:

```bash
kubectl apply -f nginx-pod.yaml
```

This command creates a pod named `nginx-pod`, which uses the PVC to store data under `/usr/share/nginx/html`.

Copy the `index.html` file into the Persistent Volume at `/usr/share/nginx/html` inside the pod. This can be done using `kubectl cp`:

```bash
kubectl cp index.html nginx-pod:/usr/share/nginx/html/index.html
```

This command copies the local `index.html` file from the user's machine into `/usr/share/nginx/html` inside `nginx-pod`. A persistent volume is mounted on that path.

If you now visit the nginx pod IP, you will see the page above.

Run:

```bash
kubectl get pod nginx-pod -o wide
```

and open the page in your browser at `http://<podip>`.

Even if the pod is terminated and recreated, the `index.html` file will still be available and nginx will continue to serve it. Let us delete the pod:

```bash
kubectl delete pod nginx-pod
```

Let us recreate it:

```bash
kubectl apply -f nginx-pod.yaml
```

Now retrieve the new IP assigned to the new pod:

```bash
kubectl get pod nginx-pod -o wide
```

and open the browser again at the new address: `http://<podip>`.

You will see that the page **remains available** even after destroying the **pod**.

**Create an nginx pod without a PVC (ephemeral storage)**

Now let us create an nginx pod without persistent storage, which means that data will be lost when the pod terminates.

The file `nginx-pod-ephemeral.yaml` for the nginx pod without persistent storage contains:

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: nginx-pod-ephemeral
spec:
  containers:
    - name: nginx
      image: nginx:latest
```

To create the pod, run:

```bash
kubectl apply -f nginx-pod-ephemeral.yaml
```

Copy the same `index.html` file into `/usr/share/nginx/html` inside the new pod:

```bash
kubectl cp index.html nginx-pod-ephemeral:/usr/share/nginx/html/index.html
```

Retrieve the pod IP so that you can open its page in a browser:

```bash
kubectl get pod nginx-pod-ephemeral -o wide
```

If you visit the page in your browser, you will see the page you uploaded.

Now, to observe the difference, terminate the pod:

```bash
kubectl delete pod nginx-pod-ephemeral
```

Recreate the pod:

```bash
kubectl apply -f nginx-pod-ephemeral.yaml
```

If you visit the page again in your browser, you will see the default nginx page (`Welcome to nginx!`), because the data (the `index.html` file) has been lost. The pod filesystem is ephemeral, so its contents disappear when the pod is terminated.

**🧹 Infrastructure cleanup**

After completing the tests and verifying the difference between persistent and ephemeral storage, you can delete the resources you created with the following commands:

```bash
# Delete the pods
kubectl delete pod nginx-pod
kubectl delete pod nginx-pod-ephemeral

# Delete the PersistentVolumeClaim (PVC)
kubectl delete pvc nginx-pvc
```

## 5. ReplicaSets

A **ReplicaSet** is a Kubernetes control object that ensures that a specified number of replicas (pods) of an application are always running in the cluster. If a pod fails or is terminated, the ReplicaSet automatically creates a new one to maintain the desired state according to the user's intent.

**Behavior and characteristics**

- **Maintains the desired number of pods:** If a pod is deleted or fails, the ReplicaSet replaces it.
- **Uses label selectors:** ReplicaSets use label selectors to identify which pods they should manage.
- **Supports scaling:** We can adjust the size of the ReplicaSet by increasing or decreasing the number of pods.
- **Often part of a Deployment:** In practice, ReplicaSets are usually used through Deployments for more flexible application management.

Navigate to the example directory:

```bash
cd ~/cloud-uth/code/05_replicaset
```

**Example YAML file**

Below is `my-replicaset.yaml`, which defines a ReplicaSet that keeps 3 replicas of a pod running:

```yaml
apiVersion: apps/v1
kind: ReplicaSet
metadata:
  name: my-replicaset
spec:
  replicas: 3
  selector:
    matchLabels:
      app: my-app
  template:
    metadata:
      labels:
        app: my-app
    spec:
      containers:
      - name: my-container
        image: nginx:latest
```

**ReplicaSet management commands**

**Create a ReplicaSet**:

```bash
kubectl apply -f my-replicaset.yaml
```

**Check its status**:

```bash
kubectl get replicaset
```

**Scale the pods**:

```bash
kubectl scale --replicas=5 rs/my-replicaset
```

**Best practices — summary**

- **Use Deployments instead of ReplicaSets:** Although ReplicaSets can be used directly, Deployments provide additional capabilities such as rolling updates and rollbacks.
- **Define appropriate label selectors:** Always make sure the ReplicaSet manages the correct pods.
- **Monitoring and logging:** Use tools such as `kubectl describe rs` and `kubectl logs` to inspect status and behavior.
- **Summary:** ReplicaSets are a core Kubernetes mechanism for maintaining the desired state of pods. However, in most real-world cases, Deployments are preferred because they are more flexible and easier to manage.

**🧹 Infrastructure cleanup**

```bash
# Delete the ReplicaSet and the pods it manages
kubectl delete rs my-replicaset
```

## 6. Deployments in Kubernetes

**Introduction to Deployments:** Deployments in Kubernetes provide a higher-level pod management mechanism compared to ReplicaSets. They support controlled updates, rollback to previous versions, and automation of the application rollout process.

**Differences between Deployments and ReplicaSets**

ReplicaSets only manage how many pods should be running, while Deployments add an extra abstraction layer that allows application updates to be managed. Specifically:

- **ReplicaSets** ensure that a specified number of pods are always available.
- **Deployments** create and manage ReplicaSets, allowing version upgrades and rollbacks to previous versions.
- With a Deployment, we can change the container image without manually managing ReplicaSets.

Navigate to the example directory:

```bash
cd ~/cloud-uth/code/06_deployments
```

Create a **Deployment**

Example `basic-deployment.yaml` file for a Deployment:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: my-deployment
spec:
  replicas: 3
  selector:
    matchLabels:
      app: my-app
  template:
    metadata:
      labels:
        app: my-app
    spec:
      containers:
      - name: my-container
        image: nginx:latest
        ports:
        - containerPort: 80
```

To run the deployment above:

```bash
kubectl apply -f basic-deployment.yaml
```

After that, you can inspect the pod status:

```bash
kubectl get pods -o wide
```

You should see three pods running with the label `app=my-app`.

**Additional Deployment use cases**

Deployments can be used for several purposes beyond simply starting an application.

**Rolling updates:** They allow a gradual upgrade of an application with no service interruption. Create the file `myrolling_deployment.yaml` with the following content.

To perform a gradual transition from an old nginx version to a new one, you only need to modify the `image` field in the Deployment. The following example starts from `nginx:1.14` and upgrades to `nginx:latest` using a rolling update.

**Example YAML with rolling update (upgrade from an older nginx version to a newer one):**

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: my-deployment
spec:
  replicas: 3
  selector:
    matchLabels:
      app: my-app
  template:
    metadata:
      labels:
        app: my-app
    spec:
      containers:
      - name: my-container
        image: nginx:1.14  # Older Nginx version
        ports:
        - containerPort: 80
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxSurge: 1              # Maximum number of extra pods that may be created during the update
      maxUnavailable: 1        # Maximum number of pods that may be unavailable during the update
```

**Run it:**

```bash
kubectl apply -f myrolling_deployment.yaml
```

**Result:** The deployment is installed with the older nginx version.

**Steps to upgrade to the new version (`nginx:latest`)**

Initially, the old version (`nginx:1.14`) is running.

Modify the nginx version in `myrolling_deployment.yaml` so that it uses the latest version, `nginx:latest`:

```yaml
image: nginx:latest  # New Nginx version
```

Update the **Deployment**: after making the change, apply the Deployment again with `kubectl apply`.

```bash
kubectl apply -f myrolling_deployment.yaml
```

Kubernetes will perform a gradual transition from `nginx:1.14` to `nginx:latest` using a rolling update, creating new pods with the new version and progressively removing the old ones.

**Monitor the rollout**

You can monitor the rollout progress with:

```bash
kubectl rollout status deployment/my-deployment
```

**Rollback** to a previous version: revert to the previous ReplicaSet if a problem is detected.

```bash
kubectl rollout undo deployment my-deployment
```

**Result:** The Deployment returns to the previous stable version.

With the following command, we can inspect the deployment revision history:

```bash
kubectl rollout history deployment my-deployment
```

**Blue-green deployments:** Two versions of the same application can coexist at the same time, allowing very fast cutover.

File `blue-deployment.yaml`:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: blue-deployment
spec:
  replicas: 3
  selector:
    matchLabels:
      app: my-app
  template:
    metadata:
      labels:
        app: my-app
    spec:
      containers:
      - name: my-container
        image: nginx:1.14
```

File `green-deployment.yaml`:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: green-deployment
spec:
  replicas: 3
  selector:
    matchLabels:
      app: my-app
  template:
    metadata:
      labels:
        app: my-app
    spec:
      containers:
      - name: my-container
        image: nginx:latest
```

**Run them:**

```bash
kubectl apply -f blue-deployment.yaml
kubectl apply -f green-deployment.yaml
```

**Result:** Both versions will run simultaneously, allowing fast switchover by changing the Service selector.

With these features, Deployments provide a flexible and reliable way to manage applications in Kubernetes.

**🧹 Infrastructure cleanup**

After you finish testing Deployments, rolling updates, and blue-green deployments, you can clean up the resources by running:

```bash
# Delete the Deployment used for the basic example and rolling update
kubectl delete -f basic-deployment.yaml

# Delete the blue-green Deployments
kubectl delete -f blue-deployment.yaml
kubectl delete -f green-deployment.yaml
```

## 7. StatefulSets in Kubernetes

**Introduction to StatefulSets:** StatefulSets in Kubernetes are used to manage applications that require persistent identity and state retention (stateful applications). Unlike Deployments and ReplicaSets, StatefulSets guarantee stable identity (stable pod names) and retain storage even after pod restarts (persistent volumes).

**Differences between StatefulSets and Deployments**

- **Stable pod names:** Pods in a StatefulSet receive predictable names with increasing ordinals (for example, `my-app-0`, `my-app-1`).
- **Stable Persistent Volumes:** Each pod has its own volume, which is not automatically deleted when the pod terminates.
- **Ordered startup and termination:** Pods are started and terminated sequentially, in a defined order.

Navigate to the example directory:

```bash
cd ~/cloud-uth/code/07_statefulsets
```

**Create a StatefulSet**

Example `statefulset.yaml` file:

```yaml
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: my-statefulset
spec:
  serviceName: "my-service"
  replicas: 3
  selector:
    matchLabels:
      app: my-app
  template:
    metadata:
      labels:
        app: my-app
    spec:
      containers:
      - name: my-container
        image: nginx:latest
        volumeMounts:
        - name: my-volume
          mountPath: /data
  volumeClaimTemplates:
  - metadata:
      name: my-volume
    spec:
      accessModes: [ "ReadWriteOnce" ]
      resources:
        requests:
          storage: 1Gi
```

**Run the StatefulSet**

```bash
kubectl apply -f statefulset.yaml
```

After running the command, you can view the generated pods with:

```bash
kubectl get pods
```

You will notice pod names such as `my-statefulset-0`, `my-statefulset-1`, and `my-statefulset-2`, and they will start sequentially.

To view the Persistent Volume Claims that were created:

```bash
kubectl get pvc
```

You will notice that each pod has its own Persistent Volume Claim (`my-volume-my-statefulset-0`, `my-volume-my-statefulset-1`, and so on), which remains bound to the corresponding pod even after termination.

**Verify data persistence on Persistent Volumes**

To test whether a Persistent Volume keeps its data even after the pod is terminated, run:

```bash
kubectl exec -it my-statefulset-0 -- /bin/sh
```

Inside the pod, create a file on the mounted volume:

```bash
echo "Hello Kubernetes" > /data/testfile.txt
```

```bash
exit
```

Now delete the pod:

```bash
kubectl delete pod my-statefulset-0
```

Once the pod is recreated, reconnect:

```bash
kubectl exec -it my-statefulset-0 -- /bin/sh
```

and check whether the file still exists:

```bash
cat /data/testfile.txt
```

If the output is `Hello Kubernetes`, then the Persistent Volume has preserved its data, proving that the volume remains attached to the same pod even after a restart.

**Additional StatefulSet use cases**

StatefulSets are appropriate for applications that require ordered startup and stable storage, such as:

- **Databases** (for example, MySQL, PostgreSQL, MongoDB)
- **Distributed systems** (for example, Kafka, Zookeeper, Elasticsearch)
- **File storage systems**

When managed correctly, StatefulSets provide a reliable solution for deploying stateful applications in Kubernetes.

**🧹 Infrastructure cleanup**

After testing the StatefulSet, you can clean up the resources with:

```bash
# Delete the StatefulSet (its pods will also be deleted)
kubectl delete -f statefulset.yaml

# Check whether PVCs are still present (one for each pod)
kubectl get pvc

# Delete the automatically created Persistent Volume Claims
kubectl delete pvc my-volume-my-statefulset-0
kubectl delete pvc my-volume-my-statefulset-1
kubectl delete pvc my-volume-my-statefulset-2
```

## 8. DaemonSets in Kubernetes

**Introduction to DaemonSets:** DaemonSets in Kubernetes are used to run pods on **every node** in a cluster. They are useful for workloads such as log collection, monitoring agents, and network services that should run everywhere.

**Differences between DaemonSets and Deployments**

- **Runs on every node:** Unlike Deployments, DaemonSets ensure that each node has one copy of the pod.
- **Automatically added to new nodes:** When a new node is added to the cluster, the DaemonSet automatically schedules a pod there.
- **Does not use ReplicaSets:** DaemonSets do not depend on ReplicaSets, since the number of pods is determined only by the number of nodes.

Navigate to the example directory:

```bash
cd ~/cloud-uth/code/08_daemonsets
```

**Create a DaemonSet**

Example `fluentd-daemonset.yaml` file for a DaemonSet using Fluentd:

```yaml
apiVersion: apps/v1
kind: DaemonSet
metadata:
  name: fluentd-daemonset
spec:
  selector:
    matchLabels:
      name: fluentd-pod
  template:
    metadata:
      labels:
        name: fluentd-pod
    spec:
      containers:
      - name: fluentd
        image: fluent/fluentd:v1.14-1
        resources:
          limits:
            memory: 200Mi
            cpu: 100m
        volumeMounts:
        - name: varlog
          mountPath: /var/log
      volumes:
      - name: varlog
        hostPath:
          path: /var/log
```

**Run the DaemonSet**

```bash
kubectl apply -f fluentd-daemonset.yaml
```

After running it, you can inspect the DaemonSet pods on all nodes with:

```bash
kubectl get pods -o wide
```

You should observe one Fluentd pod on each worker node in the cluster.

**Collecting and printing metrics with Fluentd**

We can use Fluentd to collect metrics from all pods and nodes in the cluster.

**View logs** from all **Fluentd pods**

To inspect the logs collected from all nodes via Fluentd, use:

```bash
kubectl logs -l name=fluentd-pod --all-containers=true --tail=50
```

This command displays the latest 50 log lines from all Fluentd pods in the cluster.

**Additional DaemonSet use cases**

DaemonSets are useful in many scenarios, such as:

- **Log collection** with Fluentd, Logstash, or other agents
- **Monitoring** with Prometheus Node Exporter or Datadog Agent
- **Network services** such as CNI plugins (Calico, Flannel) for cluster networking

With DaemonSets, we can ensure that critical services run uniformly across all nodes in the cluster.

**🧹 Infrastructure cleanup**

After finishing your tests with the DaemonSet (for example, Fluentd on every node), you can delete the resources with:

```bash
# Delete the DaemonSet
kubectl delete -f fluentd-daemonset.yaml
```

## 9. Secrets

In Kubernetes, **Secrets** are used to store sensitive data securely, such as passwords or API tokens. In this example, we will see how to use a Secret to provide database credentials to an application, making them available inside the pod as files through a volume.

Navigate to the example directory:

```bash
cd ~/cloud-uth/code/09_Secrets
```

**Step 1: Create the Secret**

We create a Secret containing credentials (for example, for a database):

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: db-credentials
type: Opaque
data:
  username: cG9zdGdyZXM=      # "postgres" in base64
  password: c3VwZXJzZWNyZXQ=  # "supersecret" in base64
```

To create the Secret:

```bash
kubectl apply -f db-credentials.yaml
```

To view the available secrets:

```bash
kubectl get secrets
```

**Step 2: Use the Secret through a volume**

Below is a pod example where the Secret is mounted as a volume. The application can read the credentials from the files `/etc/db-credentials/username` and `/etc/db-credentials/password`:

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: app-with-db
spec:
  containers:
  - name: my-app
    image: my-app-image
    volumeMounts:
    - name: secret-volume
      mountPath: "/etc/db-credentials"
      readOnly: true
  volumes:
  - name: secret-volume
    secret:
      secretName: db-credentials
```

Kubernetes will automatically create the files `username` and `password` in `/etc/db-credentials`, and the application can read them as plain text files.

To create the pod:

```bash
kubectl apply -f app-with-db.yaml
```

Using `k9s`, open a shell (press `s` on the created pod) and run:

```bash
cat /etc/db-credentials/username; echo
```

You will see:

```
postgres
```

and:

```bash
cat /etc/db-credentials/password; echo
```

You will see:

```
supersecret
```

This shows that the values were passed from Kubernetes into the pod and are available there. Press `Ctrl+d` to disconnect from the pod shell, and then `Ctrl+c` to exit `k9s`.

**🧹 Infrastructure cleanup**

To clean up the pod and secrets before moving to the next example, run:

```bash
kubectl delete -f .
```

**Attention:** Make sure you are inside the `09_Secrets` directory when you run the `delete` command.

Then leave the directory:

```bash
cd ..
```

## 10. ConfigMaps

In Kubernetes, **ConfigMaps** are used to store non-sensitive configuration parameters, such as usernames, service addresses, URLs, or any application setting that should not be treated as secret.

In this example, we will use a ConfigMap to store the database username and make it available to the application as a mounted file.

Navigate to the example directory:

```bash
cd ~/cloud-uth/code/10_ConfigMaps
```

**Step 1: Create the ConfigMap**

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: db-config
data:
  username: postgres
  host: db-service
```

To create the ConfigMap:

```bash
kubectl apply -f db-configmap.yaml
```

To view available ConfigMaps:

```bash
kubectl get configmaps
```

**Step 2: Use the ConfigMap through a volume**

Below is an example pod where the ConfigMap is mounted as a volume, allowing the application to read the database username and host from files:

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: app-with-configmap
spec:
  containers:
  - name: my-app
    image: nginx
    volumeMounts:
    - name: config-volume
      mountPath: "/etc/db-config"
      readOnly: true
  volumes:
  - name: config-volume
    configMap:
      name: db-config
```

With this configuration, the application can read:

- `/etc/db-config/username` for the username (for example, `postgres`)
- `/etc/db-config/host` for the database host

To create the pod:

```bash
kubectl apply -f pod-with-configmap.yaml
```

Using `k9s`, open a shell (press `s` on the created pod) and run:

```bash
cat /etc/db-config/username; echo
```

You will see:

```
postgres
```

Run:

```bash
cat /etc/db-config/host; echo
```

You will see:

```
db-service
```

This confirms that the values were passed from Kubernetes into the pod and are available there. Press `Ctrl+d` to disconnect from the pod shell, and then `Ctrl+c` to exit `k9s`.

**🧹 Infrastructure cleanup**

To clean up the pod and ConfigMaps before moving to the next example, run:

```bash
kubectl delete -f .
```

**Attention:** Make sure you are inside the `10_ConfigMaps` directory when you run the `delete` command.

## 11. ConfigMap and Secrets for deploying a web server with Postgres

**Short description**

Below is a complete Kubernetes example containing:

✅ **A PostgreSQL pod**
- With a **Persistent Volume** through a PVC
- It receives connection settings from a **Secret** (`password`) and a **ConfigMap** (`username`, `database name`)

✅ **A web server pod** (simple PHP)
- Connects to the database
- Receives config from the same Secret and ConfigMap
- Displays table data from the database on a web page

The **PostgreSQL container** runs an **init SQL script** that creates the database and a table with sample data.

The **web server container** is ready to use, based on **`php:apache`**, with an `index.php` file that reads data from the database.

Navigate to the example directory:

```bash
cd ~/cloud-uth/code/11-web-pgsql-demo
```

**ℹ️ Important notes — summary**

**🔐 User and database initialization in PostgreSQL**

This is defined through:

- `POSTGRES_USER` (from ConfigMap)
- `POSTGRES_DB` (from ConfigMap)
- `POSTGRES_PASSWORD` (from Secret)

These variables apply **only at first startup**, when the volume is **empty**. If the PVC already contains data, they do not change the existing user or password.

**🗃️ Table and sample data creation**

The `init.sql` file is executed automatically on first startup through the path `/docker-entrypoint-initdb.d/init.sql`. It creates the `my_table` table and inserts sample data.

**ℹ️ Important notes — detailed version**

**🔐 How the PostgreSQL user is initialized**

In the provided example, the PostgreSQL **user password** is initialized through **environment variables** that are read from the Secret and ConfigMap when the PostgreSQL container starts.

**📌 Specifically:**

The `postgres:15` container (like all official PostgreSQL images) supports the following environment variables:

| **Variable** | **Description** |
| --- | --- |
| `POSTGRES_USER` | Username (for example, `postgres`) |
| `POSTGRES_DB` | Database name (for example, `myappdb`) |
| `POSTGRES_PASSWORD` | User password |

These values come from:

`02-configmap.yaml` → `username`, `dbname`

`01-secret.yaml` → `password`

If the PersistentVolumeClaim is **new** (empty disk), the PostgreSQL container:

- Creates the user and the database
- Sets the password based on `POSTGRES_PASSWORD`

⚠️ If the PVC already contains data (for example, from a previous run), these variables **do not affect** the existing credentials. In that case, you must either change the password from inside PostgreSQL using SQL (`ALTER USER`) or delete the PVC (and its data).

**🔁 How this works in practice**

```yaml
    env:
    - name: POSTGRES_USER
      valueFrom:
        configMapKeyRef:
          name: db-config
          key: username
    - name: POSTGRES_DB
      valueFrom:
        configMapKeyRef:
          name: db-config
          key: dbname
    - name: POSTGRES_PASSWORD
      valueFrom:
        secretKeyRef:
          name: db-secret
          key: password
```

This means:

- The user `postgres` will be created (if it does not already exist)
- The database `myappdb` will be created
- The user `postgres` will have the password `supersecret` (from the `db-secret` Secret)

💡 All of this happens during the **first startup** of the container, when `/var/lib/postgresql/data` is **empty** (that is, when using a new PVC).

**🧩 Creating the table and initial data**

The `my_table` table is created automatically by an SQL script (`init.sql`) that is loaded via a `ConfigMap` and mounted into the PostgreSQL container under `/docker-entrypoint-initdb.d`.

The `CREATE TABLE` command uses `IF NOT EXISTS`, so the process is **idempotent** and safe across restarts.

If you have already run the container and the persistent data volume (PVC) still contains previous data, these variables **no longer have any effect**, because the database has already been initialized.

**Detailed steps**

**🔧 Step 1: Secret for the database password**

```bash
kubectl apply -f 01-secret.yaml
```

🔐 Creates the Secret with the PostgreSQL password (`supersecret` encoded in base64).

**🧩 Step 2: ConfigMap with database settings**

```bash
kubectl apply -f 02-configmap.yaml
```

📋 Includes: username, dbname, and host.

**💾 Step 3: ConfigMap with the initialization SQL**

```bash
kubectl apply -f init-sql-configmap.yaml
```

📄 Contains SQL commands to create the `my_table` table and insert sample data (`Alice`, `Bob`, `Charlie`).

**✅ Step 4: Persistent Volume Claim for the database**

```bash
kubectl apply -f 03-pvc.yaml
```

**🐘 Step 5: PostgreSQL pod**

```bash
kubectl apply -f 04-postgres.yaml
```

💾 Creates 1Gi of storage space for PostgreSQL data.

**✅ Step 6: Service for the database**

```bash
kubectl apply -f 05-postgres-service.yaml
```

🌐 Allows the other pods to find the database through DNS:

`postgres.<username>-priv.svc.cluster.local`

**✅ Step 7: Web application (PHP through ConfigMap)**

```bash
kubectl apply -f 06-web-content-configmap.yaml
```

📄 Creates `index.php` through a ConfigMap; the script reads data from the database.

**🌐 Step 8: Web server pod**

```bash
kubectl apply -f 07-webserver.yaml
```

Starts the web server using the image `webdevops/php-apache:8.1`, which includes the `pgsql` extension for PostgreSQL connectivity.

**✅ Step 9: Service for accessing the web server**

```bash
kubectl apply -f 08-webserver-service.yaml
```

At this point, the pod is running and the service is available. You can open:

`http://webserver-service.<username>-priv.svc.cluster.local/`

Or you can run the following command from the command line:

```bash
curl http://webserver-service.<username>-priv.svc.cluster.local
```

You should see output similar to the following:

```
<h1>Records from DB</h1><p>Alice</p><p>Bob</p><p>Charlie</p>
```

**📦 Bulk deployment via Makefile**

To run all steps together, use the Makefile provided in the directory. It includes two actions: `deploy` and `clean`.

```bash
make deploy
```

**🧼 Bulk cleanup**

```bash
make clean
```

## 12. Nginx and multiple web servers in Kubernetes

Navigate to the example directory:

```bash
cd ~/cloud-uth/code/12_nginx-proxy
```

### 12.1 Define the web servers (Deployments and Services)

**File:** `web-deployments.yaml`

We create two web servers that serve simple HTML pages.

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: web1
spec:
  replicas: 1
  selector:
    matchLabels:
      app: web1
  template:
    metadata:
      labels:
        app: web1
    spec:
      containers:
        - name: web1
          image: nginx
          volumeMounts:
            - name: web-content
              mountPath: /usr/share/nginx/html
      volumes:
        - name: web-content
          configMap:
            name: web1-html

---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: web2
spec:
  replicas: 1
  selector:
    matchLabels:
      app: web2
  template:
    metadata:
      labels:
        app: web2
    spec:
      containers:
        - name: web2
          image: nginx
          volumeMounts:
            - name: web-content
              mountPath: /usr/share/nginx/html
      volumes:
        - name: web-content
          configMap:
            name: web2-html
```

**File:** `web-services.yaml`

We define the Services that provide access to the web servers.

```yaml
apiVersion: v1
kind: Service
metadata:
  name: web1
spec:
  selector:
    app: web1
  ports:
    - protocol: TCP
      port: 80
      targetPort: 80
---
apiVersion: v1
kind: Service
metadata:
  name: web2
spec:
  selector:
    app: web2
  ports:
    - protocol: TCP
      port: 80
      targetPort: 80
```

### 12.2 Add content to the pages (ConfigMaps)

**File:** `web-configmaps.yaml`

We use ConfigMaps for the HTML page content.

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: web1-html
data:
  index.html: |
    <h1>Welcome to Web1</h1>

---
apiVersion: v1
kind: ConfigMap
metadata:
  name: web2-html
data:
  index.html: |
    <h1>Welcome to Web2</h1>
```

### 12.3 Define the nginx reverse proxy

**File:** `nginx-configmap.yaml`

We define the nginx configuration as a reverse proxy.

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: nginx-config
data:
  nginx.conf: |
    events {}

    http {
        upstream backend {
            server web1;
            server web2;
        }

        server {
            listen 80;

            location / {
                proxy_pass http://backend;
            }
        }
    }
```

**File:** `nginx-deployment.yaml`

We define the `Deployment` and `Service` for the nginx proxy.

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: nginx-proxy
spec:
  replicas: 1
  selector:
    matchLabels:
      app: nginx-proxy
  template:
    metadata:
      labels:
        app: nginx-proxy
    spec:
      containers:
        - name: nginx
          image: nginx
          ports:
            - containerPort: 80
          volumeMounts:
            - name: config-volume
              mountPath: /etc/nginx/nginx.conf
              subPath: nginx.conf
      volumes:
        - name: config-volume
          configMap:
            name: nginx-config
---
apiVersion: v1
kind: Service
metadata:
  name: nginx-service
spec:
  type: LoadBalancer
  selector:
    app: nginx-proxy
  ports:
    - protocol: TCP
      port: 80
      targetPort: 80
```

### 12.4 Deploy on Kubernetes

```bash
kubectl apply -f web-configmaps.yaml
kubectl apply -f web-deployments.yaml
kubectl apply -f web-services.yaml
kubectl apply -f nginx-configmap.yaml
kubectl apply -f nginx-deployment.yaml
```

### 12.5 Access the application

Open the following in your browser:

`http://nginx-service.<username>-priv.svc.cluster.local/`

Nginx will distribute requests alternately between **Web1** and **Web2**.

**🧹 Infrastructure cleanup**

After completing the tests with multiple web servers and the nginx reverse proxy, you can clean up the infrastructure with the following commands:

```bash
# Delete the nginx proxy (Deployment and Service)
kubectl delete -f nginx-deployment.yaml
kubectl delete -f nginx-configmap.yaml

# Delete the web servers (Deployments and Services)
kubectl delete -f web-deployments.yaml
kubectl delete -f web-services.yaml

# Delete the ConfigMaps for the HTML content
kubectl delete -f web-configmaps.yaml
```

## 13. Services — Headless and Load-Balanced

In this section, we examine two important kinds of Kubernetes Services: **Headless** and **Load-Balancing (ClusterIP)**. We will use a StatefulSet with two pods as an example.

### 13.1 Goal

- Understand the difference between Headless and Load-Balanced Services
- Apply these service types in practice with a StatefulSet

### 13.2 Theoretical background: ClusterIP and Headless Services

#### 13.2.1 ClusterIP (default Service type)

`ClusterIP` is the **default Service type** in Kubernetes. The API server creates a **virtual IP address (Cluster IP)** inside the cluster network and routes traffic to the pods that match the `selector`.

📚 *Documentation:* [ClusterIP - Kubernetes Docs](https://kubernetes.io/docs/concepts/services-networking/service/#type-clusterip)

**Characteristics:**
- Creates one virtual IP (`CLUSTER-IP`) that routes traffic to pods
- The service DNS name (`my-service.default.svc.cluster.local`) resolves to that IP
- All routing is handled internally through `kube-proxy`
- Suitable for use only from inside the cluster
- The service load-balances traffic equally across all pods that match the selector

#### 13.2.2 Headless Services (`clusterIP: None`)

When a Service is declared as Headless (with `clusterIP: None`), no virtual IP is created at all. Instead, DNS returns **all pod IPs** matching the `selector`.

📚 *More information:* [Headless Services in the Kubernetes documentation](https://kubernetes.io/docs/concepts/services-networking/service/#headless-services)

**Characteristics:**
- Defined with `clusterIP: None`
- The DNS name returns A/AAAA records for **each pod**
- Ideal for stateful applications (StatefulSets), databases, and workloads that require stable network identity
- Useful for clients that want to communicate directly with a specific pod

**Useful for:**
- StatefulSets where each pod needs a unique identity
- Direct client-to-pod communication (without kube-proxy)
- Solutions such as databases, quorum-based applications, and similar systems

**DNS behavior:**
- `my-service.<username>-priv.svc.cluster.local` → A/AAAA records for *each* pod (`pod-0`, `pod-1`, ...)
- `my-app-headless.<username>-priv.svc.cluster.local` → `[10.244.1.12, 10.244.2.15]`
- You can also refer to a full pod DNS name such as `pod-0.my-service.<username>-priv.svc.cluster.local`
- `my-app-0.my-app-headless.<username>-priv.svc.cluster.local` → `10.244.1.12`

---

### 13.3 Creating Headless and Load-Balanced Services

The folder `code/13_services` contains all the YAML files used in this example.

### 13.4 Run with the Makefile

Use `make deploy` to apply all resources:

```bash
make deploy
```

This:
- creates `my-app-headless` (headless service),
- creates `my-app-svc` (ClusterIP service), and
- creates the StatefulSet `my-app` with 2 pods (`my-app-0`, `my-app-1`).

---

To delete all resources, run:

```bash
make clean
```

---

### 13.5 What to expect

After applying the resources:

```bash
kubectl get pods
```

🎯 You should see two pods named `my-app-0` and `my-app-1`.

```bash
kubectl get svc
```

🎯 You should see two services: `my-app-headless` and `my-app-svc`. The latter will have a `CLUSTER-IP`.

---

### 13.6 Headless Service

```yaml
apiVersion: v1
kind: Service
metadata:
  name: my-app-headless
spec:
  clusterIP: None
  selector:
    app: my-app
  ports:
    - port: 80
      name: http
      targetPort: 80
```

### 13.7 Load-Balancing Service (ClusterIP)

```yaml
apiVersion: v1
kind: Service
metadata:
  name: my-app-svc
spec:
  type: ClusterIP
  selector:
    app: my-app
  ports:
    - port: 80
      targetPort: 80
```

### 13.8 StatefulSet with 2 pods

```yaml
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: my-app
spec:
  serviceName: my-app-headless
  replicas: 2
  selector:
    matchLabels:
      app: my-app
  template:
    metadata:
      labels:
        app: my-app
    spec:
      containers:
        - name: nginx
          image: nginx
          ports:
            - containerPort: 80
          volumeMounts:
            - name: html-volume
              mountPath: /usr/share/nginx/html
      volumes:
        - name: html-volume
          downwardAPI:
            items:
              - path: index.html
                fieldRef:
                  fieldPath: metadata.name
```

### 13.9 Test using `curl`

If you are connected to the cluster through VPN, run the following command multiple times. You should see a different `hostname` (pod name) if load balancing is working.

```bash
# ⚠️ Replace "ikons" below with your own username
curl my-app-svc.ikons-priv.svc.cluster.local
```

Likewise, run the following command multiple times:

```bash
# ⚠️ Replace "ikons" below with your own username
curl my-app-headless.ikons-priv.svc.cluster.local
```

Again, you should see a different `hostname` (pod name), but for a different reason: in this case `my-app-headless` resolves to two different IPs, and the `curl` client picks one of them at random.

### 13.10 Test DNS resolution

```bash
# ⚠️ Replace "ikons" below with your own username
nslookup my-app-svc.ikons-priv.svc.cluster.local
```

🎯 It will return **one IP** (the ClusterIP).

```bash
# ⚠️ Replace "ikons" below with your own username
nslookup my-app-headless.ikons-priv.svc.cluster.local
```

🎯 It will return **two IPs** — one for each pod.

```bash
# ⚠️ Replace "ikons" below with your own username
nslookup my-app-0.my-app-headless.ikons-priv.svc.cluster.local
```

🎯 It will return the IP of the specific pod (`my-app-0`).

```bash
# ⚠️ Replace "ikons" below with your own username
nslookup my-app-1.my-app-headless.ikons-priv.svc.cluster.local
```

🎯 It will return the IP of the specific pod (`my-app-1`).
