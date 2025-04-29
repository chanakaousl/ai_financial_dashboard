from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, Text, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
import datetime

Base = declarative_base()

class FinancialReport(Base):
    """Model representing annual financial reports"""
    __tablename__ = 'financial_reports'
    
    id = Column(Integer, primary_key=True)
    year = Column(Integer, unique=True, nullable=False)
    pdf_path = Column(String(255))
    
    # Relationships
    metrics = relationship("YearlyData", back_populates="report")
    shareholders = relationship("ShareholderData", back_populates="report")
    
    def __repr__(self):
        return f"<FinancialReport(year={self.year})>"


class FinancialMetric(Base):
    """Model representing financial metrics"""
    __tablename__ = 'financial_metrics'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(50), unique=True, nullable=False)
    description = Column(Text)
    unit = Column(String(20), default="LKR")
    category = Column(String(50))
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    
    # Relationships
    yearly_data = relationship("YearlyData", back_populates="metric")
    
    def __repr__(self):
        return f"<FinancialMetric(name={self.name})>"


class YearlyData(Base):
    """Model representing yearly financial metric data"""
    __tablename__ = 'yearly_data'
    
    id = Column(Integer, primary_key=True)
    metric_id = Column(Integer, ForeignKey('financial_metrics.id'), nullable=False)
    report_id = Column(Integer, ForeignKey('financial_reports.id'), nullable=False)
    value = Column(Float, nullable=False)
    
    # Relationships
    metric = relationship("FinancialMetric", back_populates="yearly_data")
    report = relationship("FinancialReport", back_populates="metrics")
    
    def __repr__(self):
        return f"<YearlyData(metric_id={self.metric_id}, report_id={self.report_id}, value={self.value})>"


class ShareholderData(Base):
    """Model representing top shareholders data"""
    __tablename__ = 'shareholders_data'
    
    id = Column(Integer, primary_key=True)
    report_id = Column(Integer, ForeignKey('financial_reports.id'), nullable=False)
    shareholder_name = Column(String(255), nullable=False)
    ownership_percentage = Column(Float, nullable=False)
    shares_count = Column(Integer)
    rank = Column(Integer)
    
    # Relationships
    report = relationship("FinancialReport", back_populates="shareholders")
    
    def __repr__(self):
        return f"<ShareholderData(name={self.shareholder_name}, percentage={self.ownership_percentage})>"
