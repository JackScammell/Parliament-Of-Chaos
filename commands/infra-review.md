---
description: Audit Dockerfiles, k8s manifests, and docker-compose for best practices
effort: medium
argument-hint: "[<path>] [--type <docker|k8s|compose|ci>]"
---

# Infra Review

Analyse infrastructure configuration files for security, performance, and operational best practices. Covers Dockerfiles, Kubernetes manifests, docker-compose files, and CI/CD configs.

## Usage

```
/infra-review [<path>] [--type <docker|k8s|compose|ci>]
```

**Examples**:
```
/infra-review                        # Auto-detect and review all infra files
/infra-review Dockerfile             # Review a specific Dockerfile
/infra-review --type k8s             # Review all Kubernetes manifests
/infra-review .github/workflows/     # Review CI/CD pipelines
```

## Options

- `<path>` (optional): Specific file or directory to review
- `--type` (optional): Filter to a specific type — `docker`, `k8s`, `compose`, `ci`

## Process

1. **Detect Infrastructure Files**
   - Dockerfiles, .dockerignore
   - docker-compose.yml / compose.yaml
   - Kubernetes manifests (Deployment, Service, Ingress, ConfigMap, etc.)
   - CI configs (.github/workflows/, .gitlab-ci.yml, Jenkinsfile)
   - Terraform / CloudFormation (if present)

2. **Dockerfile Analysis**
   - Layer caching efficiency (order of COPY/RUN)
   - Image size (multi-stage builds, minimal base images)
   - Running as root (security risk)
   - Unpinned base image tags (reproducibility)
   - Missing .dockerignore entries
   - Hardcoded secrets or credentials

3. **Kubernetes Analysis**
   - Missing resource limits and requests
   - No liveness/readiness probes
   - Privilege escalation (runAsRoot, privileged containers)
   - Missing network policies
   - Hardcoded ConfigMap values that should be secrets
   - Missing pod disruption budgets

4. **Docker Compose Analysis**
   - Network isolation between services
   - Volume mount security (host paths)
   - Missing restart policies
   - Exposed ports that should be internal

5. **CI/CD Analysis**
   - Caching configuration for faster builds
   - Unnecessary serial steps that could run in parallel
   - Missing matrix strategies for cross-version testing
   - Security: pull_request_target misuse, secret exposure

## Output

```markdown
# Infrastructure Review

## Dockerfile (3 issues)
| Severity | Issue | Line | Fix |
|----------|-------|------|-----|
| High | Running as root | 1 | Add USER directive |
| Medium | No multi-stage build | — | Split build and runtime stages |
| Low | Unpinned base image | 1 | Pin to specific digest |

## Kubernetes (2 issues)
| Severity | Issue | File | Fix |
|----------|-------|------|-----|
| High | No resource limits | deploy.yaml:15 | Add resources.limits |
| Medium | No liveness probe | deploy.yaml:20 | Add livenessProbe |
```
