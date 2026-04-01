# Kubernetes in the VDCLOUD lab

This guide serves as the main entry point for the Kubernetes part of the course. The practical material is organized as a sequence of self-contained examples under `code/02_kubernetes`, so that students work directly with the exact same files that appear in the guides instead of copying isolated snippets.

## What you receive by email

After filling in the access form, you receive:

- a username for your personal lab namespace
- the file `vdcloud-k8s.ovpn`
- the file `config` for `kubectl`

That username usually maps to a context/namespace of the form `<username>-priv`.

## Local clone of the repository

The main assumption of this guide is that you work from WSL and keep the repository inside your home directory. If you have already completed `00_workstation-setup`, this clone already exists and you only need to enter the same directory again. Otherwise, you can use the following idempotent form:

```bash
cd ~
if [ ! -d cloud-uth/.git ]; then
  git clone https://github.com/ikons/cloud-uth.git
fi
cd cloud-uth
```

To keep it up to date:

```bash
git pull
```

## OpenVPN and kubeconfig

### Connect to the VPN

On Windows, install the [OpenVPN client](https://openvpn.net/community-downloads/), import `vdcloud-k8s.ovpn`, and connect.

### Copy `config` into WSL

Assuming you downloaded it into your Windows `Downloads` folder:

```bash
mkdir -p ~/.kube
cp /mnt/c/Users/<windows-username>/Downloads/config ~/.kube/config
chmod 600 ~/.kube/config
```

## Quick connectivity check

```bash
kubectl config current-context
kubectl config view --minify -o jsonpath='{.clusters[0].cluster.server}{"\n"}'
kubectl get pods
```

Expected values:

- current context: `<username>-priv`
- cluster server: `https://source-code-master.cluster.local:6443`

In this cluster, work with namespace-scoped commands. Do not rely on cluster-admin commands such as `kubectl get nodes`.

## Tools

Minimum toolset:

- `kubectl`
- optionally `k9s`

Install `kubectl` on Ubuntu/WSL:

```bash
sudo apt-get install -y apt-transport-https ca-certificates curl gnupg
curl -fsSL https://pkgs.k8s.io/core:/stable:/v1.32/deb/Release.key | sudo gpg --dearmor -o /etc/apt/keyrings/kubernetes-apt-keyring.gpg
sudo chmod 644 /etc/apt/keyrings/kubernetes-apt-keyring.gpg
echo 'deb [signed-by=/etc/apt/keyrings/kubernetes-apt-keyring.gpg] https://pkgs.k8s.io/core:/stable:/v1.32/deb/ /' | sudo tee /etc/apt/sources.list.d/kubernetes.list
sudo chmod 644 /etc/apt/sources.list.d/kubernetes.list
sudo apt-get update
sudo apt-get install -y kubectl
```

Optionally, for `k9s`:

```bash
wget https://github.com/derailed/k9s/releases/download/v0.40.10/k9s_linux_amd64.deb
sudo dpkg -i k9s_linux_amd64.deb
echo "export KUBE_EDITOR=nano" >> ~/.bashrc
```

## Structure of the exercise sequence

| Step | Directory | Concept |
|------|-----------|---------|
| 01 | `code/02_kubernetes/01_first-pod` | Pod + `kubectl` |
| 02 | `code/02_kubernetes/02_services` | Services |
| 03 | `code/02_kubernetes/03_replicaset` | ReplicaSet |
| 04 | `code/02_kubernetes/04_deployments` | Deployments |
| 05 | `code/02_kubernetes/05_configmaps` | ConfigMaps |
| 06 | `code/02_kubernetes/06_secrets` | Secrets |
| 07 | `code/02_kubernetes/07_storage` | Persistent storage / PVC |
| 08 | `code/02_kubernetes/08_statefulsets` | StatefulSets |
| 09 | `code/02_kubernetes/09_stateless-app` | Stateless web app |
| 10 | `code/02_kubernetes/10_autoscaling` | Horizontal autoscaling with HPA |
| 11 | `code/02_kubernetes/11_web-app` | Composite web application example |

Steps `01` to `09` form the core teaching sequence of the lab. Steps `10` and `11` build on the same concepts and present more advanced applications of them.

## Execution rules

- Work from your WSL clone, usually `~/cloud-uth`
- Enter the directory of each step before running commands
- When using `kubectl port-forward`, if the local port is already taken change only the left-hand side, for example `8081:80`
- Clean up resources after each step so that you do not leave old workloads in your namespace

## First check

For the first exercise:

```bash
cd ~/cloud-uth/code/02_kubernetes/01_first-pod
kubectl apply -f nginx-pod.yaml
kubectl get pod my-nginx -o wide
kubectl delete -f nginx-pod.yaml
```

From that point onward, the recommended approach is to proceed sequentially through the `README.md` and `README.en.md` files in the following directories.
