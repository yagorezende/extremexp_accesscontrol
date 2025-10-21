#/bin/bash
SWAGGER_UI_VERSION="5.29.5"

cd docs/
rm -rf dist swaggerui swagger-ui-$SWAGGER_UI_VERSION swaggerui.zip swagger
mkdir swagger
wget https://github.com/swagger-api/swagger-ui/archive/refs/tags/v$SWAGGER_UI_VERSION.zip -O swaggerui.zip
unzip swaggerui.zip
cp swagger-ui-$SWAGGER_UI_VERSION/dist/* swagger/
cp swagger.json swagger/

echo "Cleaning up downloaded files..."
rm -rf swaggerui.zip swagger-ui-$SWAGGER_UI_VERSION

echo "Modifying Swagger UI to use local swagger.json..."
sed -i 's|https://petstore.swagger.io/v2/swagger.json|swagger.json|g' swagger/swagger-initializer.js
