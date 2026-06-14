import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random

def generate_data(num_months=12):
    regions = ['Hà Nội', 'TP.HCM', 'Đà Nẵng', 'Hải Phòng']
    segments = ['Gen Z', 'Millennials', 'Gen X', 'Boomers', 'Mass', 'Affluent', 'VIP', 'VVIP', 'SME', 'Corporate', 'Student', 'Freelancer', 'Startups', 'Enterprise', 'Government']
    churn_reasons = ['Phí dịch vụ cao', 'Lãi suất không cạnh tranh', 'Chăm sóc khách hàng kém', 'Ứng dụng lỗi/chậm', 'Thủ tục rườm rà', 'Đối thủ khuyến mãi tốt', 'Không còn nhu cầu', 'Khác']
    
    start_date = datetime(2025, 1, 1)
    months = [start_date + pd.DateOffset(months=i) for i in range(num_months)]
    
    data = []
    
    region_ranges = {
        'TP.HCM': (4000, 8000),
        'Hà Nội': (2000, 4000),
        'Đà Nẵng': (800, 2000),
        'Hải Phòng': (200, 800)
    }
    
    segment_multipliers = {
        'Startups': 0.05,
        'SME': 0.1,
        'Corporate': 0.02,
        'Enterprise': 0.01,
        'Government': 0.005,
        'VIP': 0.1,
        'VVIP': 0.05
    }
    
    for region in regions:
        min_cust, max_cust = region_ranges[region]
        for segment in segments:
            for reason in churn_reasons:
                # Initialize beginning customers for this combination based on region scale

                base_customers = random.randint(min_cust, max_cust)
                if segment in segment_multipliers:
                    base_customers = max(5, int(base_customers * segment_multipliers[segment]))
                
                # Assign an Average Revenue Per User (ARPU)
                if segment in ['Startups', 'SME', 'Corporate', 'Enterprise', 'Government']:
                    arpu = random.uniform(10000000, 100000000) # 10M to 100M VND
                else:
                    arpu = random.uniform(500000, 5000000) # 500k to 5M VND
                base_mrr = base_customers * arpu
                
                for month in months:
                    new_customers = int(base_customers * random.uniform(0.01, 0.15))
                    lost_customers = int(base_customers * random.uniform(0.01, 0.1))
                    
                    net_customers = new_customers - lost_customers
                    running_total = base_customers + net_customers
                    
                    # Generate MRR data
                    expansion_mrr = new_customers * arpu * random.uniform(0.8, 1.2)
                    lost_mrr = lost_customers * arpu * random.uniform(0.8, 1.2)
                    net_mrr = expansion_mrr - lost_mrr
                    running_total_mrr = base_mrr + net_mrr
                    
                    churn_rate = lost_customers / base_customers if base_customers > 0 else 0
                    retention_rate = 1 - churn_rate
                    
                    # Randomly inject some data quality issues (~5% of the time)
                    has_issue = random.random() < 0.05
                    missing_records = random.randint(1, 10) if has_issue else 0
                    duplicate_customers = random.randint(1, 10) if (has_issue and random.random() < 0.3) else 0
                    invalid_churn = random.randint(1, 5) if (has_issue and random.random() < 0.2) else 0
                    
                    if missing_records > 0 or duplicate_customers > 0 or invalid_churn > 0:
                        dq_status = 'Cần kiểm tra'
                    else:
                        dq_status = 'Đạt'
                        
                    data.append({
                        'Month': month.strftime('%Y-%m-%d'),
                        'Region': region,
                        'Segment': segment,
                        'Churn_Reason': reason,
                        'Beginning_Customers': base_customers,
                        'New_Customers': new_customers,
                        'Lost_Customers': lost_customers,
                        'Net_Customers': net_customers,
                        'Running_Total': running_total,
                        'Beginning_MRR': base_mrr,
                        'Expansion_MRR': expansion_mrr,
                        'Lost_MRR': lost_mrr,
                        'Net_MRR': net_mrr,
                        'Running_Total_MRR': running_total_mrr,
                        'Churn_Rate': churn_rate,
                        'Retention_Rate': retention_rate,
                        'Missing_Records': missing_records,
                        'Duplicate_Customers': duplicate_customers,
                        'Invalid_Churn_Records': invalid_churn,
                        'Data_Quality_Status': dq_status,
                        'Last_Updated_Date': datetime.now().strftime('%Y-%m-%d')
                    })
                    
                    # Update base customers & MRR for next month
                    base_customers = running_total
                    base_mrr = running_total_mrr

    df = pd.DataFrame(data)
    return df

if __name__ == "__main__":
    df = generate_data(12)
    df.to_csv("customer_churn_governance_dataset.csv", index=False)
    print(f"Generated {len(df)} rows and saved to customer_churn_governance_dataset.csv")
