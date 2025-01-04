import os

from dotenv import load_dotenv
from flask import Flask, Blueprint
from flask_restx import Api
from werkzeug.middleware.proxy_fix import ProxyFix

from api.api import api as translator_ns

load_dotenv()

app = Flask(__name__)

with app.app_context():
    app.config['KEYCLOAK_SERVER_URL'] = os.getenv('KEYCLOAK_SERVER_URL')
    app.config['OIDC_OP_AUTHORIZATION_ENDPOINT'] = os.getenv('OIDC_OP_AUTHORIZATION_ENDPOINT')
    app.config['OIDC_OP_TOKEN_ENDPOINT'] = os.getenv('OIDC_OP_TOKEN_ENDPOINT')
    app.config['OIDC_OP_USER_ENDPOINT'] = os.getenv('OIDC_OP_USER_ENDPOINT')
    app.config['OIDC_OP_JWKS_ENDPOINT'] = os.getenv('OIDC_OP_JWKS_ENDPOINT')
    app.config['OIDC_OP_LOGOUT_ENDPOINT'] = os.getenv('OIDC_OP_LOGOUT_ENDPOINT')
    app.config['OIDC_OP_ENDSESSION_ENDPOINT'] = os.getenv('OIDC_OP_ENDSESSION_ENDPOINT')
    app.config['OIDC_OP_LOGOUT_URL_METHOD'] = os.getenv('OIDC_OP_LOGOUT_URL_METHOD')
    app.config['OIDC_RP_CLIENT_ID'] = os.getenv('OIDC_RP_CLIENT_ID')
    app.config['OIDC_RP_REALM_ID'] = os.getenv('OIDC_RP_REALM_ID')
    app.config['OIDC_RP_CLIENT_SECRET'] = os.getenv('OIDC_RP_CLIENT_SECRET')
    app.config['OIDC_RP_SIGN_ALGO'] = os.getenv('OIDC_RP_SIGN_ALGO')

    # app.wsgi_app = KeycloakMiddleware(app)
    app.wsgi_app = ProxyFix(app.wsgi_app)
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
          description='Experiments with python flask', prefix='/api',
          authorizations=authorizations)


# create an app context so the App can be used in different modules
api.add_namespace(translator_ns, path='/v1/translator')
