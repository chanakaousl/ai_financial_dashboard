"""
API endpoints for financial data analysis.
"""
from flask import jsonify, request, make_response
from api import api_bp
from database import db
from models.financial_data import FinancialMetric, YearlyData, FinancialReport
import numpy as np
from scipy.stats import linregress
import io
import csv

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

            # Basic Anomaly Detection based on YoY changes
            if len(yoy_changes) > 1:
                yoy_values = [change['change'] for change in yoy_changes if change['change'] != float('inf')]
                if yoy_values:
                    mean_yoy = np.mean(yoy_values)
                    std_dev_yoy = np.std(yoy_values)
                    threshold = 2 * std_dev_yoy # Example threshold: 2 standard deviations

                    anomalies = []
                    for change in yoy_changes:
                        if change['change'] != float('inf') and abs(change['change'] - mean_yoy) > threshold:
                            anomalies.append({
                                'year': change['year'],
                                'value': next((item['value'] for item in yearly_data if item['year'] == change['year']), None),
                                'yoy_change': change['change'],
                                'deviation': abs(change['change'] - mean_yoy),
                                'message': f"Significant YoY change detected (deviation: {abs(change['change'] - mean_yoy):.2f}, threshold: {threshold:.2f})"
                            })
                    analysis_result['anomalies'] = anomalies
                else:
                     analysis_result['anomalies'] = []
            else:
                 analysis_result['anomalies'] = []

        else:
            analysis_result = {
                'message': 'Insufficient data for trend analysis',
                'trend_line': None,
                'growth': None,
                'yoy_changes': [],
                'anomalies': []
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


@api_bp.route('/export/metric/<int:metric_id>/csv', methods=['GET'])
def export_metric_csv(metric_id):
    """
    Export yearly data for a specific metric as a CSV file.

    Args:
        metric_id: ID of the metric

    Returns:
        CSV file response.
    """
    session = db.get_session()
    try:
        metric = session.query(FinancialMetric).filter(FinancialMetric.id == metric_id).first()

        if not metric:
            return jsonify({
                'status': 'error',
                'message': f'Metric with ID {metric_id} not found'
            }), 404

        # Get yearly data
        yearly_data = []
        for data_point in metric.data_points:
            yearly_data.append({
                'year': data_point.report.year,
                'value': data_point.value,
                'notes': data_point.notes
            })
        yearly_data.sort(key=lambda x: x['year'])

        # Create CSV
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(['Year', 'Value', 'Notes', 'Metric Name', 'Metric Unit']) # Header
        for item in yearly_data:
            writer.writerow([
                item['year'],
                item['value'],
                item['notes'],
                metric.name,
                metric.unit
            ])

        output.seek(0)
        response = make_response(output.getvalue())
        response.headers['Content-Disposition'] = f'attachment; filename=metric_{metric.name.replace(" ", "_")}_{metric_id}.csv'
        response.headers['Content-Type'] = 'text/csv'
        return response

    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500
    finally:
        db.close_session(session)


@api_bp.route('/export/compare/csv', methods=['GET'])
def export_compare_csv():
    """
    Export comparison data for multiple metrics as a CSV file.

    Query Parameters:
        metric_ids: Comma-separated list of metric IDs

    Returns:
        CSV file response.
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
        metrics_data = {}
        metric_details = {}
        all_years = set()

        # Fetch data for each metric
        for metric_id in metric_id_list:
            metric = session.query(FinancialMetric).filter(FinancialMetric.id == metric_id).first()
            if not metric:
                continue

            metric_details[metric_id] = {'name': metric.name, 'unit': metric.unit}
            metric_year_data = {}
            for data_point in metric.data_points:
                year = data_point.report.year
                metric_year_data[year] = data_point.value
                all_years.add(year)
            metrics_data[metric_id] = metric_year_data

        if not metrics_data:
             return jsonify({
                'status': 'error',
                'message': 'No valid metrics found for the provided IDs'
            }), 404

        sorted_years = sorted(list(all_years))

        # Create CSV
        output = io.StringIO()
        writer = csv.writer(output)

        # Header row: Year, Metric1 Name (Unit), Metric2 Name (Unit), ...
        header = ['Year'] + [f"{metric_details[mid]['name']} ({metric_details[mid]['unit']})" for mid in metric_id_list if mid in metric_details]
        writer.writerow(header)

        # Data rows
        for year in sorted_years:
            row = [year]
            for mid in metric_id_list:
                 if mid in metrics_data:
                    row.append(metrics_data[mid].get(year, '')) # Use empty string if no data for that year
            writer.writerow(row)

        output.seek(0)
        response = make_response(output.getvalue())
        filename_ids = "_".join(map(str, metric_id_list))
        response.headers['Content-Disposition'] = f'attachment; filename=compare_metrics_{filename_ids}.csv'
        response.headers['Content-Type'] = 'text/csv'
        return response

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
