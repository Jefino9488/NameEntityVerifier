from flask import Flask, request, jsonify
import google.generativeai as genai
from load_creds import load_creds
from flask_cors import CORS
from google.ai.generativelanguage_v1beta.types import content
import json

app = Flask(__name__)
CORS(app)
creds = load_creds()
genai.configure(credentials=creds)

generation_config = {
    "temperature": 0.7,
    "top_p": 0.95,
    "top_k": 64,
    "max_output_tokens": 8192,
    "response_schema": content.Schema(
        content.Type.OBJECT,
        enum={},
        required={
            "is_name_verified": True,
            "doc_type": True,
            "is_DOB_verified": True,
            "is_document_verified": True
        },
        properties={
            "is_name_verified": content.Schema(content.Type.BOOLEAN, ),
            "doc_type": content.Schema(content.Type.STRING, ),
            "is_address_verified": content.Schema(content.Type.BOOLEAN, ),
            "is_DOB_verified": content.Schema(content.Type.BOOLEAN, ),
            "is_father_name_verified": content.Schema(content.Type.BOOLEAN, ),
            "is_addhar_no_verified": content.Schema(content.Type.BOOLEAN, ),
            "is_document_verified": content.Schema(content.Type.BOOLEAN, ),
        },
    ),
    "response_mime_type": "application/json",
}


@app.route('/', methods=['GET'])
def home():
    return 'Server is running!'


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


def crossVerify(combined_data):
    model = genai.GenerativeModel(
        model_name="gemini-1.5-pro",
        generation_config=generation_config,
        system_instruction="{\n    \"name\": \"\",\n    \"father_name\": \"\",\n    \"dob\": \"\",\n    \"aadhaar_number\": \"\",\n    \"unstructured_data\": \"\"\n}\n\nif the named entities is same as in unstructured return true else return false\nif any of the entity is not matched return document verification as false else true",
    )
    prompt = combined_data
    result = model.generate_content(prompt)
    print(result)
    return result


if __name__ == '__main__':
    app.run(debug=True)
