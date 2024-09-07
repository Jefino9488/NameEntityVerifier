from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)


@app.route('/verify', methods=['POST'])
def verify_named_entities():
    try:
        data = request.get_json()

        form_data = data.get('formData')
        pdf_text = data.get('pdfText')

        name = form_data.get('name')
        father_name = form_data.get('fatherName')
        dob = form_data.get('dob')
        aadhaar_number = form_data.get('aadhaarNumber')

        verification_result = {
            "name_verified": name in pdf_text,
            "father_name_verified": father_name in pdf_text,
            "dob_verified": dob in pdf_text,
            "aadhaar_number_verified": aadhaar_number in pdf_text
        }

        if all(verification_result.values()):
            return jsonify({"message": "All named entities verified successfully."}), 200
        else:
            return jsonify({"message": "Some named entities do not match.", "result": verification_result}), 400

    except Exception as e:
        return jsonify({"message": str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True)
