import logging
from typing import Any, Dict, List, Tuple

from flasgger import Swagger
from flask import Flask, jsonify, Response, request
from sqlalchemy import create_engine, Column, Integer, Float, String
from sqlalchemy.orm import declarative_base, sessionmaker

# Main app
app = Flask(__name__)
swagger = Swagger(app)
Base = declarative_base()


# Define the Auto model
class Auto(Base):
    __tablename__ = 'autos'
    auto_id = Column(Integer, primary_key=True)
    parking_name = Column(String)
    parking_price = Column(Float)


# Database connection
engine = create_engine('sqlite:///autos.db', echo=False)
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# API Routes

@app.route('/auto', methods=['GET'])
def get_all_autos() -> Tuple[Response, int]:
    """
    Get all autos
    ---
    responses:
      200:
        description: List of autos
        schema:
          type: array
          items:
            type: object
            properties:
              auto_id:
                type: integer
                description: The ID of the auto
              parking_name:
                type: string
                description: The name of the parking location
              parking_price:
                type: number
                format: float
                description: The price for parking
      500:
        description: An error occurred while retrieving autos
    """
    try:
        with Session() as session:
            auto_list = session.query(Auto).all()
            autos: List[Dict[str, Any]] = [
                {
                    'auto_id': auto.auto_id,
                    'parking_name': auto.parking_name,
                    'parking_price': auto.parking_price
                }
                for auto in auto_list
            ]
            logger.info('Retrieved %d autos', len(autos))
            return jsonify(autos), 200

    except Exception as e:
        logger.error('Error retrieving autos: %s', str(e))
        return jsonify({'error': 'An error occurred while retrieving autos.'}), 500


@app.route('/auto/<int:auto_id>', methods=['GET'])
def get_auto(auto_id: int) -> Tuple[Response, int]:
    """
    Get a specific auto by ID
    ---
    parameters:
      - name: auto_id
        in: path
        type: integer
        required: true
        description: The ID of the auto
    responses:
      200:
        description: The auto details
      404:
        description: Auto not found
      500:
        description: An error occurred while retrieving the auto
    """
    try:
        with Session() as session:
            auto = session.query(Auto).filter(Auto.auto_id == auto_id).first()
            if auto is None:
                return jsonify({'error': 'Auto not found'}), 404

            result = {
                'auto_id': auto.auto_id,
                'parking_name': auto.parking_name,
                'parking_price': auto.parking_price
            }
            logger.info('Retrieved auto: %s', result)
            return jsonify(result), 200

    except Exception as e:
        logger.error('Error retrieving auto with ID %d: %s', auto_id, str(e))
        return jsonify({'error': 'An error occurred while retrieving the auto.'}), 500


@app.route('/auto', methods=['POST'])
def create_auto() -> Tuple[Response, int]:
    """
    Create a new auto
    ---
    parameters:
      - name: body
        in: body
        required: true
        schema:
          type: object
          properties:
            parking_name:
              type: string
            parking_price:
              type: number
              format: float
    responses:
      201:
        description: Auto created successfully
      400:
        description: Invalid input
      500:
        description: An error occurred while creating the auto
    """
    try:
        data = request.json
        new_auto = Auto(
            parking_name=data['parking_name'],
            parking_price=data['parking_price']
        )

        with Session() as session:
            session.add(new_auto)
            session.commit()
            logger.info('Created new auto: %s', new_auto)
            return jsonify({'auto_id': new_auto.auto_id}), 201

    except Exception as e:
        logger.error('Error creating auto: %s', str(e))
        return jsonify({'error': 'An error occurred while creating the auto.'}), 500


@app.route('/auto/<int:auto_id>', methods=['PUT'])
def update_auto(auto_id: int) -> Tuple[Response, int]:
    """
    Update an existing auto by ID
    ---
    parameters:
      - name: auto_id
        in: path
        type: integer
        required: true
        description: The ID of the auto
      - name: body
        in: body
        required: true
        schema:
          type: object
          properties:
            parking_name:
              type: string
            parking_price:
              type: number
              format: float
    responses:
      200:
        description: Auto updated successfully
      404:
        description: Auto not found
      500:
        description: An error occurred while updating the auto
    """
    try:
        data = request.json
        with Session() as session:
            auto = session.query(Auto).filter(Auto.auto_id == auto_id).first()
            if auto is None:
                return jsonify({'error': 'Auto not found'}), 404

            auto.parking_name = data.get('parking_name', auto.parking_name)
            auto.parking_price = data.get('parking_price', auto.parking_price)
            session.commit()

            logger.info('Updated auto ID %d: %s', auto_id, auto)
            return jsonify({'auto_id': auto.auto_id}), 200

    except Exception as e:
        logger.error('Error updating auto ID %d: %s', auto_id, str(e))
        return jsonify({'error': 'An error occurred while updating the auto.'}), 500


@app.route('/auto/<int:auto_id>', methods=['PATCH'])
def patch_auto(auto_id: int) -> Tuple[Response, int]:
    """
    Partially update an existing auto by ID
    ---
    parameters:
      - name: auto_id
        in: path
        type: integer
        required: true
        description: The ID of the auto
      - name: body
        in: body
        required: true
        schema:
          type: object
          properties:
            parking_name:
              type: string
            parking_price:
              type: number
              format: float
    responses:
      200:
        description: Auto partially updated successfully
      404:
        description: Auto not found
      500:
        description: An error occurred while partially updating the auto
    """
    try:
        data = request.json
        with Session() as session:
            auto = session.query(Auto).filter(Auto.auto_id == auto_id).first()
            if auto is None:
                return jsonify({'error': 'Auto not found'}), 404

            if 'parking_name' in data:
                auto.parking_name = data['parking_name']
            if 'parking_price' in data:
                auto.parking_price = data['parking_price']
            session.commit()

            logger.info('Partially updated auto ID %d: %s', auto_id, auto)
            return jsonify({'auto_id': auto.auto_id}), 200

    except Exception as e:
        logger.error('Error partially updating auto ID %d: %s', auto_id, str(e))
        return jsonify({'error': 'An error occurred while partially updating the auto.'}), 500


@app.route('/auto/<int:auto_id>', methods=['DELETE'])
def delete_auto(auto_id: int) -> Tuple[Response, int]:
    """
    Delete an auto by ID
    ---
    parameters:
      - name: auto_id
        in: path
        type: integer
        required: true
        description: The ID of the auto
    responses:
      204:
        description: Auto deleted successfully
      404:
        description: Auto not found
      500:
        description: An error occurred while deleting the auto
    """
    try:
        with Session() as session:
            auto = session.query(Auto).filter(Auto.auto_id == auto_id).first()
            if auto is None:
                return jsonify({'error': 'Auto not found'}), 404

            session.delete(auto)
            session.commit()

            logger.info('Deleted auto ID %d', auto_id)
            return jsonify({}), 204

    except Exception as e:
        logger.error('Error deleting auto ID %d: %s', auto_id, str(e))
        return jsonify({'error': 'An error occurred while deleting the auto.'}), 500


if __name__ == '__main__':
    app.run(debug=True)
