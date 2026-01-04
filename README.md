# Aerospace Manufacturing Execution System (MES)

<div align="center">

![Python](https://img.shields.io/badge/Python-3.12+-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Django](https://img.shields.io/badge/Django-5.2+-092E20?style=for-the-badge&logo=django&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16+-316192?style=for-the-badge&logo=postgresql&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-Ready-2496ED?style=for-the-badge&logo=docker&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)

**End-to-End Production Lifecycle Management for Defense Industry**

[Features](#-key-features) • [Architecture](#-system-architecture) • [Installation](#-installation) • [API Docs](#-api-documentation) • [Screenshots](#-screenshots)

</div>

---

## 📋 Overview

A scalable **Manufacturing Execution System (MES)** designed to digitize the production line of Unmanned Aerial Vehicles (UAVs). This system bridges the gap between raw inventory, sub-assembly production, and final aircraft integration with strict traceability, role-based access control (RBAC), and predictive inventory logic.

> **Use Case:** Defense industry production standards for UAV Manufacturing (TB2, TB3, AKINCI, KIZILELMA platforms)

![Main Dashboard](./screenshots/app_admin_1_anasayfa.png)

---

## ✨ Key Features

### 🔐 Role-Based Access Control (RBAC)

Custom permission layer built on Django Rest Framework with strict separation of duties:

| Role           | Permissions                                     | Restrictions                     |
| :------------- | :---------------------------------------------- | :------------------------------- |
| **Fabricator** | View/produce parts assigned to their team       | Cannot access other team's parts |
| **Assembler**  | Access integration interface, assemble aircraft | Cannot manufacture raw parts     |
| **Admin**      | Full oversight, P&L metrics, user management    | —                                |

### 🛡️ Assembly Validation & Traceability

- **Compatibility Rules:** TB2 Wing cannot be mounted on AKINCI airframe
- **Team Restrictions:** Avionics Team cannot produce Wing components
- **FIFO Auto-Allocation:** First-In-First-Out part allocation
- **UUID Serialization:** Every part gets unique identifier for full traceability

### 📊 Real-Time Inventory Intelligence

- Live stock level monitoring via `/api/inventory/stock-levels/`
- Zero-stock visual warnings on dashboard
- Soft-delete audit trails for compliance
- Available vs Used asset tracking

---

## 🏗️ System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        PRESENTATION LAYER                        │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐  │
│  │   Web Dashboard │  │   Swagger UI    │  │   Admin Panel   │  │
│  │   (Templates)   │  │   (API Docs)    │  │   (Django)      │  │
│  └────────┬────────┘  └────────┬────────┘  └────────┬────────┘  │
└───────────┼─────────────────────┼─────────────────────┼─────────┘
            │                     │                     │
┌───────────▼─────────────────────▼─────────────────────▼─────────┐
│                          API LAYER                               │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │              Django Rest Framework (DRF)                  │   │
│  │  • Token Authentication    • Permission Classes          │   │
│  │  • Serializers             • ViewSets & Routers          │   │
│  └──────────────────────────────────────────────────────────┘   │
└─────────────────────────────────┬───────────────────────────────┘
                                  │
┌─────────────────────────────────▼───────────────────────────────┐
│                       BUSINESS LOGIC                             │
│  ┌────────────────┐  ┌────────────────┐  ┌────────────────┐     │
│  │   Fabrication  │  │    Assembly    │  │   Inventory    │     │
│  │    Service     │  │    Service     │  │    Service     │     │
│  └────────────────┘  └────────────────┘  └────────────────┘     │
└─────────────────────────────────┬───────────────────────────────┘
                                  │
┌─────────────────────────────────▼───────────────────────────────┐
│                        DATA LAYER                                │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │                    PostgreSQL 16+                         │   │
│  │      ACID Compliance • Relational Integrity • UUID PK    │   │
│  └──────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
```

### Database Schema

The data model utilizes `OneToOne` and `ForeignKey` relationships to ensure that a single part cannot be used in multiple airframes simultaneously.

![Database Relations](./screenshots/database_relations.png)

---

## 🛠️ Tech Stack

| Layer         | Technology                | Purpose                        |
| :------------ | :------------------------ | :----------------------------- |
| **Backend**   | Python 3.12+, Django 5.2+ | Core application framework     |
| **API**       | Django Rest Framework     | RESTful API endpoints          |
| **Database**  | PostgreSQL 16+            | ACID-compliant data storage    |
| **Auth**      | DRF Token Authentication  | Stateless API authentication   |
| **Docs**      | drf-spectacular           | Auto-generated OpenAPI/Swagger |
| **Container** | Docker, Docker Compose    | Containerized deployment       |

---

## 🚀 Installation

### Prerequisites

- Docker & Docker Compose
- Git

### Option 1: Docker Compose (Recommended)

```bash
# Clone repository
git clone https://github.com/isikmuhamm/aerospace-manufacturing-execution-system.git
cd aerospace-manufacturing-execution-system

# Build and run
docker-compose up --build -d

# Run migrations & create superuser
docker-compose exec web python manage.py migrate
docker-compose exec web python manage.py createsuperuser
```

### Option 2: Pull from Docker Hub

```bash
docker pull isikmuhamm/uav-production-app:latest
docker run -p 8000:8000 isikmuhamm/uav-production-app:latest
```

### Option 3: Local Development

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your database credentials

# Run migrations
python manage.py migrate
python manage.py createsuperuser

# Start server
python manage.py runserver
```

---

## 🔗 Access Points

| Service       | URL                                            | Description                |
| :------------ | :--------------------------------------------- | :------------------------- |
| **Dashboard** | `http://localhost:8000/app/login/`             | Main application interface |
| **API Docs**  | `http://localhost:8000/api/schema/swagger-ui/` | Interactive Swagger UI     |
| **ReDoc**     | `http://localhost:8000/api/schema/redoc/`      | Alternative API docs       |
| **Admin**     | `http://localhost:8000/admin/`                 | Django admin panel         |

---

## 📚 API Documentation

Full OpenAPI 3.0 specification with interactive Swagger UI for ERP integrations.

### Core Endpoints

```
GET    /api/parts/                    # List all parts
POST   /api/parts/                    # Create new part
GET    /api/parts/{id}/               # Retrieve part details
DELETE /api/parts/{id}/               # Soft-delete part

GET    /api/aircraft/                 # List all aircraft
POST   /api/aircraft/                 # Assemble new aircraft
GET    /api/aircraft/{id}/            # Retrieve aircraft details

GET    /api/inventory/stock-levels/   # Real-time stock monitoring
GET    /api/teams/                    # List production teams
GET    /api/employees/                # List workforce
```

![Swagger UI](./screenshots/swagger_ui_redoc.png)

---

## 📸 Screenshots

<details>
<summary><b>Click to expand screenshots</b></summary>

### Admin Dashboard

![Admin Dashboard](./screenshots/app_admin_1_anasayfa.png)

### Part Production Interface

![Part Production](./screenshots/app_uretimci_2_parca_uretme_api_korumali_kendine_ait_olmayani_uretemez.png)

### Aircraft Assembly

![Aircraft Assembly](./screenshots/app_montajci_5_ucak_uret.png)

### Inventory Monitoring

![Inventory](./screenshots/app_admin_5_parca_ucak_stok_izle.png)

</details>

---

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## 📜 License

This project is licensed under the **MIT License** - see the [LICENSE](LICENSE) file for details.

---

## 👤 Author

**Muhammet Işık**

[![GitHub](https://img.shields.io/badge/GitHub-isikmuhamm-181717?style=flat-square&logo=github)](https://github.com/isikmuhamm)
[![LinkedIn](https://img.shields.io/badge/LinkedIn-Connect-0A66C2?style=flat-square&logo=linkedin)](https://linkedin.com/in/muisik)
