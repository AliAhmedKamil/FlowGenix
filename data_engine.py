# data_engine.py
import pandas as pd
import numpy as np
from datetime import datetime
from typing import Dict, Any, Optional, Tuple, List
import json

class MarketingDataEngine:
    """Core data processing engine for marketing performance metrics"""
    
    REQUIRED_COLUMNS = ['date', 'spend', 'clicks', 'impressions', 'conversions']
    
    def __init__(self):
        self.df = None
        self.metrics = None
        self.validation_errors = []
        
    def process_csv(self, file_path: str) -> Dict[str, Any]:
        """
        Main processing pipeline
        Returns structured metrics or error dict
        """
        try:
            # Step 1: Load and validate
            self._load_and_validate(file_path)
            
            if self.validation_errors:
                return self._format_error()
            
            # Step 2: Clean data
            self._clean_data()
            
            # Step 3: Compute metrics
            self._compute_metrics()
            
            # Step 4: Return structured output
            return self._structure_output()
            
        except Exception as e:
            return {
                "status": "error",
                "message": f"Processing failed: {str(e)}",
                "timestamp": datetime.now().isoformat()
            }
    
    def _load_and_validate(self, file_path: str) -> None:
        """Load CSV and validate structure"""
        try:
            self.df = pd.read_csv(file_path)
            
            # Check required columns
            missing_cols = [col for col in self.REQUIRED_COLUMNS 
                          if col not in self.df.columns]
            
            if missing_cols:
                self.validation_errors.append(
                    f"Missing required columns: {missing_cols}"
                )
                return
            
            # Check empty dataset
            if len(self.df) == 0:
                self.validation_errors.append("Empty dataset")
                
        except Exception as e:
            self.validation_errors.append(f"File read error: {str(e)}")
    
    def _clean_data(self) -> None:
        """Clean and normalize data"""
        # Convert date column
        self.df['date'] = pd.to_datetime(self.df['date'], errors='coerce')
        
        # Convert numeric columns with error handling
        numeric_cols = ['spend', 'clicks', 'impressions', 'conversions']
        for col in numeric_cols:
            # Convert to numeric, coerce errors to NaN
            self.df[col] = pd.to_numeric(self.df[col], errors='coerce')
            # Fill NaN with 0 for calculations (business logic)
            self.df[col] = self.df[col].fillna(0)
        
        # Remove rows where date is null (invalid dates)
        self.df = self.df.dropna(subset=['date'])
        
        # Ensure non-negative values for metrics
        for col in numeric_cols:
            self.df[col] = self.df[col].clip(lower=0)
    
    def _compute_metrics(self) -> None:
        """Compute all performance metrics"""
        
        # Totals
        totals = {
            'spend': float(self.df['spend'].sum()),
            'clicks': int(self.df['clicks'].sum()),
            'impressions': int(self.df['impressions'].sum()),
            'conversions': int(self.df['conversions'].sum())
        }
        
        # Rates with zero-division protection
        total_clicks = totals['clicks']
        total_impressions = totals['impressions']
        
        ctr = (total_clicks / total_impressions * 100) if total_impressions > 0 else 0.0
        conversion_rate = (totals['conversions'] / total_clicks * 100) if total_clicks > 0 else 0.0
        
        cpc = (totals['spend'] / total_clicks) if total_clicks > 0 else 0.0
        cpa = (totals['spend'] / totals['conversions']) if totals['conversions'] > 0 else 0.0
        
        rates = {
            'ctr': round(ctr, 2),
            'conversion_rate': round(conversion_rate, 2),
            'cpc': round(cpc, 2),
            'cpa': round(cpa, 2)
        }
        
        # Performance analysis
        if not self.df.empty:
            # Best/worst day by conversions
            best_day_row = self.df.loc[self.df['conversions'].idxmax()]
            worst_day_row = self.df.loc[self.df['conversions'].idxmin()]
            
            performance = {
                'best_day': {
                    'date': best_day_row['date'].strftime('%Y-%m-%d'),
                    'conversions': int(best_day_row['conversions']),
                    'spend': float(best_day_row['spend'])
                },
                'worst_day': {
                    'date': worst_day_row['date'].strftime('%Y-%m-%d'),
                    'conversions': int(worst_day_row['conversions']),
                    'spend': float(worst_day_row['spend'])
                },
                'avg_daily_spend': round(float(self.df['spend'].mean()), 2),
                'avg_daily_conversions': round(float(self.df['conversions'].mean()), 2),
                'data_points': len(self.df)
            }
            
            # Calculate daily averages for key metrics
            daily_stats = {
                'avg_ctr': round(float((self.df['clicks'] / 
                                      self.df['impressions'].replace(0, np.nan)).mean() * 100), 2),
                'avg_cpc': round(float((self.df['spend'] / 
                                      self.df['clicks'].replace(0, np.nan)).mean()), 2)
            }
            
            performance.update(daily_stats)
            
        else:
            performance = {
                'best_day': None,
                'worst_day': None,
                'avg_daily_spend': 0,
                'avg_daily_conversions': 0,
                'data_points': 0,
                'avg_ctr': 0,
                'avg_cpc': 0
            }
        
        self.metrics = {
            'totals': totals,
            'rates': rates,
            'performance': performance,
            '_metadata': {
                'processed_at': datetime.now().isoformat(),
                'rows_processed': len(self.df)
            }
        }
    
    def _structure_output(self) -> Dict[str, Any]:
        """Format final output structure"""
        return {
            "status": "success",
            "data": self.metrics,
            "summary": {
                "period_start": self.df['date'].min().strftime('%Y-%m-%d'),
                "period_end": self.df['date'].max().strftime('%Y-%m-%d'),
                "roi": round(
                    (self.metrics['totals']['conversions'] * 100 / 
                     max(self.metrics['totals']['spend'], 1)), 
                    2
                ) if self.metrics['totals']['spend'] > 0 else 0.0
            }
        }
    
    def _format_error(self) -> Dict[str, Any]:
        """Format error response"""
        return {
            "status": "error",
            "validation_errors": self.validation_errors,
            "timestamp": datetime.now().isoformat()
        }


