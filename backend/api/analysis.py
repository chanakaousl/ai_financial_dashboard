"""
API endpoints for financial data analysis.
"""
from flask import jsonify, request
from . import api_bp
from ..database import db
from ..models.financial_data import FinancialMetric, YearlyData, FinancialReport
import numpy as np
from scipy.stats import linregress

@api_bp.route('/analysis/trend/<int:metric_id>', methods=['GET'])
def get_metric_trend(metric_id):
    """
    Analyze the trend for a specific financial metric.
    
    Args:
        metric_id: ID of the metric
        
    Returns:
        JSON response with trend analysis data.
    """
    session = db.get_session()
    try:
        metric = session.query(FinancialMetric).filter(FinancialMetric.id == metric_id).first()
        
        if not metric:
            return jsonify({
                'status': 'error',
                'message': f'Metric with ID {metric_id} not found'
            }), 404
            
        # Get yearly data for this metric
        yearly_data = []
        for data_point in metric.data_points:
            yearly_data.append({
                'year': data_point.report.year,
                'value': data_point.value
            })
            
        # Sort by year
        yearly_data.sort(key=lambda x: x['year'])
        
        # Perform trend analysis
        if len(yearly_data) >= 2:
            years = np.array([item['year'] for item in yearly_data])
            values = np.array([item['value'] for item in yearly_data])
            
            # Linear regression
            slope, intercept, r_value, p_value, std_err = linregress(years, values)
            
            # Calculate growth rate (CAGR)
            if len(yearly_data) > 1 and yearly_data[0]['value'] != 0:
                first_value = yearly_data[0]['value']
                last_value = yearly_data[-1]['value']
                years_diff = yearly_data[-1]['year'] - yearly_data[0]['year']
                cagr = (last_value / first_value) ** (1 / years_diff) - 1 if years_diff > 0 else 0
            else:
                cagr = 0
                
            # Calculate YoY changes
            yoy_changes = []
            for i in range(1, len(yearly_data)):
                prev_value = yearly_data[i-1]['value']
                curr_value = yearly_data[i]['value']
                if prev_value != 0:
                    yoy_change = (curr_value - prev_value) / abs(prev_value)
                else:
                    yoy_change = 0 if curr_value == 0 else float('inf')
                    
                yoy_changes.append({
                    'year': yearly_data[i]['year'],
                    'change': yoy_change
                })
                
            analysis_result = {
                'trend_line': {
                    'slope': slope,
                    'intercept': intercept,
                    'r_squared': r_value ** 2,
                    'p_value': p_value,
                    'std_err': std_err
                },
                'growth': {
                    'cagr': cagr,
                    'total_change': (last_value - first_value) / abs(first_value) if first_value != 0 else 0
                },
                'yoy_changes': yoy_changes
            }
        else:
            analysis_result = {
                'message': 'Insufficient data for trend analysis'
            }
            
        return jsonify({
            'status': 'success',
            'data': {
                'metric': {
                    'id': metric.id,
                    'name': metric.name,
                    'unit': metric.unit,
                    'category': metric.category
                },
                'yearly_data': yearly_data,
                'analysis': analysis_result
            }
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500
    finally:
        db.close_session(session)

@api_bp.route('/analysis/compare', methods=['GET'])
def compare_metrics():
    """
    Compare multiple metrics over time.
    
    Query Parameters:
        metric_ids: Comma-separated list of metric IDs
        
    Returns:
        JSON response with comparative analysis.
    """
    metric_ids = request.args.get('metric_ids', '')
    if not metric_ids:
        return jsonify({
            'status': 'error',
            'message': 'No metric IDs provided'
        }), 400
        
    try:
        metric_id_list = [int(id) for id in metric_ids.split(',')]
    except ValueError:
        return jsonify({
            'status': 'error',
            'message': 'Invalid metric ID format'
        }), 400
        
    session = db.get_session()
    try:
        metrics_data = []
        
        # Get data for each metric
        for metric_id in metric_id_list:
            metric = session.query(FinancialMetric).filter(FinancialMetric.id == metric_id).first()
            
            if not metric:
                continue
                
            yearly_data = []
            for data_point in metric.data_points:
                yearly_data.append({
                    'year': data_point.report.year,
                    'value': data_point.value
                })
                
            # Sort by year
            yearly_data.sort(key=lambda x: x['year'])
            
            metrics_data.append({
                'metric': {
                    'id': metric.id,
                    'name': metric.name,
                    'unit': metric.unit,
                    'category': metric.category
                },
                'yearly_data': yearly_data
            })
            
        # Get a unified list of years
        all_years = set()
        for metric_data in metrics_data:
            all_years.update(item['year'] for item in metric_data['yearly_data'])
        
        all_years = sorted(list(all_years))
        
        return jsonify({
            'status': 'success',
            'data': {
                'years': all_years,
                'metrics': metrics_data
            }
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500
    finally:
        db.close_session(session) 