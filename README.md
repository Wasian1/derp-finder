<div align="center">

<img height="120" src="https://i.pinimg.com/474x/c9/19/c5/c919c5a010aa8cf79c2e5c078e1b7aee.jpg" alt="Playwright Logo"/>

# Enterprise-Grade Derpy Card Purchases Go Brr
### The Ultimate Boilerplate for Scalable, Robust, and Modern Card Collection

![CI Status](https://github.com/nirtal85/Playwright-Python-Example/actions/workflows/devRun.yml/badge.svg)
![Nightly Build](https://github.com/nirtal85/Playwright-Python-Example/actions/workflows/nightly.yml/badge.svg)
[![Tests](https://img.shields.io/endpoint?url=https%3A%2F%2Fflakiness.io%2Fapi%2Fbadge%3Finput%3D%257B%2522badgeToken%2522%253A%2522badge-4G6NKalA9bX7seUqFAyqhs%2522%257D)](https://flakiness.io/nirtal85/Playwright-Python-Example)
[![uv](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/uv/main/assets/badge/v0.json)](https://github.com/astral-sh/uv)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)


</div>

---

## 🚀 About The Project

This repository is a **Production-Ready Reference Architecture** for feeding my derpy card addiction using **Playwright**, **Python** and ~~autism~~.

<p align="center">
    <img src="resources/images/slowpoke.jpg" alt="Automation College - Playwright Python Course" width="600" style="border-radius: 10px;" />
  </a>
</p>

### ✨ Key Features
* **Modern Tooling:** Powered by `uv` for blazing fast package management and `Ruff` for linting.
* **Accessibility First:** Integrated **Axe** scans to ensure your app is accessible to everyone.
* **Deep Debugging:** Full integration with **Playwright Traces** and Video recording linked directly to Allure Reports.
* **Cloud Scale:** Native integration with **BrowserStack** for cross-browser testing on real devices.
* **CI/CD Optimization:** Parallel execution strategies and dynamic version syncing for GitHub Actions.

---

## 🛠️ Tech Stack

| Tool                                                              | Description & Why We Use It                                      |
|-------------------------------------------------------------------|------------------------------------------------------------------|
| [Playwright](https://pypi.org/project/playwright/)                | The modern standard for reliable, flaky-free browser automation. |
| [Pytest](https://pypi.org/project/pytest/)                        | The most powerful testing framework for Python.                  |
| [Axe Playwright](https://pypi.org/project/axe-playwright-python/) | For automated accessibility (A11y) compliance testing.           |
| [Allure](https://pypi.org/project/allure-pytest/)                 | For beautiful, data-rich test reports including Traces & Video.  |
| [Pytest Split](https://pypi.org/project/pytest-split/)            | To intelligently split test suites for parallel execution.       |
| [Requests](https://pypi.org/project/requests/)                    | For API interactions and test data setup.                        |

### 🌐 Cloud Testing Provider

This project is powered by **[BrowserStack](https://www.browserstack.com)**, enabling high-scale cross-browser and mobile testing on real devices in the cloud.

---

## ⚙️ Getting Started

### 1. Clone

```bash
git clone https://github.com/nirtal85/Playwright-Python-Example
cd TCGScrape

### 2. Install (The Modern Way)

We use uv for lightning-fast installations.

Windows (PowerShell):


```bash
python -m pip install uv
python -m uv venv
.venv\Scripts\Activate.ps1
uv sync --all-extras --dev
playwright install
```

Mac/Linux:

```bash
python3 -m pip install uv
uv venv
source .venv/bin/activate
uv sync --all-extras --dev
playwright install
```

## 🏃‍♂️ Execution

Run all tests (Chromium by default):

```bash
pytest
```

Run specific suite (Tags):

```bash
pytest -m sanity
```

## 📊 Results, Traces & Debugging

We use Allure for reporting. To generate and open the report locally:

```bash
npx -y allure generate allure-results --output allure-report --open
```

### 🕵️‍♀️ Using the Trace Viewer

Navigate to the Playwright Trace Viewer.

Drag & Drop the trace file (located in test-results/) generated after a failure.

Time Travel: Move back and forth in the timeline to see exactly what happened (Network, DOM, Console).

---

<div align="center">

</div>