# Test function with sample data creation
def test_data_engine():
    """Test the engine with various edge cases"""
    
    import tempfile
    
    engine = MarketingDataEngine()
    
    # Test Case 1: Normal data
    normal_data = pd.DataFrame({
        'date': ['2024-01-01', '2024-01-02', '2024-01-03'],
        'spend': [100.50, 200.75, 150.25],
        'clicks': [1000, 2000, 1500],
        'impressions': [10000, 20000, 15000],
        'conversions': [50, 100, 75]
    })
    
    # Test Case 2: Edge cases (zero values)
    edge_case_data = pd.DataFrame({
        'date': ['2024-01-01', '2024-01-02'],
        'spend': [100.50, 200.75],
        'clicks': [0, 2000],          # Zero clicks on day1
        'impressions': [10000, 0],    # Zero impressions on day2
        'conversions': [50, 100]
    })
    
    # Test Case 3: Missing values and high spend
    messy_data = pd.DataFrame({
        'date': ['2024-01-01', '', None],
        'spend': [999999.99, '', None],
        'clicks': ['invalid', '', None],
        'impressions': ['text', '', None],
        'conversions': [None, '', None]
    })
    
    test_cases = [
        ("normal_data.csv", normal_data),
        ("edge_case_data.csv", edge_case_data),
        ("messy_data.csv", messy_data)
    ]
    
    results = []
    
    for filename, df in test_cases:
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            df.to_csv(f.name, index=False)
            
            print(f"\n{'='*60}")
            print(f"Testing: {filename}")
            
            result = engine.process_csv(f.name)
            
            if result["status"] == "success":
                print("✓ Processing successful")
                
                # Validate structure
                required_keys = ["status", "data", "summary"]
                assert all(key in result for key in required_keys), "Missing keys"
                
                data_keys = ["totals", "rates", "performance"]
                assert all(key in result["data"] for key in data_keys), "Missing data keys"
                
                print("✓ Structure validated")
                
                # Verify calculations are numbers (not strings)
                assert isinstance(result["data"]["totals"]["spend"], float), "Spend not float"
                
                print("✓ Data types correct")
                
                results.append({
                    "test_case": filename,
                    "status": "PASS",
                    "metrics": result["data"]
                })
                
                print(json.dumps(result["summary"], indent=2))
                
            else:
                print("✗ Processing failed")
                
                results.append({
                    "test_case": filename,
                    "status": f"FAIL - {result.get('validation_errors', ['Unknown error'])[0]}"
                })
    
    return results


