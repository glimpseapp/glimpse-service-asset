from flask_restful import Resource


class Image(Resource):
    def post(self):
        return {"status": True}
