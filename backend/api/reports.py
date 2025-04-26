"""
API endpoints for financial reports.
"""
from flask import jsonify, request
from . import api_bp
from ..database import db
from ..models.financial_data import FinancialReport

@api_bp.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint to verify the API is running."""
    return jsonify({
        'status': 'success',
        'message': 'API is running'
    })

@api_bp.route('/reports', methods=['GET'])
def get_reports():
    """
    Get a list of all available financial reports.
    
    Returns:
        JSON response with a list of report metadata.
    """
    session = db.get_session()
    try:
        reports = session.query(FinancialReport).order_by(FinancialReport.year).all()
        return jsonify({
            'status': 'success',
            'data': [
                {
                    'id': report.id,
                    'year': report.year,
                    'title': report.title,
                    'file_path': report.file_path
                } for report in reports
            ]
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500
    finally:
        db.close_session(session)

@api_bp.route('/reports/<int:report_id>', methods=['GET'])
def get_report(report_id):
    """
    Get detailed information about a specific financial report.
    
    Args:
        report_id: ID of the report
        
    Returns:
        JSON response with report details and associated metrics.
    """
    session = db.get_session()
    try:
        report = session.query(FinancialReport).filter(FinancialReport.id == report_id).first()
        
        if not report:
            return jsonify({
                'status': 'error',
                'message': f'Report with ID {report_id} not found'
            }), 404
            
        # Get associated metrics
        metrics_data = []
        for data_point in report.metrics:
            metrics_data.append({
                'id': data_point.id,
                'metric_name': data_point.metric.name,
                'value': data_point.value,
                'notes': data_point.notes
            })
            
        return jsonify({
            'status': 'success',
            'data': {
                'id': report.id,
                'year': report.year,
                'title': report.title,
                'file_path': report.file_path,
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