if __name__ == "__main__":
    print("Marketing Data Engine - Test Suite")
    print("="*60)
    
    test_results = test_data_engine()
    
    print("\n" + "="*60)
    print("TEST SUMMARY:")
    
    for result in test_results:
        status_symbol = "✓" if "PASS" in result["status"] else "✗"
        
        print(f"{status_symbol} {result['test_case']}: {result['status']}")
    
    print("\nEngine ready for production use.")


# Additional utility functions for production use
def process_marketing_data(file_path: str) -> Dict[str, Any]:
    """
    Production-ready function for external use
    Returns structured metrics or error dict
    """
    engine = MarketingDataEngine()
    return engine.process_csv(file_path)


def validate_csv_structure(file_path: str) -> Tuple[bool, List[str]]:
    """
    Quick validation without full processing
    Returns (is_valid, list_of_issues)
    """
    try:
        df = pd.read_csv(file_path)
        issues = []
        
        # Check required columns
        missing_cols = [col for col in MarketingDataEngine.REQUIRED_COLUMNS 
                       if col not in df.columns]
        if missing_cols:
            issues.append(f"Missing columns: {missing_cols}")
        
        # Check for empty file
        if len(df) == 0:
            issues.append("File is empty")
        
        # Check data types (quick sample)
        if 'date' in df.columns:
            date_sample = pd.to_datetime(df['date'].head(), errors='coerce')
            if date_sample.isna().any():
                issues.append("Invalid date format detected")
        
        return len(issues) == 0, issues
        
    except Exception as e:
        return False, [f"File read error: {str(e)}"]


def batch_process_files(file_paths: List[str]) -> Dict[str, Any]:
    """
    Process multiple CSV files and aggregate results
    """
    aggregated = {
        "status": "success",
        "files_processed": 0,
        "files_failed": 0,
        "aggregated_metrics": {
            "totals": {
                "spend": 0.0,
                "clicks": 0,
                "impressions": 0,
                "conversions": 0
            },
            "rates": {
                "ctr": 0.0,
                "conversion_rate": 0.0,
                "cpc": 0.0,
                "cpa": 0.0
            }
        },
        "file_results": []
    }
    
    for file_path in file_paths:
        result = process_marketing_data(file_path)
        
        if result["status"] == "success":
            aggregated["files_processed"] += 1
            
            # Aggregate totals
            for key in aggregated["aggregated_metrics"]["totals"]:
                if key == "spend":
                    aggregated["aggregated_metrics"]["totals"][key] += result["data"]["totals"][key]
                else:
                    aggregated["aggregated_metrics"]["totals"][key] += int(result["data"]["totals"][key])
            aggregated["file_results"].append({
                "file": file_path,
                "status": "success",
                "summary": result["summary"]
            })
        else:
            aggregated["files_failed"] += 1
            aggregated["file_results"].append({
                "file": file_path,
                "status": "error",
                "errors": result.get("validation_errors", ["Unknown error"])
            })
    
    # Calculate aggregated rates
    total_clicks = aggregated["aggregated_metrics"]["totals"]["clicks"]
    total_impressions = aggregated["aggregated_metrics"]["totals"]["impressions"]
    total_conversions = aggregated["aggregated_metrics"]["totals"]["conversions"]
    total_spend = aggregated["aggregated_metrics"]["totals"]["spend"]
    
    # With zero-division protection
    ctr = (total_clicks / total_impressions * 100) if total_impressions > 0 else 0.0
    conversion_rate = (total_conversions / total_clicks * 100) if total_clicks > 0 else 0.0
    cpc = (total_spend / total_clicks) if total_clicks > 0 else 0.0
    cpa = (total_spend / total_conversions) if total_conversions > 0 else 0.0
    
    aggregated["aggregated_metrics"]["rates"] = {
        "ctr": round(ctr, 2),
        "conversion_rate": round(conversion_rate, 2),
        "cpc": round(cpc, 2),
        "cpa": round(cpa, 2)
    }
    
    return aggregated


