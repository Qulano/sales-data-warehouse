# 🏛️ Multi-Source ETL Pipeline & Relational Data Warehouse

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-blue.svg)](https://www.postgresql.org/)
[![Docker](https://img.shields.io/badge/Docker-Compose-2496ED.svg)](https://www.docker.com/)
[![Code Style](https://img.shields.io/badge/CLI-Rich-orange.svg)](https://github.com/Textualize/rich)

An automated production-ready **ETL (Extract, Transform, Load)** pipeline and analytical data warehouse designed to ingest, clean, and consolidate disparate sales data into an enterprise-grade **PostgreSQL** database running inside **Docker**.

---

## 📐 Architecture Overview
```text
+--------------------+      +--------------------+
|   dirty_data.csv   |      |  dirty_orders.csv  |
|  (Clients Dataset) |      |  (Orders Dataset)  |
+---------+----------+      +---------+----------+
          |                           |
          +-------------+-------------+
                        |
                        v
+------------------------------------------------+
|            In-Memory ETL Transform             |
|   - Type validation & string hygiene           |
|   - Integrity check: orphans rejection         |
+-----------------------+------------------------+
                        | (psycopg2 batch insert)
                        v
+------------------------------------------------+
|     PostgreSQL 16 Storage (Docker Container)   |
|   - Table: clients (PK: id)                    |
|   - Table: orders  (FK: client_id -> clients.id|
|   - Performance: B-Tree Index on client_id     |
+-----------------------+------------------------+
                        | (SQL Relational Aggregation)
                        v
+------------------------------------------------+
|    Financial Analytics & Executive Reporting   |
|   - Relational INNER JOIN                      |
|   - Revenue metrics via GROUP BY, SUM, COUNT   |
+------------------------------------------------+
```
---

## ⚡ Core Engineering Highlights

- **Multi-Source Ingestion & Hygiene:** Concurrently processes multiple dirty CSV sources, enforcing data types, rejecting malformed emails, negative prices, and invalid records.
- **Relational Integrity (Foreign Keys):** Strictly guarantees that no orphaned orders can enter the warehouse without an existing, validated client record.
- **Query Performance Optimization:** Custom B-Tree index (`idx_orders_client_id`) deployed on foreign keys to eliminate full table scans during heavy analytical `JOIN` operations.
- **Containerized Infrastructure:** One-command deployment using **Docker Compose** with isolated networking and persistent volume storage.
- **Modular CLI Architecture:** Granular execution using system flags (`--etl`, `--report`, or default all-in-one).
- **12-Factor Security:** Complete database credential isolation via `python-dotenv` and `.env.example` templates.

---

## 🚀 Quickstart & Setup

### 1. Clone the repository
```bash
git clone https://github.com/Qulano/sales-data-warehouse.git
cd sales-data-warehouse
```

### 2. Configure Environment
Copy the example configuration to your local .env:
```bash
cp .env.example .env #cp on Linux, macOS, PowerShell
```
```bash
copy .env.example .env #copy on cmd Windows
```

### 3. Launch PostgreSQL via Docker
Spin up the isolated database engine in the background:
```bash
docker compose up -d
```

### 4. Install Dependencies
```bash
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt
```
**Note for Windows PowerShell users:** If you encounter a script execution error (`PSSecurityException`), run the following command in PowerShell once to allow virtual environment activation:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope Process
```

### 5. Run the Pipeline
Execute the full automated workflow:
```bash
python pipeline.py
```

Or run granular stages using CLI flags:
```bash
python pipeline.py --etl     # Run only Extract, Transform, and Database Load
python pipeline.py --report  # Run only Relational Financial Reporting
```