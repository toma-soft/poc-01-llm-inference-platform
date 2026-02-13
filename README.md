# 🚀 poc-01-llm-inference-platform

## 📌 Opis projektu

Proof of Concept platformy do inferencji LLM uruchomionej na Kubernetes,
zbudowanej w oparciu o:

-   🧠 **Ollama (llm-runtime)** -- runtime do obsługi modeli LLM
-   ⚡ **FastAPI (llm-api)** -- warstwa API z limiterem współbieżności
-   📊 **Prometheus** -- zbieranie metryk
-   📈 **Grafana** -- wizualizacja i dashboardy
-   📦 **Helm Charts** -- deklaratywne deploymenty
-   🔁 Gotowość pod przyszłe **ArgoCD (GitOps)**

Projekt został zaprojektowany tak, aby był: - Reprodukowalny - Przenośny
(portability-first) - Monitoring-first - Gotowy pod rozwój produkcyjny

------------------------------------------------------------------------

# 🏗 Architektura

``` mermaid
flowchart LR
    User -->|HTTP| LLM_API
    LLM_API -->|HTTP| LLM_RUNTIME
    LLM_API -->|/metrics| Prometheus
    Prometheus --> Grafana
```

------------------------------------------------------------------------

# ⚡ Quick Start (5 minut)

### 1️⃣ Uruchom klaster (np. Colima + Minikube)

Upewnij się, że masz min. 4--5GB RAM dla klastra.

### 2️⃣ Uruchom bootstrap

``` bash
./scripts/bootstrap.sh
```

Skrypt: - Tworzy namespace `llm` - Tworzy namespace `monitoring` -
Deployuje llm-runtime - Deployuje llm-api - Deployuje Prometheus stack -
Tworzy ServiceMonitor

### 3️⃣ Port-forward

``` bash
kubectl port-forward svc/llm-api -n llm 8000:8000
kubectl port-forward svc/prometheus-grafana -n monitoring 3000:80
```

### 4️⃣ Test requestu

``` bash
curl -X POST "http://localhost:8000/generate?prompt=2%2B2%3D%3F"
```

------------------------------------------------------------------------

# 📊 Monitoring i metryki

API eksportuje:

-   `llm_requests_total`
-   `llm_inference_seconds_bucket`
-   `llm_inference_seconds_sum`
-   `llm_inference_seconds_count`

### 📈 Dashboard Grafana

Dashboard zawiera:

-   Requests per second (RPS)
-   Average inference duration
-   P95 latency
-   Error rate

PromQL przykłady:

**RPS**

    rate(llm_requests_total[1m])

**Średni czas inferencji**

    rate(llm_inference_seconds_sum[1m]) 
    / rate(llm_inference_seconds_count[1m])

**P95**

    histogram_quantile(0.95, rate(llm_inference_seconds_bucket[1m]))

------------------------------------------------------------------------

# 🧠 llm-api -- cechy

-   Asynchroniczne requesty (httpx.AsyncClient)
-   Semaphore limiter
-   Dynamiczne wykrywanie aktywnego modelu
-   Histogram metryk
-   Logowanie z request_id

------------------------------------------------------------------------

# 📁 Struktura repozytorium

    charts/
      llm-runtime/
      llm-api/

    platform/
      monitoring/
        prometheus-stack/
        servicemonitor.yaml

    scripts/
      bootstrap.sh

    api/
      main.py

------------------------------------------------------------------------

# 🎯 Cele projektu

-   Demonstracja LLM inference platformy
-   Monitoring-first mindset
-   Gotowość pod GitOps
-   Fundament pod skalowanie (HPA, autoscaling, multi-model)

------------------------------------------------------------------------

# 🔮 Kolejne kroki

-   Autoscaling llm-api
-   Resource limits tuning
-   Load testing
-   ArgoCD deployment
-   Alerty w Prometheus
-   Tracing (OpenTelemetry)

------------------------------------------------------------------------

# 👨‍💻 Autor

Maciej Łuszcz\
TOMA Software\
DevSecOps \| Cloud Native \| AI Platform Engineering

------------------------------------------------------------------------

# 🏁 Status

✔️ LLM działa\
✔️ Monitoring działa\
✔️ Dashboard działa\
✔️ Bootstrap automatyzuje klaster

Projekt rozwijany dalej 🚀