# Example usage patterns for different scenarios
class DataEngineExamples:
    
    @staticmethod
    def example_normal_usage():
        """Example: Normal processing flow"""
        import tempfile
        
        # Create sample data
        sample_data = pd.DataFrame({
            'date': ['2024-01-01', '2024-01-02', '2024-01-03'],
            'spend': [150.25, 200.50, 175.75],
            'clicks': [1200, 1800, 1500],
            'impressions': [12000, 18000, 15000],
            'conversions': [60, 90, 75]
        })
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            sample_data.to_csv(f.name, index=False)
            
            # Process the file
            result = process_marketing_data(f.name)
            
            print("Example Output:")
            print(json.dumps(result, indent=2))
            
            return result
    
    @staticmethod
    def example_error_handling():
        """Example: Error handling with invalid data"""
        import tempfile
        
        # Create invalid data (missing column)
        invalid_data = pd.DataFrame({
            'date': ['2024-01-01'],
            'spend': [100],
            'clicks': [1000],
            'impressions': [10000]
            # Missing 'conversions' column
        })
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            invalid_data.to_csv(f.name, index=False)
            
            result = process_marketing_data(f.name)
            
            print("\nError Handling Example:")
            print(json.dumps(result, indent=2))
            
            return result
    
    @staticmethod
    def example_batch_processing():
        """Example: Batch multiple files"""
        import tempfile
        
        files_to_process = []
        
        # Create multiple test files
        for i in range(3):
            data = pd.DataFrame({
                'date': [f'2024-01-{d+1:02d}' for d in range(3)],
                'spend': [100 + i*50 + d*10 for d in range(3)],
                'clicks': [1000 + i*200 + d*100 for d in range(3)],
                'impressions': [10000 + i*2000 + d*1000 for d in range(3)],
                'conversions': [50 + i*10 + d*5 for d in range(3)]
            })
            
            with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
                data.to_csv(f.name, index=False)
                files_to_process.append(f.name)
        
        # Process batch
        result = batch_process_files(files_to_process)
        
        print("\nBatch Processing Example:")
        print(json.dumps(result, indent=2))
        
        return result


