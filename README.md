# 🚀 PoC #1 --- Lokalna Platforma Inference LLM (Kubernetes + Ollama)

## 📌 Opis projektu

Projekt demonstracyjny przedstawiający lokalną platformę inference LLM
uruchomioną w środowisku Kubernetes z wykorzystaniem:

-   🧠 **Ollama** jako runtime modelu LLM
-   ⚙️ **FastAPI** jako warstwy API
-   📦 **Helm** do zarządzania cyklem życia aplikacji
-   ☸️ **Minikube** jako lokalny klaster Kubernetes

System realizuje pełny przepływ inference:

Klient → FastAPI → Ollama → Model → Odpowiedź

------------------------------------------------------------------------

## 🏗 Architektura

    +--------------------+
    |      Klient        |
    |      (curl)        |
    +---------+----------+
              |
              v
    +--------------------+
    |   FastAPI (API)    |
    |  llm-llm-platform  |
    +---------+----------+
              |
              | http://ollama:11434
              v
    +--------------------+
    |      Ollama        |
    |   (Runtime LLM)    |
    +--------------------+

### Wykorzystane zasoby Kubernetes

-   Deployment -- warstwa API (FastAPI)
-   Deployment -- runtime LLM (Ollama)
-   Service (ClusterIP) -- komunikacja wewnętrzna
-   Helm -- zarządzanie release
-   Liveness & Readiness Probes
-   Resource Requests & Limits

------------------------------------------------------------------------

## 🛠 Wymagania

-   Docker / Colima
-   Minikube
-   kubectl
-   Helm
-   Python 3.11+

------------------------------------------------------------------------

## ▶️ Uruchomienie

### 1️⃣ Start klastra

``` bash
minikube start --driver=docker --memory=2899 --cpus=2
```

------------------------------------------------------------------------

### 2️⃣ Budowa obrazu API wewnątrz klastra

``` bash
minikube image build -t llm-api:0.1 ./api
```

------------------------------------------------------------------------

### 3️⃣ Deployment przez Helm

``` bash
helm upgrade --install llm ./llm-platform
```

------------------------------------------------------------------------

### 4️⃣ Pobranie modelu LLM

``` bash
kubectl exec -it deploy/ollama -- ollama pull tinyllama
```

------------------------------------------------------------------------

### 5️⃣ Test inference

``` bash
kubectl port-forward deploy/llm-llm-platform 8000:8000
```

W drugim terminalu:

``` bash
curl -X POST "localhost:8000/generate?prompt=Hello"
```

------------------------------------------------------------------------

## 🔄 Aktualizacja aplikacji

Po zmianie kodu API:

``` bash
minikube image build -t llm-api:<nowy-tag> ./api
helm upgrade llm ./llm-platform --set image.tag=<nowy-tag>
```

Rollout wykona się automatycznie -- bez potrzeby ręcznego restartu.

------------------------------------------------------------------------

## 🧠 Co demonstruje ten projekt

-   Uruchomienie LLM w Kubernetes lokalnie\
-   Komunikację service-to-service przez DNS klastra\
-   Zarządzanie cyklem życia aplikacji przez Helm\
-   Debugowanie ReplicaSet, ServiceAccount, Probes i ImagePull\
-   Kontrolę zasobów (requests / limits)\
-   Oddzielenie warstwy API od runtime modelu

------------------------------------------------------------------------

## 🚧 Możliwe dalsze kroki

-   PersistentVolume dla przechowywania modeli
-   InitContainer do automatycznego pobierania modelu
-   Integracja z ArgoCD (GitOps)
-   Monitoring (Prometheus)
-   Autoskalowanie (HPA)

------------------------------------------------------------------------

## 🎯 Cel PoC

Weryfikacja możliwości uruchomienia lekkiej, samowystarczalnej platformy
inference LLM w pełni w środowisku Kubernetes, bez zależności od usług
chmurowych.

------------------------------------------------------------------------

## 👤 Autor

Maciej Łuszcz\
TOMA Software
