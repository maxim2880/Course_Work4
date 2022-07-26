from flask_restx import Namespace, Resource
from flask import request

from project.container import genre_service, movie_service
from project.services.decorators import auth_requered
from project.setup.api.models import genre, movie
from project.setup.api.parsers import page_parser

api = Namespace('movies')


@api.route('/')
class MoviesView(Resource):
    @auth_requered
    @api.expect(page_parser)
    @api.marshal_with(movie, as_list=True, code=200, description='OK')
    def get(self):
        """
        Get all movies.
        """
        filter = request.args.get('status')
        if filter != None and filter == 'new':
            return movie_service.get_all(filter=filter, **page_parser.parse_args())
        return movie_service.get_all(**page_parser.parse_args())


@api.route('/<int:movie_id>/')
class MovieView(Resource):
    @auth_requered
    @api.response(404, 'Not Found')
    @api.marshal_with(movie, code=200, description='OK')
    def get(self, movie_id: int):
        """
        Get genre by id.
        """
        return movie_service.get_item(movie_id)
