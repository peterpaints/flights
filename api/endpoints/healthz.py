"""
/healthz endpoint.

"""

from flask import Blueprint, jsonify

healthz = Blueprint('healthz', __name__)


@healthz.route('/api/healthz')
def get():
    """Return service health status."""
    return jsonify({'status': 'healthy'}), 200
