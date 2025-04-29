from flask import Flask, redirect, url_for
from dotenv import load_dotenv
import os
from database import db
from api import api_bp

# Load environment variables
load_dotenv()

def create_app(config_name='development'):
    app = Flask(__name__)
    
    # Load configuration
    if config_name == 'production':
        app.config.from_object('config.ProductionConfig')
    elif config_name == 'testing':
        app.config.from_object('config.TestingConfig')
    else:
        app.config.from_object('config.DevelopmentConfig')
    
    # Initialize database
    db.init_db()
    
    # Register blueprints
    app.register_blueprint(api_bp)
    
    # Add root route
    @app.route('/')
    def index():
        return redirect(url_for('api.health_check'))
    
    return app

# Create the Flask application
app = create_app(os.environ.get('FLASK_ENV', 'development'))


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)