#!/bin/bash
echo "Setting up virtual environment for JKH Financial Dashboard..."

# Create virtual environment
python -m venv venv

# Activate virtual environment
source venv/bin/activate

# Upgrade pip
python -m pip install --upgrade pip

# Install dependencies
pip install -r requirements.txt

# Create .env file
echo "Creating .env file..."
cat > .env << EOL
SECRET_KEY=development-secret-key
FLASK_ENV=development
DATABASE_URI=sqlite:///jkh_financial.db
PDF_DIRECTORY=../data-pdf
EOL

echo "Setup completed successfully!"
echo "To activate the environment, run: source venv/bin/activate" 