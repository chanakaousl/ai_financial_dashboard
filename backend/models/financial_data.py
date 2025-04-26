from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
import datetime

Base = declarative_base()

class FinancialReport(Base):
    """Model representing a financial report document."""
    
    __tablename__ = 'financial_reports'
    
    id = Column(Integer, primary_key=True)
    year = Column(Integer, nullable=False, unique=True)
    title = Column(String(255), nullable=False)
    file_path = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
    
    # Relationships
    metrics = relationship("YearlyData", back_populates="report")
    
    def __repr__(self):
        return f"<FinancialReport(year={self.year}, title='{self.title}')>"

class FinancialMetric(Base):
    """Model representing a financial metric type."""
    
    __tablename__ = 'financial_metrics'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False, unique=True)
    description = Column(Text)
    unit = Column(String(50))
    category = Column(String(100))  # e.g., 'revenue', 'expense', 'profit', etc.
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    
    # Relationships
    data_points = relationship("YearlyData", back_populates="metric")
    
    def __repr__(self):
        return f"<FinancialMetric(name='{self.name}', category='{self.category}')>"

class YearlyData(Base):
    """Model representing yearly data for a specific financial metric."""
    
    __tablename__ = 'yearly_data'
    
    id = Column(Integer, primary_key=True)
    report_id = Column(Integer, ForeignKey('financial_reports.id'), nullable=False)
    metric_id = Column(Integer, ForeignKey('financial_metrics.id'), nullable=False)
    value = Column(Float)
    notes = Column(Text)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
    
    # Relationships
    report = relationship("FinancialReport", back_populates="metrics")
    metric = relationship("FinancialMetric", back_populates="data_points")
    
    def __repr__(self):
        return f"<YearlyData(report_id={self.report_id}, metric_id={self.metric_id}, value={self.value})>"

class ShareholderData(Base):
    """Model for storing detailed shareholder data."""
    __tablename__ = 'shareholder_data'

    id = Column(Integer, primary_key=True)
    report_id = Column(Integer, ForeignKey('financial_reports.id'), nullable=False)
    rank = Column(Integer)
    shareholder_name = Column(String(255), nullable=False)
    number_of_shares = Column(Integer) # Using Integer, adjust if shares can be fractional
    percentage_holding = Column(Float)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    # Relationship back to FinancialReport (optional but good practice)
    report = relationship("FinancialReport") # Add back_populates if needed later

    def __repr__(self):
        return f"<ShareholderData(report_id={self.report_id}, rank={self.rank}, name='{self.shareholder_name}', holding={self.percentage_holding}%)>"
