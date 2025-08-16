## Dynamic Pricing & Demand Analysis for E-Commerce

## 📌 Project Overview

E-commerce businesses often lose potential revenue by failing to adjust prices in response to demand fluctuations and competitor strategies.
This project implements a dynamic pricing pipeline that integrates demand forecasting, price elasticity modeling, and optimization techniques to generate data-driven price recommendations.

## ⚠️ Note:
- Data is synthetically generated (not scraped or collected from external sources).
- Visualizations are limited to exported CSVs (Power BI integration not yet implemented).

## 🚀 Features
- Synthetic Data Generation: Created realistic datasets for products, competitor prices, and sales history.
- Data Preprocessing: Cleaned and structured raw data for modeling.
- Demand Forecasting: Applied time-series forecasting to predict future demand.
- Price Elasticity Modeling: Estimated how price changes impact demand.
- Price Optimization: Generated optimal price recommendations to maximize revenue.
- Pipeline Automation: End-to-end execution via run_pipeline.py.

## 📂 Project Structure
<pre>
dynamic_pricing_project/
│
├── data/                     # Input datasets (synthetic)
│   ├── clean_data.csv
│   ├── competitor_prices.csv
│   ├── products.csv
│   └── sales_history.csv
│
├── docs/                     # Documentation (if any)
│
├── notebooks/                # Jupyter notebooks for experimentation
│   ├── 01_data_collection.ipynb
│   ├── 02_data_cleaning.ipynb
│   ├── 03_forecasting.ipynb
│   ├── 04_price_elasticity.ipynb
│   └── 05_optimizer.ipynb
│
├── outputs/                  # Model outputs
│   ├── elasticity_results.csv
│   ├── forecast_demand.csv
│   └── price_recommendations.csv
│
├── reports/                  # Reports and exports
│   ├── figures/
│   └── powerbi_exports/
│
├── src/                      # Core Python scripts
│   ├── elasticity.py
│   ├── forecasting.py
│   ├── optimizer.py
│   └── utils.py
│
├── run_pipeline.py           # End-to-end execution script
├── requirements.txt          # Dependencies
├── README.md                 # Project documentation
└── .gitignore
</pre>

## ⚙️ Installation & Setup

1️⃣ Clone the Repository
<pre>git clone https://github.com/ViveK9740/Dynamic-Pricing-Demand-Analysis-for-E-Commerce.git</pre>

2️⃣ Install Dependencies
<pre> pip install -r requirements.txt</pre>

3️⃣ Run the Pipeline
<pre>python run_pipeline.py</pre>

## 📊 Outputs

- Forecasted Demand → outputs/forecast_demand.csv
- Elasticity Results → outputs/elasticity_results.csv
- Price Recommendations → outputs/price_recommendations.csv
- These outputs can be further visualized in Power BI or other BI tools.

## 🔑 Key Skills Demonstrated

- Data Engineering (data cleaning, pipeline structuring)
- Time Series Forecasting
- Price Elasticity Analysis
- Optimization for Revenue Maximization
- Modular Python Development

## 📌 Future Enhancements

- Integrate real-world data sources via web scraping or APIs.
- Build interactive dashboards in Power BI or Streamlit.
- Deploy pipeline to the cloud (AWS / GCP / Azure) for scalability.

## 📝 License
- This project is for educational purposes. You are free to use and adapt it.

## 👨‍💻 Author
- **Vivek Y**
- 📧 Email: viveky9740@gmail.com  
