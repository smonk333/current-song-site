from app import create_app
from dotenv import load_dotenv
import os.path

dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
try:
    load_dotenv(dotenv_path)
except FileNotFoundError:
    print("No .env file found")

app = create_app()

if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', load_dotenv=True)