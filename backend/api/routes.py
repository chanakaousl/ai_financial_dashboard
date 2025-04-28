from flask import jsonify, request
from database import db
from models.financial_data import FinancialMetric, YearlyData, FinancialReport, ShareholderData
from sqlalchemy import desc
from . import api_bp

@api_bp.route('/health', methods=['GET'])
def health_check():
    """API health check endpoint"""
    return jsonify({"status": "success", "message": "API is running"})

@api_bp.route('/metrics', methods=['GET'])
def get_all_metrics():
    """Get all financial metrics"""
    session = db.get_session()
    try:
        metrics = session.query(FinancialMetric).all()
        result = []
        
        for metric in metrics:
            result.append({
                "id": metric.id,
                "name": metric.name,
                "display_name": metric.display_name,
                "description": metric.description,
                "unit": metric.unit,
                "category": metric.category,
                "visualization_type": metric.visualization_type
            })
        
        return jsonify({"status": "success", "data": result})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500
    finally:
        db.close_session(session)

@api_bp.route('/metrics/<int:metric_id>', methods=['GET'])
def get_metric_by_id(metric_id):
    """Get a specific financial metric with its yearly data"""
    session = db.get_session()
    try:
        metric = session.query(FinancialMetric).filter_by(id=metric_id).first()
        
        if not metric:
            return jsonify({"status": "error", "message": "Metric not found"}), 404
        
        # Get yearly data for this metric, ordered by year
        yearly_data_query = session.query(YearlyData, FinancialReport.year)\
            .join(FinancialReport)\
            .filter(YearlyData.metric_id == metric_id)\
            .order_by(FinancialReport.year)
            
        yearly_data = []
        for data, year in yearly_data_query:
            yearly_data.append({
                "year": year,
                "value": data.value
            })
        
        result = {
            "id": metric.id,
            "name": metric.name,
            "display_name": metric.display_name,
            "description": metric.description,
            "unit": metric.unit,
            "category": metric.category,
            "visualization_type": metric.visualization_type,
            "annotations": metric.annotations,
            "yearly_data": yearly_data
        }
        
        return jsonify({"status": "success", "data": result})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500
    finally:
        db.close_session(session)

@api_bp.route('/reports', methods=['GET'])
def get_all_reports():
    """Get all financial reports"""
    session = db.get_session()
    try:
        reports = session.query(FinancialReport).order_by(desc(FinancialReport.year)).all()
        result = []
        
        for report in reports:
            result.append({
                "id": report.id,
                "year": report.year,
                "pdf_path": report.pdf_path
            })
        
        return jsonify({"status": "success", "data": result})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500
    finally:
        db.close_session(session)

@api_bp.route('/reports/<int:report_id>', methods=['GET'])
def get_report_by_id(report_id):
    """Get a specific financial report with metrics data"""
    session = db.get_session()
    try:
        report = session.query(FinancialReport).filter_by(id=report_id).first()
        
        if not report:
            return jsonify({"status": "error", "message": "Report not found"}), 404
        
        # Get metrics data for this report
        metrics_data = []
        for data in report.metrics:
            metric = data.metric
            metrics_data.append({
                "id": metric.id,
                "name": metric.name,
                "display_name": metric.display_name,
                "value": data.value,
                "unit": metric.unit
            })
        
        result = {
            "id": report.id,
            "year": report.year,
            "pdf_path": report.pdf_path,
            "metrics": metrics_data
        }
        
        return jsonify({"status": "success", "data": result})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500
    finally:
        db.close_session(session)

@api_bp.route('/shareholders', methods=['GET'])
def get_shareholders():
    """Get top shareholders data for all years or a specific year"""
    session = db.get_session()
    try:
        year = request.args.get('year')
        limit = request.args.get('limit', default=20, type=int)
        
        query = session.query(ShareholderData, FinancialReport.year).\
            join(FinancialReport)
        
        if year:
            query = query.filter(FinancialReport.year == year)
        
        query = query.order_by(FinancialReport.year.desc(), ShareholderData.rank)
        
        shareholder_data = []
        for data, year in query:
            shareholder_data.append({
                "id": data.id,
                "year": year,
                "rank": data.rank,
                "name": data.shareholder_name,
                "percentage": data.ownership_percentage,
                "shares": data.shares_count
            })
        
        # Group by year
        years = {}
        for data in shareholder_data:
            year = data["year"]
            if year not in years:
                years[year] = []
            years[year].append(data)
        
        result = {
            "years": years
        }
        
        return jsonify({"status": "success", "data": result})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500
    finally:
        db.close_session(session) 