"""
API endpoints for financial metrics.
"""
from flask import jsonify, request
from . import api_bp
from ..database import db
from ..models.financial_data import FinancialMetric, YearlyData

@api_bp.route('/metrics', methods=['GET'])
def get_metrics():
    """
    Get a list of available financial metrics.
    
    Returns:
        JSON response with a list of metrics.
    """
    session = db.get_session()
    try:
        metrics = session.query(FinancialMetric).all()
        return jsonify({
            'status': 'success',
            'data': [
                {
                    'id': metric.id,
                    'name': metric.name,
                    'description': metric.description,
                    'unit': metric.unit,
                    'category': metric.category
                } for metric in metrics
            ]
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500
    finally:
        db.close_session(session)

@api_bp.route('/metrics/<int:metric_id>', methods=['GET'])
def get_metric(metric_id):
    """
    Get detailed information about a specific metric, including yearly data.
    
    Args:
        metric_id: ID of the metric
        
    Returns:
        JSON response with metric details and historical data.
    """
    session = db.get_session()
    try:
        metric = session.query(FinancialMetric).filter(FinancialMetric.id == metric_id).first()
        
        if not metric:
            return jsonify({
                'status': 'error',
                'message': f'Metric with ID {metric_id} not found'
            }), 404
            
        # Get historical data for this metric
        yearly_data = []
        for data_point in metric.data_points:
            yearly_data.append({
                'id': data_point.id,
                'year': data_point.report.year,
                'value': data_point.value,
                'notes': data_point.notes
            })
            
        # Sort by year
        yearly_data.sort(key=lambda x: x['year'])
            
        return jsonify({
            'status': 'success',
            'data': {
                'id': metric.id,
                'name': metric.name,
                'description': metric.description,
                'unit': metric.unit,
                'category': metric.category,
                'yearly_data': yearly_data
            }
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500
    finally:
        db.close_session(session)

@api_bp.route('/metrics/categories', methods=['GET'])
def get_metric_categories():
    """
    Get a list of all metric categories.
    
    Returns:
        JSON response with a list of unique categories.
    """
    session = db.get_session()
    try:
        # Get distinct categories
        categories = session.query(FinancialMetric.category).distinct().all()
        return jsonify({
            'status': 'success',
            'data': [category[0] for category in categories if category[0]]
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500
    finally:
        db.close_session(session) 