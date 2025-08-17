# Demo sécurité CI/CD – Python Flask + CodeQL + Trivy + ZAP

Ce dépôt montre une mini application Flask et une pipeline GitHub Actions qui exécute:

SAST du code Python avec CodeQL

SCA des dépendances avec Trivy

scan de l’image Docker avec Trivy

DAST de base avec OWASP ZAP

Objectif: obtenir des rapports exploitables à chaque push et un statut bloquant en fin de job si des vulnérabilités graves sont détectées.

Remplace OWNER/REPO dans le badge ci-dessus par ton organisation et ton dépôt.

## Contenu du dépôt

.
├── app.py
├── requirements.txt
├── Dockerfile
├── .dockerignore
├── .zap/
│   └── rules.tsv
└── .github/
    └── workflows/
        └── security.yml

## Prérequis

Git installé en local

rien d’autre à installer pour la pipeline; les runners GitHub disposent de Docker

Remarque sur GitHub Advanced Security
Sur un dépôt privé, l’affichage des alertes CodeQL/Trivy dans l’onglet Security peut nécessiter GHAS. Les rapports restent disponibles dans les artefacts du run Actions.

Démarrage rapide

cloner et configurer Git

## vérifier les fichiers

app.py expose les routes / et /health

Dockerfile écoute sur le port 8080

.zap/rules.tsv contient des règles pour réduire le bruit des alertes

.github/workflows/security.yml contient le workflow complet

## pousser pour déclencher la pipeline

## consulter les résultats

onglet Actions → ouvre le run

artefacts à télécharger:

trivy-deps.txt

trivy-image.txt

zap-baseline.html

zap-warn.txt

onglet Security → Code scanning alerts si disponible


## Ce que fait chaque job
codeql

Analyse statique du code Python et génération d’un rapport SARIF. Ajuste le langage si besoin dans security.yml.

trivy_deps

Analyse des dépendances déclarées dans requirements.txt et autres manifestes.
Génère un SARIF et un rapport texte. Un garde-fou en fin de job échoue si Trivy a trouvé des vulnérabilités de sévérité élevée ou critique.

image_and_dast

Construit l’image Docker de l’app, la scanne avec Trivy, lance l’app dans un conteneur, puis exécute OWASP ZAP Baseline contre http://127.0.0.1:8080.
Les rapports ZAP sont déposés dans le workspace et uploadés comme artefacts. Le garde-fou d’image échoue en fin de job si Trivy a trouvé des vulnérabilités élevées ou critiques.


## Dépannage

erreur YAML en ligne 1
mettre la valeur de name: entre guillemets si elle contient un deux-points.

trivy: command not found
vérifier la présence de uses: aquasecurity/setup-trivy@v0.2.3.

image ZAP introuvable
utiliser ghcr.io/zaproxy/zaproxy:stable au lieu de owasp/zap2docker-stable.

pas d’artefacts ZAP
s’assurer que l’étape ZAP écrit vers /zap/wrk/... et que .zap/rules.tsv est présent.

l’app ne démarre pas
confirmer que /health répond et que le port est correct; consulter docker logs app dans l’étape de démarrage.

runner sans Docker
le job image_and_dast requiert Docker. Le désactiver temporairement avec if: false si nécessaire.
