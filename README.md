# 💵 Cash Flow Optimization for Retail Network Operations

This repository presents the implementation of two **linear programming models** designed to optimize **cash flow redistribution among retail stores** in Guadalajara, Mexico.  
The project integrates data analysis, mathematical modeling, and Python-based optimization to minimize operational and transportation costs in the handling of physical cash.

---

## 📂 Repository Structure

```bash
Data/
│
├── abonos.csv
├── distancias_tiendas_completas.csv
├── flujo_efectivo_semanal.csv
├── restricciones.docx
├── rop_po.csv
├── tipo_tiendas.csv
└── ventas.csv

imagenes/
├── Prestamos.jpeg
├── PrestamosPorTienda.jpeg
└── RutasMartes.jpeg

Notebooks/
├── eda_ventas.ipynb
├── Flujo_Coppel1.ipynb
├── Flujo_Coppel2.ipynb
├── Flujo_Coppel3.ipynb
└── optimizar_t.ipynb

Scripts/
├── coppel_martes.py
├── coppel_semana.py
├── graficas_tienda_operacionales.py
├── Graficas.py
├── iterar_modelo_dia3.py
└── modelo_dia.py

Presentation.pdf
Report_Cash_Flow.pdf
Reporte_Flujo_Efectivo.pdf
requirements.txt
README.md
```

---

## ⚙️ Project Overview

This project tackles the **uneven distribution of cash** among stores operating under different demand and sales dynamics.  
The models determine optimal cash transfers between stores to:

- Maintain each branch above its **Reorder Point (ROP)**.
- Minimize **total weekly costs**, including logistics, insurance, and transfer fees.
- Incorporate **operational constraints** such as vehicle capacity, minimum change, and mandatory deposits.

---

## 📊 Methodology

1. **Exploratory Data Analysis (EDA)**  
   - Aggregation of weekly sales and repayments.  
   - Detection of loan variability and daily cash flow trends.  
   - Definition of realistic operational thresholds (ROP, PO, minimum cash).

2. **Model 1 – Internal Transfers Optimization**  
   - Minimizes the transportation cost between donor and recipient stores.  
   - Considers distance, insurance, and handling costs.  
   - Constraints include cash limits and vehicle capacity.

3. **Model 2 – External Transfers Optimization**  
   - Activates when Model 1 cannot satisfy demand.  
   - Integrates **non-Coppel stores** for external cash injection.  
   - Balances physical and electronic transfer costs.

4. **Model Implementation**  
   - Built using Python and **PuLP** for linear programming.  
   - Automated daily execution with dynamic updates and OSRM route mapping.  
   - Visual analysis via **Leaflet** and **Matplotlib**.

---

## 📈 Results Summary

| Day        | Travel Cost ($) | Operational Cost ($) | Total Cost ($) |
|-------------|----------------|----------------------|----------------|
| Monday      | 869.10         | 26,956.60            | 27,825.70      |
| Tuesday     | 6,122.00       | 25,590.30            | 31,712.30      |
| Wednesday   | 10,605.50      | 25,916.50            | 36,522.10      |
| Thursday    | 10,993.00      | 24,274.40            | 35,267.50      |
| Friday      | 11,500.50      | 24,231.00            | 35,731.60      |
| Saturday    | 15,003.50      | 31,801.30            | 46,804.80      |
| Sunday      | 12,128.80      | 23,026.10            | 35,154.90      |
| **Total**   | **67,222.70**  | **181,796.40**       | **249,019.10** |

✅ The proposed models achieved a **total weekly cost reduction of $249,019.10 MXN**, optimizing liquidity and ensuring all stores remain operational while reducing security risk.

---

## 🧠 Key Insights

- **Data-driven decision-making**: Dynamic model adjusted daily using real operational inputs.  
- **Operational realism**: Integrated business rules, transfer fees, and safety constraints.  
- **Scalability**: Framework ready for expansion to multiple cities or retail networks.  
- **Visualization**: Generated OSRM-based optimized route maps for each day.

---

## 🧩 Technologies Used

- **Python 3.10+**
- **PuLP** / **OR-Tools**
- **Pandas**, **NumPy**, **Matplotlib**
- **Folium**, **OSRM**, **Geopy**
- **Jupyter Notebooks**

---

## 📘 Reports

- **[`Report_Cash_Flow.pdf`](Report_Cash_Flow.pdf)** — Analytical summary (English version)  
- **[`Reporte_Flujo_Efectivo.pdf`](Reporte_Flujo_Efectivo.pdf)** — Full report (Spanish version)

---

## 👥 Authors

- **Diego Vértiz Padilla**  
- **José Ángel Govea García**  
- **Daniel Alberto Sánchez Fortiz**  
- **Augusto Ley Rodríguez**  
- **Ángel Esparza Enríquez**

Tecnológico de Monterrey, School of Engineering and Sciences  
Guadalajara, Jalisco — México  

---

## 🔒 Confidentiality

All data presented in this repository is **synthetic or anonymized**.  
Company identifiers, customer information, and internal data have been excluded to comply with confidentiality agreements.

---

## 🧾 License

This project is distributed for **academic and research purposes only**.  
Commercial use or redistribution of internal data is strictly prohibited.
```
