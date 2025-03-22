from flask import Flask, Blueprint
from flask_cors import CORS
from flask_restx import Api

from api.api import api as translator_ns
from person.views import api as person_ns
app = Flask(__name__)
cors = CORS(app,
            allow_headers=["Content-Type", "Authorization", "User-Agent", "Accept"],
            allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            allow_origins=["*"]
            ) # allow CORS for all domains on all routes.
# app.config['CORS_HEADERS'] = 'Content-Type'

blueprint = Blueprint('api', __name__)
app.register_blueprint(blueprint)

authorizations = {
    'bearer': {
        'name': "Authorization",
        'in': "header",
        'type': "oauth2",
        'flow': "password",
        'scopes': {
            'openid': 'openid'
        },
        'description': "Request with username and password!"
    }
}
api = Api(app,
          title='Flask ExtremeXP App',
          version='1.0',
          description='Experiments with python flask', prefix='/extreme_auth',
          authorizations=authorizations)


# create an app context so the App can be used in different modules
api.add_namespace(translator_ns, path='/api/v1/translator')
api.add_namespace(person_ns, path='/api/v1/person')
