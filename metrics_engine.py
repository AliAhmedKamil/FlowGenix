import pandas as pd
import numpy as np

class MetricsEngine:
    """
    Core calculation engine.
    Transforms raw CSV data into structured performance metrics.
    """

    REQUIRED_COLUMNS = ['date', 'spend', 'clicks', 'impressions', 'conversions']

    def __init__(self, file_path: str):
        self.file_path = file_path
        self.df = None
        self.metrics = {}

    def _load_data(self):
        """Loads CSV and validates structure."""
        try:
            self.df = pd.read_csv(self.file_path)
            self._validate_columns()
            # Ensure numeric types for calculation columns
            cols_to_numeric = ['spend', 'clicks', 'impressions', 'conversions']
            for col in cols_to_numeric:
                self.df[col] = pd.to_numeric(self.df[col], errors='coerce').fillna(0)
            
            # Ensure date is datetime
            self.df['date'] = pd.to_datetime(self.df['date'])
            
        except FileNotFoundError:
            raise FileNotFoundError(f"File not found: {self.file_path}")
        except Exception as e:
            raise Exception(f"Error loading data: {str(e)}")

    def _validate_columns(self):
        """Validates that all required columns exist."""
        missing = [col for col in self.REQUIRED_COLUMNS if col not in self.df.columns]
        if missing:
            raise ValueError(f"Missing required columns: {missing}")

    def _calculate_metrics(self):
        """Computes core KPIs."""
        if self.df is None or self.df.empty:
            return

        # 1. Aggregations
        total_spend = self.df['spend'].sum()
        total_clicks = self.df['clicks'].sum()
        total_impressions = self.df['impressions'].sum()
        total_conversions = self.df['conversions'].sum()

        # 2. Ratios (Handling division by zero)
        ctr = (total_clicks / total_impressions * 100) if total_impressions > 0 else 0.0
        conversion_rate = (total_conversions / total_clicks * 100) if total_clicks > 0 else 0.0
        cost_per_conversion = (total_spend / total_conversions) if total_conversions > 0 else 0.0

        # 3. Temporal Performance (Best/Worst Day based on Conversion Count)
        # Tie-breaking: earlier date wins for best, later date for worst (implicit in sort)
        daily_performance = self.df.sort_values(by='date')
        
        best_day_row = daily_performance.loc[daily_performance['conversions'].idxmax()]
        worst_day_row = daily_performance.loc[daily_performance['conversions'].idxmin()]

        # 4. Structure Output
        self.metrics = {
            "total_spend": round(total_spend, 2),
            "total_clicks": int(total_clicks),
            "total_impressions": int(total_impressions),
            "total_conversions": int(total_conversions),
            "ctr": round(ctr, 2),
            "conversion_rate": round(conversion_rate, 2),
            "cost_per_conversion": round(cost_per_conversion, 2),
            "best_day": {
                "date": best_day_row['date'].strftime('%Y-%m-%d'),
                "conversions": int(best_day_row['conversions']),
                "spend": round(best_day_row['spend'], 2)
            },
            "worst_day": {
                "date": worst_day_row['date'].strftime('%Y-%m-%d'),
                "conversions": int(worst_day_row['conversions']),
                "spend": round(worst_day_row['spend'], 2)
            }
        }

    def process(self) -> dict:
        """Main execution method."""
        self._load_data()
        self._calculate_metrics()
        return self.metrics

# Standalone function for integration
def get_metrics(file_path: str) -> dict:
    engine = MetricsEngine(file_path)
    return engine.process()
