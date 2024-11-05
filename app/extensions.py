from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_bootstrap import Bootstrap
from flask_wtf.csrf import CSRFProtect
from flask_jwt_extended import JWTManager

# initialize flask extensions
login_manager = LoginManager()
migrate = Migrate()
bootstrap = Bootstrap()
csrf = CSRFProtect()
jwt = JWTManager()
db = SQLAlchemy()