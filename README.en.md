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
| Preparatory lab | [docs/00_Preparatory-lab/README.md](docs/00_Preparatory-lab/README.md) | [docs/00_Preparatory-lab/README.en.md](docs/00_Preparatory-lab/README.en.md) | [odigoi/0_Preparatory lab_Docker-Desktop-wsl.en.docx](odigoi/0_Preparatory%20lab_Docker-Desktop-wsl.en.docx) |
| Docker lab | [docs/01_lab1-docker/README.md](docs/01_lab1-docker/README.md) | [docs/01_lab1-docker/README.en.md](docs/01_lab1-docker/README.en.md) | [odigoi/01_lab1-docker.en.docx](odigoi/01_lab1-docker.en.docx) |
| Kubernetes lab | [docs/01_lab1-k8s/README.md](docs/01_lab1-k8s/README.md) | [docs/01_lab1-k8s/README.en.md](docs/01_lab1-k8s/README.en.md) | [odigoi/01_lab1-k8s.en.docx](odigoi/01_lab1-k8s.en.docx) |

## 🌐 Language Availability

- The original material remains available in Greek.
- English content is provided in parallel files using the `.en.md` and `.en.docx` suffixes.
- Code examples remain functionally identical; only explanatory text and inline teaching comments were translated.

## 🚀 Getting Started

```bash
git clone https://github.com/ikons/cloud-uth.git
cd cloud-uth
```

> 💡 Make sure you have installed:
> - Docker Desktop (with WSL2 backend)
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
On Windows, `scripts/export-docx.ps1` and `make -C docs docx` also use Microsoft Word to refresh the table of contents after export.
