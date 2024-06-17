from flask import Flask, request
from flask_restful import Resource, Api
from flask_cors import CORS
import os
import recommendation_system_tps as tps_rec
import recommendation_system_literasi as literasi_rec

app = Flask(__name__)
cors = CORS(app, resources={r"*": {"origins": "*"}})
api = Api(app)


class Test(Resource):
    def get(self):
        return {'status': 'success', 'message': 'Welcome to, Test App API!'}


class GetRecommendation(Resource):
    def post(self):
        try:
            data = request.get_json()
            if data["quizCategory"] == "TPS":
                questions = tps_rec.get_recommendation(data["userId"])
                return {'status': 'success', 'data': {'questions': questions}}
            elif data["quizCategory"] == "Literasi":
                questions = literasi_rec.get_recommendation(data["userId"])
                return {'status': 'success', 'data': {'questions': questions}}

        except Exception as error:
            return {'error': error}


api.add_resource(Test, '/')
api.add_resource(GetRecommendation, '/recommendation')
# api.add_resource(GetPredictionOutput, '/exp')

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
