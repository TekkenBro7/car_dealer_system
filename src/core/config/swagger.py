class SwaggerConfig:
    SWAGGER_SETTINGS = {
        "SECURITY_DEFINITIONS": {
            "Bearer": {
                "type": "apiKey",
                "name": "Authorization",
                "in": "header",
                "description": 'JWT Auth header. Example: "Bearer <access token>"',
            }
        },
        "USE_SESSION_AUTH": False,
    }
