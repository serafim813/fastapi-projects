# fastapi-projects

Projects FastAPI via Heroku.

# To run locally
- git clone https://github.com/serafim813/fastapi-projects.git
- pip install -r requirements.txt

# Then, run via uvicorn:
- uvicorn main:app --reload

# To deploy to heroku
- heroku login  
- heroku create
- git push heroku main
- heroku open
