# Aerospace Manufacturing Execution System (MES)

### **End-to-End Production Lifecycle Management for Defense Industry**

> **Architectural Overview:** A scalable Manufacturing Execution System (MES) designed to digitize the production line of Unmanned Aerial Vehicles (UAVs). It bridges the gap between raw inventory, sub-assembly production, and final aircraft integration with strict traceability, role-based access control (RBAC), and predictive inventory logic.

![Main Dashboard](./screenshots/app_admin_1_anasayfa.png)

---

### 🏗️ System Architecture & Logic

This platform replaces legacy tracking methods with a relational database model, ensuring data integrity across the manufacturing floor.

| Module | Functionality | Business Logic |
| :--- | :--- | :--- |
| **Component Fabrication** | Part Production | Auto-serialization (UUID) & Team-based restrictions. |
| **Assembly Line** | Integration Logic | FIFO (First-In-First-Out) allocation & Interoperability Validation. |
| **Workforce** | RBAC Security | Strict separation of duties: *Fabricator*, *Assembler*, *Admin*. |
| **Inventory Intelligence** | Forecasting | Real-time "Zero Stock" warnings & soft-delete audit trails. |

---

### 🚀 Key Modules & Capabilities

#### 1. Strict Assembly Validation & Traceability
The system prevents production errors by enforcing compatibility rules. An *Avionics Team* cannot produce a *Wing*, and a *TB2 Wing* cannot be mounted on an *AKINCI* airframe.
* **Feature:** FIFO Auto-Allocation.
* **Safety:** Prevents cross-contamination of parts between active assembly lines.

![Assembly Line Interface](./screenshots/app_montajci_5_ucak_uret.png)

#### 2. Role-Based Production Flow (RBAC)
Security is handled via a custom permission layer built on Django Rest Framework.
* **Fabricators:** Can only view/produce parts assigned to their specific team type.
* **Assemblers:** Access the integration interface but cannot manufacture raw parts.
* **Admins:** Full oversight of the P&L and production metrics.

![Fabricator Interface](./screenshots/app_uretimci_2_parca_uretme_api_korumali_kendine_ait_olmayani_uretemez.png)

#### 3. Real-Time Inventory & Stock Intelligence
The system monitors critical stock thresholds in real-time.
* **Logic:** `/api/inventory/stock-levels/` endpoint calculates `AVAILABLE` vs `USED` assets instantly.
* **Alerts:** Triggers visual warnings on the dashboard when critical components hit zero stock.

![Inventory Monitoring](./screenshots/app_admin_5_parca_ucak_stok_izle.png)

---

### 🛠️ Technical Stack & Data Model

The application is built on a robust, containerized architecture designed for high availability.

* **Core Backend:** `Python 3.12+` `Django 5.2+`
* **API Layer:** `Django Rest Framework` (Standardized REST endpoints)
* **Database:** `PostgreSQL` (ACID Compliance & Relational Integrity)
* **Documentation:** `Drf-Spectacular` (Auto-generated Swagger/OpenAPI)
* **Containerization:** `Docker` & `Docker Compose`

#### Database Design (ER Diagram)
The data model utilizes `OneToOne` and `ForeignKey` relationships to ensure that a single part cannot be used in multiple airframes simultaneously.

![Database Relations](./screenshots/database_relations.png)

#### API Documentation (Swagger/OpenAPI)
Full interactive documentation provided for ERP integrations.

![Swagger UI](./screenshots/swagger_ui_redoc.png)

---

### 📦 Installation & Deployment

The system is fully containerized. A pre-built image is also available on Docker Hub.

**Option 1: Build from Source**
```bash
# Clone the repository
git clone [https://github.com/isikmuhamm/aerospace-manufacturing-execution-system.git](https://github.com/isikmuhamm/aerospace-manufacturing-execution-system.git)

# Build & Run via Docker
docker-compose up --build -d

```

**Option 2: Pull from Docker Hub**

```bash
docker pull isikmuhamm/uav-production-app:latest

```

**Access Points:**

* **App Dashboard:** `http://localhost:8000/app/login/`
* **API Docs:** `http://localhost:8000/api/schema/swagger-ui/`
* **Admin Panel:** `http://localhost:8000/admin/`

---

### ⚖️ Disclaimer

*Originally developed as a technical prototype demonstrating defense industry production standards (UAV Manufacturing).*

### 📜 License

This project is licensed under the MIT License.
