# Pulse

A small uptime monitor with a status page. You register URLs, Pulse checks them and shows what is up or down.

The app is intentionally simple. The point of the project is everything **around** it: how it is
built, deployed, observed and operated on Kubernetes.

> **Status:** early stage (v0.1). The API skeleton and the Kubernetes manifests are done; monitoring features are on the roadmap below.

## What works today (v0.1)

| Endpoint | Purpose | Used by |
|---|---|---|
| `GET /healthz` | Is the process alive? No dependencies checked. | liveness probe |
| `GET /readyz` | Can this instance serve traffic? Will check PostgreSQL (returns `503` when it can't). | readiness probe |

## Roadmap

| Version | Scope |
|---|---|
| v0 | FastAPI skeleton, health endpoints, Kubernetes manifests ← **you are here** |
| v0.2 | PostgreSQL + CRUD for monitored services, `/metrics` |
| v1 | Helm chart, GitOps deploy with Argo CD, Grafana dashboards |
| v2 | Go checker that probes the URLs concurrently; Terraform + AWS |
| v3 | Queue between checker and notifier, incidents, SLOs |

## Run locally

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --port 8000
curl -i localhost:8000/healthz
```

## Run on Kubernetes (minikube)

```bash
minikube start
minikube image build -t pulse:0.1.1 .      # builds the image inside minikube
kubectl apply -f k8s/
kubectl rollout status deploy/pulse
kubectl port-forward svc/pulse 8080:80
curl -i localhost:8080/readyz
```

## Design decisions

- **Liveness never checks dependencies.** A database outage must not restart every pod at once
  (a restart doesn't fix the database, and the crash-loop backoff delays recovery).
  The database check lives in the **readiness** probe, which only takes the pod out of the Service.
- **`minReadySeconds: 40`** (> liveness `initialDelay + failureThreshold × period`), so a pod that becomes Ready
  and is then killed by its liveness probe can't be counted as available and replace a healthy one during a rollout.
- **Resources:** memory `request = limit` (128Mi), CPU `request 50m / limit 100m` (Burstable QoS).
- **Failure injection:** setting `FORCE_UNREADY=true` makes `/readyz` return `503`. It is used to demo that a bad rollout
  stalls while the old pods keep serving traffic.

## Project layout

```
app/            FastAPI application
k8s/            Deployment and Service manifests
Dockerfile
requirements.txt
```
