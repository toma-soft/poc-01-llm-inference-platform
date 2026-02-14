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

