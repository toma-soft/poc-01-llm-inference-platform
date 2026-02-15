# 🚀 LLM Inference Platform (PoC)

## 📌 Opis projektu

Projekt **poc-01-llm-inference-platform** to praktyczne laboratorium
DevOps + AI, którego celem jest zbudowanie mini platformy inferencyjnej
dla modeli LLM z wykorzystaniem Kubernetes, Helm, Prometheus, Grafana
oraz autoskalowania HPA.

Projekt ewoluował z prostego PoC do **mini platformy produkcyjnej klasy
"real-world ready"**, z monitoringiem, metrykami i autoskalowaniem CPU.

------------------------------------------------------------------------

## 🎯 Cele projektu

-   Budowa API dla inferencji LLM (FastAPI)
-   Uruchomienie runtime (Ollama) w Kubernetes
-   Monitoring metryk aplikacyjnych i infrastrukturalnych
-   Integracja z Prometheus + Grafana
-   Implementacja HPA (Horizontal Pod Autoscaler)
-   Przygotowanie chartów Helm pod przyszłe ArgoCD
-   Automatyczny bootstrap klastra

------------------------------------------------------------------------

## 🏗 Architektura

Użytkownik → LLM API (FastAPI) → LLM Runtime (Ollama) → Model (np.
gemma)

Monitoring: - Prometheus (kube-prometheus-stack) - Grafana (custom
dashboard) - metrics-server (CPU metrics dla HPA)

Autoskalowanie: - HPA dla `llm-api` - HPA dla `llm-runtime` (CPU-based +
behavior)

------------------------------------------------------------------------

## 📂 Struktura repozytorium

    api/
      Dockerfile
      main.py
      requirements.txt

    charts/
      llm-api/
      llm-runtime/

    platform/monitoring/
      dashboards/
      prometheus-stack/

    scripts/
      bootstrap.sh

    README.md

------------------------------------------------------------------------

## 📊 Monitoring metryk

Platforma posiada:

-   Prometheus (kube-prometheus-stack)
-   Grafana
-   Custom dashboard „LLM Platform Dashboard"

Dashboard zawiera:

-   Requests per second (RPS)
-   Average inference latency
-   P95 inference duration
-   Errors per second

Metryki aplikacyjne:

-   `llm_requests_total`
-   `llm_inference_seconds_bucket`
-   `llm_inference_seconds_sum`
-   `llm_inference_seconds_count`

Dashboard jest utrwalony jako ConfigMap (nie jest już ulotny).

------------------------------------------------------------------------

## 🔌 LLM API

Technologie: - FastAPI - httpx (async) - Prometheus client - Semaphore
(limit równoległych requestów)

Funkcjonalności: - `/generate` - `/health` - `/metrics`

Metryki: - liczba requestów - histogram czasu inferencji

Autoskalowanie: - HPA CPU-based - target CPU: 60% - minReplicas: 1 -
maxReplicas: 3

------------------------------------------------------------------------

## 🧠 LLM Runtime

Runtime oparty o **Ollama**.

Funkcjonalności: - uruchamianie modelu (np. gemma) - obsługa wielu
requestów - autoskalowanie HPA

HPA dla runtime:

-   target CPU: 70%
-   minReplicas: 1
-   maxReplicas: 2
-   behavior:
    -   szybki scale-up
    -   opóźniony scale-down (stabilization window)

Runtime skaluje się pod obciążeniem (CPU \~500% → 2 repliki), a po
zakończeniu obciążenia wraca do 1 pod.

------------------------------------------------------------------------

## ⚙️ Bootstrap klastra

Automatyczny skrypt:

    ./scripts/bootstrap.sh

Wykonuje:

-   tworzenie namespace
-   deployment llm-runtime
-   deployment llm-api
-   deployment Prometheus stack
-   aplikację ServiceMonitor

------------------------------------------------------------------------

## 📈 Co już działa

-   API z metrykami
-   Runtime z autoskalowaniem
-   Monitoring z dashboardem
-   CPU-based HPA
-   behavior w HPA
-   Automatyczny bootstrap
-   Helm charts gotowe pod GitOps

------------------------------------------------------------------------

## 🔧 Komendy operacyjne (PoC1)

Poniżej znajduje się zestaw komend używanych do pracy z PoC1 – lokalną platformą LLM Inference Platform uruchamianą na Minikube + Colima.

---

### 🧱 1. Uruchomienie klastra lokalnego

```bash
# Start Colima (Docker runtime)
colima start --memory 5 --cpu 4

# Start Minikube
minikube start --memory=4500 --cpus=4

# Weryfikacja
kubectl get nodes

# wlaczenie metryk minikube
minikube addons enable metrics-server

# budowanie LLM API
helm upgrade --install llm-api ./charts/llm-api -n llm

# budowanie LLM runtime
helm upgrade --install llm-runtime ./charts/llm-runtime -n llm

# Lokalny LLM 
kubectl port-forward svc/llm-runtime 11434:11434 -n llm

# Lokalne API
kubectl port-forward svc/llm-api -n llm 8000:8000

# Lokalna Grafana
kubectl port-forward -n monitoring svc/prometheus-grafana 3000:80

# Lokalny Prometheus
kubectl port-forward svc/prometheus-kube-prometheus-prometheus 9090 -n monitoring

```

------------------------------------------------------------------------

## 🔮 Kolejne kroki

-   Ingress + cert-manager
-   Custom metrics HPA (RPS-based)
-   Load testing (k6)
-   ArgoCD
-   Resource limits tuning
-   Production-grade values.yaml

------------------------------------------------------------------------

## 🏁 Status

Projekt edukacyjny + DevOps lab. Mini platforma inferencyjna gotowa do
dalszego rozwoju.

