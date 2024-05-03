from laZone import create_app

application = create_app()

if __name__ == '__main__':
    application.run(ssl_context=('cert.pem','key.pem'))
