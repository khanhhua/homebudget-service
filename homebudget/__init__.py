from pyramid.config import Configurator
# See http://docs.pylonsproject.org/projects/pyramid_cookbook/en/latest/database/sqlalchemy.html
# See http://docs.pylonsproject.org/projects/pyramid_cookbook/en/latest/database/index.html
from sqlalchemy import engine_from_config
from sqlalchemy.orm import sessionmaker

def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """
    config = Configurator(settings=settings)
    config.include('pyramid_jinja2')
    config.add_jinja2_renderer('.html')

    engine = engine_from_config(settings, prefix='sqlalchemy.')
    config.registry.dbmaker = sessionmaker(bind=engine)
    config.add_request_method(db, reify=True)

    config.add_static_view('static', 'static', cache_max_age=3600)
    config.add_route('home', '/')
    config.add_route('facebook_callback', '/auth/facebook')

    # - - - - - - - - - - - - - - - - - - - - - - - -
    config.add_route('api_quota', '/api/quota')
    config.add_route('api_settings', '/api/settings')
    # - - - - - - - - - - - - - - - - - - - - - - - -
    config.add_route('api_categories', '/api/categories')
    config.add_route('api_entries', '/api/entries')

    config.scan()
    return config.make_wsgi_app()


def db(request):
    maker = request.registry.dbmaker
    session = maker()

    def cleanup(request):
        if request.exception is not None:
            session.rollback()
        else:
            session.commit()
        session.close()
    request.add_finished_callback(cleanup)

    return session
