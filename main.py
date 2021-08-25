from app import create_app, db
from flask_migrate import Migrate, migrate

app = create_app()
migrate = Migrate(app=app, db=db)

if __name__ == '__main__':
  app.run()