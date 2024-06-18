from flask import Flask, request
from flask_restful import Resource, Api
from flask_cors import CORS
import os
import recommendation_system_tps as tps_rec
import recommendation_system_literasi as literasi_rec
import exp_calculation as exp_calc

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
                return {'status': 'success', 'data': {'questions': questions}}, 200
            elif data["quizCategory"] == "Literasi":
                questions = literasi_rec.get_recommendation(data["userId"])
                return {'status': 'success', 'data': {'questions': questions}}, 200
            else:
                return {'status': 'error', 'message': 'Invalid quiz category'}, 400

        except Exception:
            return {'error': 'Internal server error'}, 500


class ClaculateExp(Resource):
    def post(self):
        try:
            data = request.get_json()
            answers = data["answers"]
            exp_gain = round(exp_calc.calculate_exp(answers))
            return {'status': 'success', 'data': {'exp': exp_gain}}, 200

        except Exception:
            return {'error': 'Internal server error'}, 500


api.add_resource(Test, '/')
api.add_resource(GetRecommendation, '/recommendation')
api.add_resource(ClaculateExp, '/exp')

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
