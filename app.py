from flask import Flask, request, jsonify
from flask_cors import CORS
import json

app = Flask(__name__)
CORS(app)


@app.route('/verify', methods=['POST'])
def get_named_entity():
    try:
        data = request.get_json()

        form_data = data.get('formData')
        pdf_text = data.get('pdfText')

        name = form_data.get('name')
        father_name = form_data.get('fatherName')
        dob = form_data.get('dob')
        aadhaar_number = form_data.get('aadhaarNumber')

        named_entity = {
            "name": name,
            "father_name": father_name,
            "dob": dob,
            "aadhaar_number": aadhaar_number
        }
        unstructured_data = {"unstructured_data": pdf_text}
        combined_data = {**named_entity, **unstructured_data}

        print(json.dumps(combined_data, indent=4))

        return jsonify(combined_data), 200

    except Exception as e:
        print(f"An error occurred: {e}")
        return jsonify({"error": str(e)}), 400


if __name__ == '__main__':
    app.run(debug=True)
