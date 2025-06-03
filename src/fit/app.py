from flask import Flask
from src.fit.blueprints.auth import bp_auth
from src.fit.blueprints.users import bp_users
from src.fit.blueprints.fitness import bp_fitness
from src.fit.database import init_db
from src.fit.services.fitness_data_init import init_fitness_data

app = Flask(__name__)

app.register_blueprint(bp_auth)
app.register_blueprint(bp_users)
app.register_blueprint(bp_fitness)

@app.route("/health")
def health():
    return {"status": "UP"}

def run_app():
    init_db()                
    init_fitness_data()      
    app.run(host="0.0.0.0", port=5001, debug=True)

if __name__ == "__main__":
    run_app()
