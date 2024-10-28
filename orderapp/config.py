import pymysql
pymysql.install_as_MySQLdb()

class Config:
    """Configuration settings for the application.."""

    SECRET_KEY = 'thisismysessionkey'
    PASSWORD_SALT = 'thisismypasswordsalt'
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:154200@localhost:3306/orderapp'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
