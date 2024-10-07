from flask import Flask, request, jsonify
import google.generativeai as genai
from dotenv import load_dotenv
from flask_cors import CORS
import json
import os

app = Flask(__name__)
CORS(app)
load_dotenv()
genai.configure(api_key=os.getenv('API_KEY'))


def load_json(file_path):
    with open(file_path, 'r') as file:
        return json.load(file)


@app.route('/', methods=['GET'])
def home():
    return 'Server is running!'


@app.route('/verify', methods=['POST'])
def get_named_entity():
    try:
        data = request.get_json()
        form_data = data.get('formData')
        doc_type = data.get('docType')  # Get the document type
        extracted_text = data.get('extractedText')

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

        unstructured_data = {"unstructured_data": extracted_text}
        combined_data = {**named_entity, **unstructured_data}
        with open('unstructured_data_log.txt', 'a', encoding='utf-8') as f:
            f.write(f"Input:\n{combined_data}\n\n")

        if doc_type == 'aadhaar':
            schema = load_json('aadhaarSchema.json')
        elif doc_type == 'pan':
            schema = load_json('panSchema.json')
        elif doc_type == 'marksheet':
            schema = load_json('marksheetSchema.json')
        else:
            return jsonify({"error": "Invalid document type"}), 400

        print(json.dumps(combined_data, indent=4))
        result = crossVerify(combined_data, schema)

        parsed_result = json.loads(result.text)
        if parsed_result['is_document_verified']:
            message = f"The {doc_type} verification was successful."
        else:
            message = f"The {doc_type} verification failed."
            reasons = []
            if not parsed_result.get('is_name_verified'):
                reasons.append("Name does not match.")
            if not parsed_result.get('is_father_name_verified'):
                reasons.append("Father's name does not match.")
            if not parsed_result.get('is_dob_verified'):
                reasons.append("Date of birth does not match.")
            if not parsed_result.get('is_addhar_no_verified') and doc_type == 'aadhaar':
                reasons.append("Aadhaar number does not match.")
            if not parsed_result.get('is_aadhaar') and doc_type == 'aadhaar':
                reasons.append("Aadhaar not found in the document.")
            if not parsed_result.get('is_pan_no_verified') and doc_type == 'pan':
                reasons.append("PAN number does not match.")
            if not parsed_result.get('is_pan') and doc_type == 'pan':
                reasons.append("PAN not found in the document.")
            if not parsed_result.get('is_marksheet_verified') and doc_type == 'marksheet':
                reasons.append("Marksheet does not match.")
            if not parsed_result.get('is_marksheet') and doc_type == 'marksheet':
                reasons.append("Marksheet not found in the document.")


            sub_status = "Reasons: " + ", ".join(reasons) if reasons else "No specific reason provided."
            message = f"{message} {sub_status}"

        return jsonify({"message": message}), 200

    except Exception as e:
        print(f"An error occurred: {e}")
        return jsonify({"error": str(e)}), 400


def crossVerify(combined_data, VerifySchema):
    model = genai.GenerativeModel('gemini-1.5-flash',
                                  safety_settings="BLOCK_ONLY_HIGH",
                                  generation_config={"response_mime_type": "application/json",
                                                     "temperature": 0.7,
                                                     "top_p": 0.95,
                                                     "top_k": 64,
                                                     "max_output_tokens": 8192,
                                                     "response_schema": VerifySchema},
                                  system_instruction="input:{\n    \"name\": \"\",\n    \"father_name\": \"\",\n    \"dob\": \"\",\n    \"aadhaar_number\": \"\",\n    \"unstructured_data\": \"\"\n}\n\nif the named entities in input is same as in unstructured return true else return false\nif any of the entity is not matched return document verification as false else true",
                                  )
    chat_history = load_json('chat_history.json')
    chat_session = model.start_chat(history=chat_history)
    result = chat_session.send_message(f"""{combined_data}""")
    print(result)
    return result


if __name__ == '__main__':
    app.run(debug=True)
