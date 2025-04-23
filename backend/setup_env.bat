@echo off
echo Setting up virtual environment for JKH Financial Dashboard...

REM Create virtual environment
python -m venv venv

REM Activate virtual environment
call venv\Scripts\activate

REM Upgrade pip
python -m pip install --upgrade pip

REM Install dependencies
pip install -r requirements.txt

REM Create .env file
echo Creating .env file...
echo SECRET_KEY=development-secret-key > .env
echo FLASK_ENV=development >> .env
echo DATABASE_URI=sqlite:///jkh_financial.db >> .env
echo PDF_DIRECTORY=../data-pdf >> .env

echo Setup completed successfully!
echo To activate the environment, run: venv\Scripts\activate 