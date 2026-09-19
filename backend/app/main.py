from flask import Flask, jsonify, request
from flask_cors import CORS
from app.config.settings import Config
from app.config.database import Database
from app.utils.logger import setup_logger
from app.utils.responses import error_response, success_response
from app.utils.seeder import seed_database

# Routers
from app.routers.auth import auth_bp
from app.routers.organizations import organizations_bp
from app.routers.projects import projects_bp
from app.routers.item_types import item_types_bp
from app.routers.items import items_bp
from app.routers.part_types import part_types_bp
from app.routers.vendors import vendors_bp
from app.routers.parts import parts_bp
from app.routers.lots import lots_bp
from app.routers.cells import cells_bp
from app.routers.locations import locations_bp
from app.routers.inventory import inventory_bp
from app.routers.stock import stock_bp
from app.routers.transactions import transactions_bp
from app.routers.dashboard import dashboard_bp
from app.routers.reports import reports_bp
from app.routers.indents import indents_bp
from app.routers.indent_returns import indent_returns_bp
from app.routers.users import users_bp

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Logging
    logger = setup_logger("inventory_backend")
    logger.info("Initializing MES Inventory Management Application...")

    # CORS
    CORS(app, resources={r"/api/*": {"origins": "*"}}, supports_credentials=True)

    # Database Initialization
    Database.initialize(app.config["MONGO_URI"], app.config["MONGO_DB_NAME"])

    # Seeding
    try:
        seed_database()
    except Exception as e:
        logger.warning(f"Seeder note: {e}")

    # Register Blueprints - Core 9-Entity Schema & Legacy Routers
    app.register_blueprint(auth_bp)
    app.register_blueprint(users_bp)
    app.register_blueprint(organizations_bp)
    app.register_blueprint(projects_bp)
    app.register_blueprint(item_types_bp)
    app.register_blueprint(items_bp)
    app.register_blueprint(part_types_bp)
    app.register_blueprint(vendors_bp)
    app.register_blueprint(parts_bp)
    app.register_blueprint(lots_bp)
    app.register_blueprint(cells_bp)
    app.register_blueprint(locations_bp)
    app.register_blueprint(inventory_bp)
    app.register_blueprint(stock_bp)
    app.register_blueprint(transactions_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(reports_bp)
    app.register_blueprint(indents_bp)
    app.register_blueprint(indent_returns_bp)

    @app.route("/api/health", methods=["GET"])
    def health_check():
        return success_response({
            "status": "HEALTHY",
            "service": "MES Inventory Management API",
            "version": "1.0.0",
            "replica_set": Database.is_replica_set
        }, message="API is live and operational")

    @app.errorhandler(404)
    def not_found(e):
        return error_response("NOT_FOUND", "The requested endpoint does not exist", 404)

    @app.errorhandler(500)
    def internal_error(e):
        return error_response("INTERNAL_SERVER_ERROR", "An unexpected server error occurred", 500)

    return app

if __name__ == "__main__":
    app = create_app()
    app.run(
        host=Config.HOST,
        port=Config.PORT,
        debug=Config.DEBUG
    )

