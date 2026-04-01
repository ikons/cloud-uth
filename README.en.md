# 🌩️ Cloud Computing

Welcome to the repository for the **Cloud Computing** course of the Department of Informatics and Telecommunications at the University of Thessaly.

This repository contains:

✅ Examples using Docker & Docker Compose  
✅ A complete guide for connecting to the lab Kubernetes infrastructure via OpenVPN  
✅ Kubernetes implementations: Pods, Deployments, StatefulSets, Volumes, ConfigMaps, Secrets, and Services  
✅ Documentation in Markdown format with generated Word guides

## 📁 Documentation Structure

| Section | Greek Markdown | English Markdown | English Word Guide |
|--------|----------------|------------------|--------------------|
| Workstation setup | [docs/00_Preparatory-lab/README.md](docs/00_Preparatory-lab/README.md) | [docs/00_Preparatory-lab/README.en.md](docs/00_Preparatory-lab/README.en.md) | [odigoi/00_workstation-setup.en.docx](odigoi/00_workstation-setup.en.docx) |
| Docker lab | [docs/01_lab1-docker/README.md](docs/01_lab1-docker/README.md) | [docs/01_lab1-docker/README.en.md](docs/01_lab1-docker/README.en.md) | [odigoi/01_docker.en.docx](odigoi/01_docker.en.docx) |
| Kubernetes lab | [docs/01_lab1-k8s/README.md](docs/01_lab1-k8s/README.md) | [docs/01_lab1-k8s/README.en.md](docs/01_lab1-k8s/README.en.md) | [odigoi/02_kubernetes.en.docx](odigoi/02_kubernetes.en.docx) |

## 🌐 Language Availability

- The original material remains available in Greek.
- English content is provided in parallel files using the `.en.md` and `.en.docx` suffixes.
- Code examples remain functionally identical; only explanatory text and inline teaching comments were translated.

## 🚀 Getting Started

```bash
git clone https://github.com/ikons/cloud-uth.git
cd cloud-uth
```

The canonical example code lives under `code/`. Whenever a guide shows a complete example file, that block is synchronized from the repository source so the README and the runnable code stay identical.

## 🧭 Preparation Layout

- `code/00_workstation-setup`: the canonical workstation steps for WSL, Docker Desktop, native Docker Engine, and final environment validation

## 🧭 Example Layout

- `code/01_docker`: the progressive sequence of Docker examples
- `code/02_kubernetes`: the progressive sequence of Kubernetes examples, from the first Pod and Services up to HPA and the composite web application example

In the preparation path, `docs/00_Preparatory-lab` acts as the central guide, while the canonical scripts and snippets live in the per-step `README.md` and `README.en.md` files under `code/00_workstation-setup/*`.

In the Kubernetes sequence, `docs/01_lab1-k8s` now acts as the central onboarding and navigation guide, while the detailed runnable instructions live inside the per-step `README.md` and `README.en.md` files under `code/02_kubernetes/*`.

> 💡 Make sure you have installed:
> - `Docker Desktop` (with the WSL2 backend), or optionally a native `Docker Engine` inside WSL
> - OpenVPN Client
> - `kubectl` and `k9s`

## 🧭 Suggested Convention for Future Additions

For any new teaching material, keep the same naming pattern:

- Greek Markdown: `README.md`
- English Markdown: `README.en.md`
- Greek Word guide: `name.docx`
- English Word guide: `name.en.docx`

## 📝 Word Guides

The Word guides under `odigoi/` are generated from the Markdown files in `docs/` with Pandoc.
On Windows, `scripts/export-docx.ps1` and `make -C docs docx` first try Microsoft Word to refresh the table of contents after export and fall back to LibreOffice if Word automation is unavailable.
