"""
Financial AI Insights Module
Provides intelligent analysis and predictions for spending patterns
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import json
import statistics
from collections import defaultdict, Counter

try:
    from sklearn.linear_model import LinearRegression
    from sklearn.ensemble import RandomForestRegressor
    from sklearn.preprocessing import StandardScaler
    import joblib
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False

class FinancialAI:
    def __init__(self):
        self.spending_model = None
        self.budget_model = None
        self.scaler = StandardScaler() if SKLEARN_AVAILABLE else None
        self.insights_cache = {}
        self.model_file = "financial_ai_model.pkl"
        
    def analyze_spending_patterns(self, expenses):
        """
        Comprehensive AI analysis of spending patterns
        Returns detailed insights dictionary
        """
        if not expenses:
            return {
                'status': 'insufficient_data',
                'message': 'Need at least some expenses for analysis'
            }
        
        try:
            # Convert to DataFrame for easier analysis
            df = self._prepare_dataframe(expenses)
            
            if df.empty:
                return {'status': 'no_valid_data'}
            
            # Core insights
            insights = {
                'status': 'success',
                'analysis_date': datetime.now().isoformat(),
                'data_period': self._get_data_period(df),
                'spending_summary': self._calculate_spending_summary(df),
                'spending_trends': self._analyze_spending_trends(df),
                'category_insights': self._analyze_categories(df),
                'behavioral_patterns': self._analyze_behavioral_patterns(df),
                'anomalies': self._detect_spending_anomalies(df),
                'predictions': self._generate_predictions(df),
                'recommendations': self._generate_ai_recommendations(df),
                'financial_health': self._assess_financial_health(df),
                'goals_tracking': self._track_financial_goals(df)
            }
            
            # Cache insights for performance
            self.insights_cache = insights
            
            return insights
            
        except Exception as e:
            return {
                'status': 'error',
                'message': f'Analysis failed: {str(e)}'
            }
    
    def _prepare_dataframe(self, expenses):
        """Convert expenses to pandas DataFrame with enriched features"""
        if not expenses:
            return pd.DataFrame()
        
        df = pd.DataFrame(expenses)
        
        # Ensure required columns exist
        required_columns = ['date', 'amount', 'category', 'description']
        for col in required_columns:
            if col not in df.columns:
                df[col] = '' if col in ['category', 'description'] else 0
        
        # Convert date column
        df['date'] = pd.to_datetime(df['date'], errors='coerce')
        df = df.dropna(subset=['date'])  # Remove invalid dates
        
        # Convert amount to numeric
        df['amount'] = pd.to_numeric(df['amount'], errors='coerce')
        df = df[df['amount'] > 0]  # Remove invalid amounts
        
        if df.empty:
            return df
        
        # Add time-based features
        df['year'] = df['date'].dt.year
        df['month'] = df['date'].dt.month
        df['day'] = df['date'].dt.day
        df['day_of_week'] = df['date'].dt.day_name()
        df['week_of_year'] = df['date'].dt.isocalendar().week
        df['is_weekend'] = df['date'].dt.weekday >= 5
        df['day_of_month'] = df['date'].dt.day
        
        # Add derived features
        df['amount_log'] = np.log1p(df['amount'])  # Log transform for skewed data
        df['description_length'] = df['description'].str.len().fillna(0)
        
        # Sort by date
        df = df.sort_values('date')
        
        return df
    
    def _get_data_period(self, df):
        """Get the time period covered by the data"""
        if df.empty:
            return {}
        
        start_date = df['date'].min()
        end_date = df['date'].max()
        total_days = (end_date - start_date).days + 1
        
        return {
            'start_date': start_date.strftime('%Y-%m-%d'),
            'end_date': end_date.strftime('%Y-%m-%d'),
            'total_days': total_days,
            'total_transactions': len(df)
        }
    
    def _calculate_spending_summary(self, df):
        """Calculate comprehensive spending summary"""
        if df.empty:
            return {}
        
        total_amount = df['amount'].sum()
        daily_amounts = df.groupby(df['date'].dt.date)['amount'].sum()
        
        summary = {
            'total_spending': float(total_amount),
            'average_daily': float(daily_amounts.mean()),
            'median_daily': float(daily_amounts.median()),
            'max_daily': float(daily_amounts.max()),
            'min_daily': float(daily_amounts.min()),
            'std_daily': float(daily_amounts.std()),
            'average_transaction': float(df['amount'].mean()),
            'median_transaction': float(df['amount'].median()),
            'largest_transaction': float(df['amount'].max()),
            'smallest_transaction': float(df['amount'].min()),
            'total_transactions': len(df),
            'spending_days': len(daily_amounts),
            'zero_spending_days': len(daily_amounts[daily_amounts == 0]) if 0 in daily_amounts.values else 0
        }
        
        return summary
    
    def _analyze_spending_trends(self, df):
        """Analyze spending trends over time"""
        if df.empty or len(df) < 7:
            return {'status': 'insufficient_data'}
        
        # Daily spending trend
        daily_spending = df.groupby(df['date'].dt.date)['amount'].sum().reset_index()
        daily_spending['days_since_start'] = range(len(daily_spending))
        
        trends = {}
        
        # Calculate trend using linear regression if available
        if SKLEARN_AVAILABLE and len(daily_spending) >= 3:
            try:
                X = daily_spending[['days_since_start']]
                y = daily_spending['amount']
                
                lr_model = LinearRegression()
                lr_model.fit(X, y)
                
                slope = lr_model.coef_[0]
                r_squared = lr_model.score(X, y)
                
                # Classify trend
                if slope > 10:
                    trend_direction = "increasing"
                elif slope < -10:
                    trend_direction = "decreasing"
                else:
                    trend_direction = "stable"
                
                trends['overall_trend'] = {
                    'direction': trend_direction,
                    'slope': float(slope),
                    'strength': float(r_squared),
                    'daily_change': float(slope)
                }
            except Exception:
                trends['overall_trend'] = {'direction': 'unknown', 'slope': 0}
        
        # Weekly patterns
        weekly_avg = df.groupby('day_of_week')['amount'].mean().to_dict()
        peak_day = max(weekly_avg, key=weekly_avg.get)
        low_day = min(weekly_avg, key=weekly_avg.get)
        
        trends['weekly_patterns'] = {
            'average_by_day': weekly_avg,
            'peak_spending_day': peak_day,
            'lowest_spending_day': low_day,
            'weekend_vs_weekday': {
                'weekend_avg': float(df[df['is_weekend']]['amount'].mean()) if len(df[df['is_weekend']]) > 0 else 0,
                'weekday_avg': float(df[~df['is_weekend']]['amount'].mean()) if len(df[~df['is_weekend']]) > 0 else 0
            }
        }
        
        # Monthly patterns
        if df['date'].dt.month.nunique() > 1:
            monthly_totals = df.groupby(df['date'].dt.to_period('M'))['amount'].sum()
            trends['monthly_patterns'] = {
                'average_monthly': float(monthly_totals.mean()),
                'growth_rate': self._calculate_growth_rate(monthly_totals),
                'seasonal_variation': float(monthly_totals.std() / monthly_totals.mean()) if monthly_totals.mean() > 0 else 0
            }
        
        return trends
    
    def _analyze_categories(self, df):
        """Analyze spending by category"""
        if df.empty:
            return {}
        
        category_analysis = {}
        
        # Basic category statistics
        category_totals = df.groupby('category')['amount'].agg(['sum', 'mean', 'count', 'std']).fillna(0)
        category_percentages = (category_totals['sum'] / category_totals['sum'].sum() * 100).round(2)
        
        for category in category_totals.index:
            category_analysis[category] = {
                'total_spent': float(category_totals.loc[category, 'sum']),
                'average_transaction': float(category_totals.loc[category, 'mean']),
                'transaction_count': int(category_totals.loc[category, 'count']),
                'percentage_of_total': float(category_percentages.loc[category]),
                'consistency': float(1 / (1 + category_totals.loc[category, 'std'])) if category_totals.loc[category, 'std'] > 0 else 1.0
            }
        
        # Top categories
        top_categories = category_totals.nlargest(3, 'sum')
        
        # Category trends
        category_trends = {}
        for category in df['category'].unique():
            cat_data = df[df['category'] == category]
            if len(cat_data) >= 3:
                daily_cat = cat_data.groupby(cat_data['date'].dt.date)['amount'].sum()
                if len(daily_cat) >= 3:
                    trend = self._calculate_simple_trend(daily_cat.values)
                    category_trends[category] = trend
        
        return {
            'detailed_analysis': category_analysis,
            'top_categories': {cat: float(amount) for cat, amount in zip(top_categories.index, top_categories['sum'])},
            'category_trends': category_trends,
            'diversity_score': len(df['category'].unique()) / len(df) * 100  # How diverse spending is
        }
    
    def _analyze_behavioral_patterns(self, df):
        """Analyze behavioral spending patterns"""
        if df.empty:
            return {}
        
        patterns = {}
        
        # Transaction timing patterns
        if 'timestamp' in df.columns or len(df) > 0:
            # Day of month patterns
            daily_spending = df.groupby('day_of_month')['amount'].mean()
            patterns['monthly_cycle'] = {
                'early_month_avg': float(daily_spending.iloc[:10].mean()) if len(daily_spending) >= 10 else 0,
                'mid_month_avg': float(daily_spending.iloc[10:20].mean()) if len(daily_spending) >= 20 else 0,
                'late_month_avg': float(daily_spending.iloc[20:].mean()) if len(daily_spending) >= 20 else 0,
                'payday_effect': self._detect_payday_pattern(df)
            }
        
        # Spending burst detection
        daily_totals = df.groupby(df['date'].dt.date)['amount'].sum()
        high_spending_threshold = daily_totals.quantile(0.8)
        high_spending_days = daily_totals[daily_totals > high_spending_threshold]
        
        patterns['spending_bursts'] = {
            'high_spending_days_count': len(high_spending_days),
            'average_burst_amount': float(high_spending_days.mean()) if len(high_spending_days) > 0 else 0,
            'burst_frequency': len(high_spending_days) / len(daily_totals) * 100 if len(daily_totals) > 0 else 0
        }
        
        # Consistency patterns
        daily_amounts = df.groupby(df['date'].dt.date)['amount'].sum()
        patterns['spending_consistency'] = {
            'coefficient_of_variation': float(daily_amounts.std() / daily_amounts.mean()) if daily_amounts.mean() > 0 else 0,
            'regular_spender_score': self._calculate_regularity_score(daily_amounts)
        }
        
        return patterns
    
    def _detect_spending_anomalies(self, df):
        """Detect unusual spending patterns and outliers"""
        if df.empty or len(df) < 5:
            return {'status': 'insufficient_data'}
        
        anomalies = {}
        
        # Transaction-level anomalies
        transaction_amounts = df['amount']
        Q1 = transaction_amounts.quantile(0.25)
        Q3 = transaction_amounts.quantile(0.75)
        IQR = Q3 - Q1
        
        # Outlier detection using IQR method
        outlier_threshold_high = Q3 + 1.5 * IQR
        outlier_threshold_low = Q1 - 1.5 * IQR
        
        high_outliers = df[df['amount'] > outlier_threshold_high]
        low_outliers = df[df['amount'] < outlier_threshold_low]
        
        anomalies['transaction_outliers'] = {
            'high_value_transactions': len(high_outliers),
            'unusual_high_amounts': high_outliers[['date', 'amount', 'category', 'description']].to_dict('records') if len(high_outliers) <= 5 else [],
            'threshold_high': float(outlier_threshold_high),
            'largest_transaction': {
                'amount': float(df.loc[df['amount'].idxmax(), 'amount']),
                'date': df.loc[df['amount'].idxmax(), 'date'].strftime('%Y-%m-%d'),
                'category': df.loc[df['amount'].idxmax(), 'category'],
                'description': df.loc[df['amount'].idxmax(), 'description']
            }
        }
        
        # Daily spending anomalies
        daily_spending = df.groupby(df['date'].dt.date)['amount'].sum()
        daily_mean = daily_spending.mean()
        daily_std = daily_spending.std()
        
        if daily_std > 0:
            unusual_days = daily_spending[abs(daily_spending - daily_mean) > 2 * daily_std]
            anomalies['unusual_spending_days'] = {
                'count': len(unusual_days),
                'dates_and_amounts': {str(date): float(amount) for date, amount in unusual_days.items()}
            }
        
        # Category anomalies
        category_stats = df.groupby('category')['amount'].agg(['mean', 'std'])
        category_anomalies = []
        
        for _, row in df.iterrows():
            category = row['category']
            amount = row['amount']
            
            if category in category_stats.index:
                cat_mean = category_stats.loc[category, 'mean']
                cat_std = category_stats.loc[category, 'std']
                
                if cat_std > 0 and abs(amount - cat_mean) > 2 * cat_std:
                    category_anomalies.append({
                        'date': row['date'].strftime('%Y-%m-%d'),
                        'category': category,
                        'amount': float(amount),
                        'expected_range': f"{cat_mean - cat_std:.0f} - {cat_mean + cat_std:.0f}"
                    })
        
        anomalies['category_anomalies'] = category_anomalies[:5]  # Limit to 5 most recent
        
        return anomalies
    
    def _generate_predictions(self, df):
        """Generate spending predictions using AI models"""
        if df.empty or len(df) < 7:
            return {'status': 'insufficient_data'}
        
        predictions = {}
        
        try:
            # Prepare data for prediction
            daily_spending = df.groupby(df['date'].dt.date)['amount'].sum().reset_index()
            daily_spending = daily_spending.sort_values('date')
            
            # Simple trend-based prediction
            recent_avg = daily_spending['amount'].tail(7).mean()  # Last 7 days average
            overall_avg = daily_spending['amount'].mean()
            
            # Next day prediction
            predictions['next_day'] = {
                'predicted_amount': float((recent_avg + overall_avg) / 2),
                'confidence': 'medium',
                'method': 'trend_average'
            }
            
            # Next week prediction
            weekly_pattern = df.groupby('day_of_week')['amount'].mean()
            next_week_dates = pd.date_range(start=df['date'].max() + timedelta(days=1), periods=7)
            weekly_prediction = []
            
            for date in next_week_dates:
                day_name = date.strftime('%A')
                predicted_amount = weekly_pattern.get(day_name, overall_avg)
                weekly_prediction.append({
                    'date': date.strftime('%Y-%m-%d'),
                    'predicted_amount': float(predicted_amount)
                })
            
            predictions['next_week'] = weekly_prediction
            
            # Monthly prediction
            if df['date'].dt.month.nunique() > 1:
                monthly_avg = df.groupby(df['date'].dt.to_period('M'))['amount'].sum().mean()
                predictions['next_month'] = {
                    'predicted_total': float(monthly_avg),
                    'confidence': 'medium'
                }
            
            # Advanced ML predictions if available
            if SKLEARN_AVAILABLE and len(daily_spending) >= 30:
                predictions.update(self._ml_predictions(daily_spending))
            
        except Exception as e:
            predictions['error'] = str(e)
        
        return predictions
    
    def _generate_ai_recommendations(self, df):
        """Generate personalized AI recommendations"""
        if df.empty:
            return []
        
        recommendations = []
        
        # Analyze spending patterns for recommendations
        daily_avg = df.groupby(df['date'].dt.date)['amount'].sum().mean()
        category_analysis = df.groupby('category')['amount'].sum().sort_values(ascending=False)
        top_category = category_analysis.index[0] if len(category_analysis) > 0 else "Unknown"
        top_category_amount = category_analysis.iloc[0] if len(category_analysis) > 0 else 0
        
        # High spending warning
        recent_week = df[df['date'] >= df['date'].max() - timedelta(days=7)]
        recent_avg = recent_week.groupby(recent_week['date'].dt.date)['amount'].sum().mean()
        
        if recent_avg > daily_avg * 1.2:
            recommendations.append({
                'type': 'warning',
                'priority': 'high',
                'title': '📈 Spending Increase Detected',
                'message': f'Your spending has increased by {((recent_avg/daily_avg - 1) * 100):.0f}% this week.',
                'action': 'Review recent transactions and consider setting daily limits',
                'potential_savings': float(recent_avg - daily_avg) * 7
            })
        
        # Category-specific recommendations
        if top_category_amount > 0:
            total_spending = df['amount'].sum()
            category_percentage = (top_category_amount / total_spending) * 100
            
            if category_percentage > 40:
                recommendations.append({
                    'type': 'info',
                    'priority': 'medium',
                    'title': f'🎯 {top_category} Dominates Spending',
                    'message': f'{top_category} accounts for {category_percentage:.0f}% of your expenses.',
                    'action': f'Consider budgeting specifically for {top_category} expenses',
                    'insight': 'focus_area'
                })
        
        # Weekend vs weekday analysis
        weekend_avg = df[df['is_weekend']]['amount'].mean() if len(df[df['is_weekend']]) > 0 else 0
        weekday_avg = df[~df['is_weekend']]['amount'].mean() if len(df[~df['is_weekend']]) > 0 else 0
        
        if weekend_avg > weekday_avg * 1.5:
            recommendations.append({
                'type': 'tip',
                'priority': 'low',
                'title': '🍻 Weekend Spending Pattern',
                'message': f'You spend {((weekend_avg/weekday_avg - 1) * 100):.0f}% more on weekends.',
                'action': 'Plan weekend activities within budget',
                'potential_savings': float((weekend_avg - weekday_avg) * 8)  # 8 weekend days per month
            })
        
        # Frequency recommendations
        transaction_frequency = len(df) / len(df['date'].dt.date.unique())
        if transaction_frequency > 5:  # More than 5 transactions per day on average
            recommendations.append({
                'type': 'tip',
                'priority': 'low',
                'title': '💳 High Transaction Frequency',
                'message': f'You average {transaction_frequency:.1f} transactions per day.',
                'action': 'Consider consolidating purchases to reduce impulse spending',
                'insight': 'behavioral_pattern'
            })
        
        # Savings opportunity
        if len(recommendations) == 0:
            recommendations.append({
                'type': 'success',
                'priority': 'low',
                'title': '✅ Good Spending Habits',
                'message': 'Your spending patterns look healthy and consistent.',
                'action': 'Consider setting up automated savings for surplus funds',
                'insight': 'positive_feedback'
            })
        
        return recommendations
    
    def _assess_financial_health(self, df):
        """Assess overall financial health based on spending patterns"""
        if df.empty:
            return {'score': 0, 'status': 'insufficient_data'}
        
        health_score = 100  # Start with perfect score
        factors = {}
        
        # Consistency factor (30 points)
        daily_amounts = df.groupby(df['date'].dt.date)['amount'].sum()
        cv = daily_amounts.std() / daily_amounts.mean() if daily_amounts.mean() > 0 else 0
        consistency_score = max(0, 30 - (cv * 10))
        health_score -= (30 - consistency_score)
        factors['spending_consistency'] = consistency_score / 30
        
        # Diversification factor (20 points)
        category_diversity = len(df['category'].unique())
        diversity_score = min(20, category_diversity * 3)
        health_score -= (20 - diversity_score)
        factors['category_diversification'] = diversity_score / 20
        
        # Trend factor (25 points)
        if len(daily_amounts) >= 7:
            recent_trend = self._calculate_simple_trend(daily_amounts.tail(7).values)
            if recent_trend > 0.1:  # Increasing trend
                trend_penalty = 15
            elif recent_trend < -0.1:  # Decreasing trend (good)
                trend_penalty = 0
            else:  # Stable
                trend_penalty = 5
            health_score -= trend_penalty
            factors['spending_trend'] = (25 - trend_penalty) / 25
        
        # Outlier factor (25 points)
        Q1 = df['amount'].quantile(0.25)
        Q3 = df['amount'].quantile(0.75)
        IQR = Q3 - Q1
        outliers = df[(df['amount'] < Q1 - 1.5 * IQR) | (df['amount'] > Q3 + 1.5 * IQR)]
        outlier_percentage = len(outliers) / len(df) * 100
        outlier_penalty = min(25, outlier_percentage * 2.5)
        health_score -= outlier_penalty
        factors['spending_discipline'] = (25 - outlier_penalty) / 25
        
        # Determine health status
        if health_score >= 85:
            status = 'excellent'
        elif health_score >= 70:
            status = 'good'
        elif health_score >= 55:
            status = 'fair'
        else:
            status = 'needs_improvement'
        
        return {
            'overall_score': max(0, min(100, health_score)),
            'status': status,
            'contributing_factors': factors,
            'recommendations': self._health_recommendations(health_score, factors)
        }
    
    def _track_financial_goals(self, df):
        """Track progress towards financial goals"""
        # This is a placeholder for goal tracking functionality
        # In a real implementation, this would compare against user-set goals
        
        if df.empty:
            return {}
        
        monthly_spending = df.groupby(df['date'].dt.to_period('M'))['amount'].sum()
        current_month_spending = monthly_spending.iloc[-1] if len(monthly_spending) > 0 else 0
        
        # Simulated goals (in a real app, these would be user-defined)
        simulated_goals = {
            'monthly_budget': 50000,
            'savings_target': 10000,
            'category_limits': {
                '🍕 Food': 15000,
                '🚗 Transportation': 8000,
                '🎬 Entertainment': 5000
            }
        }
        
        goal_progress = {}
        
        # Monthly budget progress
        budget_usage = (current_month_spending / simulated_goals['monthly_budget']) * 100
        goal_progress['monthly_budget'] = {
            'target': simulated_goals['monthly_budget'],
            'current': float(current_month_spending),
            'percentage_used': float(budget_usage),
            'status': 'on_track' if budget_usage <= 80 else 'over_budget'
        }
        
        # Category-wise progress
        current_month_data = df[df['date'].dt.to_period('M') == df['date'].dt.to_period('M').iloc[-1]]
        category_spending = current_month_data.groupby('category')['amount'].sum()
        
        category_progress = {}
        for category, limit in simulated_goals['category_limits'].items():
            spent = category_spending.get(category, 0)
            usage_percentage = (spent / limit) * 100
            category_progress[category] = {
                'limit': limit,
                'spent': float(spent),
                'percentage_used': float(usage_percentage),
                'remaining': float(limit - spent),
                'status': 'within_limit' if usage_percentage <= 100 else 'exceeded'
            }
        
        goal_progress['category_limits'] = category_progress
        
        return goal_progress
    
    # Helper methods
    def _calculate_growth_rate(self, series):
        """Calculate growth rate for a time series"""
        if len(series) < 2:
            return 0
        
        growth_rates = []
        for i in range(1, len(series)):
            if series.iloc[i-1] > 0:
                growth_rate = (series.iloc[i] - series.iloc[i-1]) / series.iloc[i-1]
                growth_rates.append(growth_rate)
        
        return statistics.mean(growth_rates) if growth_rates else 0
    
    def _calculate_simple_trend(self, values):
        """Calculate simple trend direction"""
        if len(values) < 2:
            return 0
        
        # Simple linear trend using first and last values
        return (values[-1] - values[0]) / len(values)
    
    def _detect_payday_pattern(self, df):
        """Detect payday spending patterns"""
        # Look for spending spikes early in the month
        early_month = df[df['day_of_month'] <= 5]['amount'].mean()
        rest_of_month = df[df['day_of_month'] > 5]['amount'].mean()
        
        if early_month > rest_of_month * 1.3:
            return {
                'detected': True,
                'early_month_avg': float(early_month),
                'rest_month_avg': float(rest_of_month),
                'ratio': float(early_month / rest_of_month) if rest_of_month > 0 else 0
            }
        else:
            return {'detected': False}
    
    def _calculate_regularity_score(self, daily_amounts):
        """Calculate how regular/predictable spending is"""
        if len(daily_amounts) < 7:
            return 0
        
        # Count how many days have spending vs no spending
        spending_days = len(daily_amounts[daily_amounts > 0])
        total_days = len(daily_amounts)
        regularity = spending_days / total_days
        
        # Factor in consistency of amounts
        if spending_days > 0:
            spending_amounts = daily_amounts[daily_amounts > 0]
            cv = spending_amounts.std() / spending_amounts.mean() if spending_amounts.mean() > 0 else 0
            consistency = 1 / (1 + cv)
            return (regularity + consistency) / 2
        
        return regularity
    
    def _ml_predictions(self, daily_spending):
        """Advanced ML-based predictions"""
        try:
            # Prepare features
            daily_spending['day_num'] = range(len(daily_spending))
            daily_spending['rolling_avg_7'] = daily_spending['amount'].rolling(window=7, min_periods=1).mean()
            daily_spending['rolling_avg_30'] = daily_spending['amount'].rolling(window=30, min_periods=1).mean()
            
            # Features for model
            features = ['day_num', 'rolling_avg_7', 'rolling_avg_30']
            X = daily_spending[features].fillna(method='ffill').fillna(method='bfill')
            y = daily_spending['amount']
            
            # Train model
            model = RandomForestRegressor(n_estimators=50, random_state=42)
            model.fit(X, y)
            
            # Predict next 7 days
            last_row = X.iloc[-1:].copy()
            predictions = []
            
            for i in range(7):
                # Update features for next day
                next_features = last_row.copy()
                next_features['day_num'] += (i + 1)
                
                # Predict
                pred = model.predict(next_features)[0]
                predictions.append(max(0, pred))  # Ensure non-negative
                
                # Update rolling averages (simplified)
                last_row = next_features
            
            return {
                'ml_predictions': {
                    'next_7_days': [float(p) for p in predictions],
                    'model_confidence': float(model.score(X, y)),
                    'method': 'random_forest'
                }
            }
        except Exception:
            return {}
    
    def _health_recommendations(self, health_score, factors):
        """Generate health-specific recommendations"""
        recommendations = []
        
        if factors.get('spending_consistency', 1) < 0.7:
            recommendations.append("Work on maintaining consistent daily spending habits")
        
        if factors.get('category_diversification', 1) < 0.5:
            recommendations.append("Consider diversifying your spending across different categories")
        
        if factors.get('spending_trend', 1) < 0.6:
            recommendations.append("Monitor your spending trend - it's been increasing lately")
        
        if factors.get('spending_discipline', 1) < 0.7:
            recommendations.append("Try to avoid large, unexpected purchases that disrupt your budget")
        
        if health_score > 85:
            recommendations.append("Great job! Your spending habits are very healthy")
        
        return recommendations

# Test function
def test_financial_ai():
    """Test the Financial AI system"""
    # Create sample data
    sample_expenses = [
        {'date': '2024-01-01', 'amount': 500, 'category': '🍕 Food', 'description': 'Grocery shopping'},
        {'date': '2024-01-02', 'amount': 200, 'category': '🚗 Transportation', 'description': 'Metro card'},
        {'date': '2024-01-03', 'amount': 1500, 'category': '🛒 Shopping', 'description': 'New clothes'},
        {'date': '2024-01-04', 'amount': 300, 'category': '🍕 Food', 'description': 'Restaurant'},
        {'date': '2024-01-05', 'amount': 800, 'category': '🎬 Entertainment', 'description': 'Movie and dinner'},
        {'date': '2024-01-06', 'amount': 450, 'category': '🍕 Food', 'description': 'Groceries'},
        {'date': '2024-01-07', 'amount': 150, 'category': '🚗 Transportation', 'description': 'Taxi'},
    ]
    
    # Test the AI
    ai = FinancialAI()
    insights = ai.analyze_spending_patterns(sample_expenses)
    
    print("Financial AI Test Results:")
    print("=" * 50)
    print(f"Status: {insights.get('status')}")
    print(f"Analysis Date: {insights.get('analysis_date')}")
    print(f"Data Period: {insights.get('data_period')}")
    print(f"Spending Summary: {insights.get('spending_summary')}")
    print(f"Financial Health: {insights.get('financial_health')}")
    print("\nRecommendations:")
    for rec in insights.get('recommendations', []):
        print(f"- {rec.get('title')}: {rec.get('message')}")

if __name__ == "__main__":
    test_financial_ai()