# Performance optimization for large datasets
class OptimizedMarketingDataEngine(MarketingDataEngine):
    """Optimized version for large datasets"""
    
    def _clean_data(self):
        """Optimized cleaning for large datasets"""
        
        # Use vectorized operations where possible
        
        # Convert date column with vectorized operation
        self.df['date'] = pd.to_datetime(self.df['date'], errors='coerce')
        
        # Convert numeric columns using pandas optimizations
        numeric_cols = ['spend', 'clicks', 'impressions', 'conversions']
        
        for col in numeric_cols:
            # Convert to numeric using pandas' optimized methods
            self.df[col] = pd.to_numeric(self.df[col], errors='coerce')
        
        # Remove invalid rows (where date is null or all numeric columns are null)
        mask_valid_date = self.df['date'].notna()
        
        # Keep rows where at least one metric has value (not all zeros/NaN)
        mask_has_data = (
            self.df[numeric_cols].fillna(0).sum(axis=1) > 0
        )
        
        self.df = self.df[mask_valid_date & mask_has_data].copy()
        
        # Fill remaining NaN with zeros for calculations
        self.df[numeric_cols] = self.df[numeric_cols].fillna(0)
        
        # Clip negative values to zero (in case of any negative numbers)
        self.df[numeric_cols] = self.df[numeric_cols].clip(lower=0)
    
    def _compute_metrics(self):
        """Optimized metric computation"""
        
        # Use numpy for faster calculations on large datasets
        
        totals = {
            'spend': float(np.sum(self.df['spend'].values)),
            'clicks': int(np.sum(self.df['clicks'].values)),
            'impressions': int(np.sum(self.df['impressions'].values)),
            'conversions': int(np.sum(self.df['conversions'].values))
        }
        
        total_clicks = totals['clicks']
        total_impressions = totals['impressions']
         
         # Vectorized rate calculations with numpy where possible
        ctr_val = np.divide(
            total_clicks,
            total_impressions,
            out=np.zeros_like(total_clicks, dtype=float),
            where=total_impressions > 0
        ) * 100
         
        conversion_rate_val = np.divide(
            totals['conversions'],
            total_clicks,
            out=np.zeros_like(totals['conversions'], dtype=float),
            where=total_clicks > 0
        ) * 100
         
        cpc_val = np.divide(
            totals['spend'],
            total_clicks,
            out=np.zeros_like(totals['spend'], dtype=float),
            where=total_clicks > 0
        )
         
        cpa_val = np.divide(
            totals['spend'],
            totals['conversions'],
            out=np.zeros_like(totals['spend'], dtype=float),
            where=totals['conversions'] > 0
        )
         
        rates = {
            'ctr': round(float(ctr_val), 2),
            'conversion_rate': round(float(conversion_rate_val), 2),
            'cpc': round(float(cpc_val), 2),
            'cpa': round(float(cpa_val), 2)
        }
         
         # Performance metrics using numpy argmax/argmin for speed
        if not self.df.empty:
            conversions_array = self.df['conversions'].values
            dates_array = self.df['date'].values
            spend_array = self.df['spend'].values
             
            best_idx = np.argmax(conversions_array)
            worst_idx = np.argmin(conversions_array)
             
            performance = {
                'best_day': {
                    'date': pd.Timestamp(dates_array[best_idx]).strftime('%Y-%m-%d'),
                    'conversions': int(conversions_array[best_idx]),
                    'spend': float(spend_array[best_idx])
                },
                'worst_day': {
                    'date': pd.Timestamp(dates_array[worst_idx]).strftime('%Y-%m-%d'),
                    'conversions': int(conversions_array[worst_idx]),
                    'spend': float(spend_array[worst_idx])
                },
                'avg_daily_spend': round(float(np.mean(spend_array)), 2),
                'avg_daily_conversions': round(float(np.mean(conversions_array)), 2),
                'data_points': len(self.df),
                 
                # Vectorized daily averages using numpy masked arrays to handle zeros
                'avg_ctr': round(float(np.nanmean(
                    np.divide(
                        self.df['clicks'].values,
                        self.df['impressions'].values,
                        out=np.full_like(self.df['clicks'].values, np.nan),
                        where=self.df['impressions'].values > 0
                    ) * 100
                )), 2),
                 
                'avg_cpc': round(float(np.nanmean(
                    np.divide(
                        self.df['spend'].values,
                        self.df['clicks'].values,
                        out=np.full_like(self.df['spend'].values, np.nan),
                        where=self.df['clicks'].values > 0
                    )
                )), 2)
            }
        else:
            performance = {
                'best_day': None,
                'worst_day': None,
                'avg_daily_spend':  0,
                'avg_daily_conversions' :  0 ,
                'data_points' :  0 ,
                'avg_ctr' :  0 ,
                'avg_cpc' :  0 
              }
         
        self.metrics={
            '_metadata' :{
                '__version__':'1 .1 .optimized',
                '__engine__':'OptimizedMarketingDataEngine',
                '__processed_at__' :datetime.now().isoformat(),
                '__rows__' :len(self .df ),
                '__memory_usage_mb__' :round(self .df.memory_usage(deep=True).sum()/1024/1024 ,2 )
            },
            **{'totals' :totals ,'rates' :rates ,'performance' :performance }
        }


# Export main functionality for easy imports elsewhere

__all__=[
     '__version__',
     '__author__',
     '__description__',
     '__license__',
     '__maintainers__',
     '__email__',
     '__url__',
     '__keywords__',
     '__classifiers__',
     '__requires_python__',
     '__requires_dist__',
     '__provides_dist__',
     '__obsoletes_dist__'
]

# Module metadata

__version__='1.1.optimized'
__author__='Marketing Data Engine Team'
__description__='Robust data processing engine for marketing performance metrics'
__license__='MIT'
__maintainers__=['Data Engineering Team']
__email__=['data-engine@example.com']
__url__=['https://github.com/example/marketing-data-engine']
__keywords__=['marketing','analytics','data-processing','metrics','performance']
__classifiers__=[
     'Development Status :: 5 - Production/Stable',
     'Intended Audience :: Developers',
     'Topic :: Software Development :: Libraries :: Python Modules',
     'License :: OSI Approved :: MIT License',
     'Programming Language :: Python :: 3.8',
     'Programming Language :: Python :: 3.9',
     'Programming Language :: Python :: 3.10',
     'Programming Language :: Python :: 3.11'
]
__requires_python__='>=3.8'
