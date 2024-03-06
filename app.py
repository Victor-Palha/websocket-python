from flask import Flask, jsonify, request, send_file
from repository.database import db
from models_db.payment import Payment
from datetime import datetime, timedelta
from payments.pix import Pix
from flask_socketio import SocketIO

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SECRET_KEY'] = 'some_secret_key'
socketio = SocketIO(app)
db.init_app(app)


@app.route('/payments/pix', methods=["POST"])
def create_payment_pix():
    data = request.get_json()
    if "value" not in data:
        return jsonify({
            "message": "Please provide the value data"
        }), 400

    expiration_date = datetime.now() + timedelta(minutes=30)
    new_payment = Payment(value=data["value"], expiration_date=expiration_date)
    db.session.add(new_payment)
    pix_data_information = Pix.create_payment()
    new_payment.bank_payment_id = pix_data_information["bank_payment_id"]
    new_payment.qr_code = pix_data_information["qr_code_path"]
    db.session.commit()

    return jsonify({
        "message": "Payment successfully created",
        "payment": new_payment.to_dict()
    }), 201


@app.route('/payments/pix/qr_code/<file_name>')
def get_qr_code(file_name):
    return send_file(f"static/img/{file_name}", mimetype="image/png")


@app.route('/payments/pix/confirmation', methods=["POST"])
def pix_confirmation():
    data = request.get_json()
    if "bank_payment_id" not in data or "value" not in data:
        return jsonify({
            "message": "Please provide the bank payment"
        }), 400
    payment = Payment.query.filter_by(bank_payment_id=data["bank_payment_id"]).first()
    if not payment or payment.paid is True:
        return jsonify({
            "message": "Payment does not exist"
        }), 404

    if data.get("value") != payment.value:
        return jsonify({
            "message": "Invalid payment data"
        }), 400

    payment.paid = True
    db.session.commit()
    socketio.emit(f"payment_confirmed-{payment.id}", {"message": "Payment successfully confirmed"})
    return jsonify({"status": "Payment successfully"})


@app.route('/payments/<int:payment_id>', methods=["GET"])
def payment_pix_page(payment_id):
    return jsonify({
        "status": "success"
    })


@socketio.on('connect')
def connect():
    print("Client connected")


@socketio.on('disconnect')
def disconnect():
    print("Client disconnected")


if __name__ == '__main__':
    socketio.run(app, debug=True)

