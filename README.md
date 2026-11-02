# \# EconoCausal: Dynamic Pricing via Double Machine Learning

#

# \## Project Overview

#

# EconoCausal is a machine learning project that explores how discounts influence customer purchase behavior. It combines Double Machine Learning (DML)-style estimation, predictive modeling, and discount scenario comparison to support data-driven pricing decisions.

#

# \## The Problem

#

# Traditional predictive ML models identify customers likely to purchase, but they do not necessarily determine whether a marketing offer will change customer behavior. Businesses may waste money discounting purchases that would happen anyway.

#

# \## The Solution

#

# EconoCausal uses a DML-style approach to estimate the relationship between discounts and purchase behavior. It also evaluates different discount scenarios using a predictive model to identify promising discount levels.

#

# \## Key Features

#

# \- Synthetic pricing dataset with 2,000 customer records.

# \- DML-style discount effect estimation.

# \- Predictive discount optimization across 36 scenarios.

# \- FastAPI backend for accessing project functionality.

# \- Dataset summary and preview endpoints.

# \- Automated tests for model, API, and data validation.

#

# \## Technology Stack

#

# \- Python

# \- Pandas and NumPy

# \- Scikit-learn

# \- FastAPI

# \- Uvicorn

# \- Git and GitHub

#

# \## Project Structure

#

# ```text

# EconoCausal/

# │

# ├── app/

# │   └── main.py

# ├── backend/

# │   └── requirements.txt

# ├── data/

# │   └── pricing\_data.csv

# ├── dml\_model.py

# ├── discount\_optimizer.py

# ├── generate\_data.py

# ├── test\_dml\_model.py

# ├── test\_api.py

# ├── test\_api\_validation.py

# ├── test\_discount\_optimizer.py

# ├── API\_DOCUMENTATION.md

# ├── PROJECT\_OVERVIEW.md

# └── README.md

# ```

#

# \## Installation and Setup

#

# \### 1. Clone the Repository

#

# ```bash

# git clone https://github.com/Aakash25DS02/-EconoCausal-Dynamic-Pricing-via-Double-Machine-Learning.git

# ```

#

# \### 2. Open the Project Directory

#

# ```bash

# cd -EconoCausal-Dynamic-Pricing-via-Double-Machine-Learning

# ```

#

# \### 3. Install Dependencies

#

# ```bash

# python -m pip install -r backend/requirements.txt

# ```

#

# \## Run the Application

#

# Start the FastAPI server:

#

# ```bash

# python -m uvicorn app.main:app --reload

# ```

#

# Open the following URL in your browser:

#

# \- API documentation: http://127.0.0.1:8000/docs

# \- Health check: http://127.0.0.1:8000/health

#

# \## API Endpoints

#

# | Endpoint | Description |

# |---|---|

# | `/` | Project welcome endpoint |

# | `/health`
