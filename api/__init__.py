from flask import Flask, Blueprint
from flask_cors import CORS
from flask_restx import Api, apidoc

from api.api import api as translator_ns
from person.views import api as person_ns
from orgs.views import api as orgs_ns
from resource.views import api as resource_ns
app = Flask(__name__)
cors = CORS(app,
            allow_headers=["Content-Type", "Authorization", "User-Agent", "Accept"],
            allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
            allow_origins=["*"]
            ) # allow CORS for all domains on all routes.
# app.config['CORS_HEADERS'] = 'Content-Type'

blueprint = Blueprint('api', __name__,
                      static_url_path='/extreme_auth/swaggerui',
                      url_prefix='/extreme_auth',
                      root_path='/extreme_auth')

apidoc.static_url_path = "/extreme_auth/swaggerui"
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
          title='Access Control ExtremeXP App',
          version='1.0',
          description='Access Control API for ExtremeXP App',
          doc='/extreme_auth',
          prefix='/extreme_auth',
          authorizations=authorizations)


# create an app context so the App can be used in different modules
api.add_namespace(translator_ns, path='/api/v1/translator')
api.add_namespace(person_ns, path='/api/v1/person')
api.add_namespace(resource_ns, path='/api/v1/resource')
