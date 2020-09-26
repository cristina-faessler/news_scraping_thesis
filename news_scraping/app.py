from flask import Flask


app = Flask(__name__)
db_uri = 'mysql+pymysql://root:dbs30@localhost/feedreader'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = db_uri