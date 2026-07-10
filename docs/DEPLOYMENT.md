# Deployment guide

## 1. Local, Docker Compose (fastest way to see it working)

```bash
git clone https://github.com/Kornelius99/data-governance-gateway.git
cd data-governance-gateway
docker compose up --build
```

Test it:

```bash
curl -X POST http://localhost:8000/validate \
  -H 'Content-Type: application/json' \
  -d '{"contract": "example_customer_v1", "record": {"name": "Jane Doe", "email": "jane@example.com", "age": 34}}'
```

## 2. Render (real cloud deployment, free tier)

1. Fork this repository to your own GitHub account.
2. Sign in to your own Render account at render.com (you create and control this account, not me).
3. Go to the Blueprints page and click New Blueprint Instance, then select your fork.
4. Render reads render.yaml and provisions the FastAPI service automatically.
5. Add your own contracts to the contracts/ directory in your fork before deploying, or mount a volume with your real contracts.

## 3. Any container platform

The Dockerfile is a standard Python image with no cloud-specific assumptions - it runs unmodified on ECS, Cloud Run, an existing Kubernetes cluster (add your own Deployment/Service manifests, or adapt the pattern from the pipeline-cost-observatory repo's Helm chart), or a plain VM with Docker installed.

## Adding your own contracts

Add a new YAML file to contracts/, following the shape of contracts/example_customer_v1.yaml. No restart is required if CONTRACTS_DIR is mounted as a volume and load_contract's cache is small (maxsize=64) - restart the service if you update a contract that was already cached during this process's lifetime.

## Honesty note

I have written and reviewed this deployment configuration carefully, but have not personally executed a Render deploy against a live account (I don't have a cloud account available to me). Please treat the first real deploy as a test run, and open an issue in this repo if something doesn't match reality.
