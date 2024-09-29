from flask import Flask, request, jsonify
import google.generativeai as genai
import typing_extensions as typing
from flask_cors import CORS
import json

app = Flask(__name__)
CORS(app)
genai.configure(api_key="")


def load_chat_history(file_path):
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
        with open('unstructured_data_log.txt', 'a', encoding='utf-8') as f:
            f.write(f"Input:\n{combined_data}\n\n")
        print(json.dumps(combined_data, indent=4))
        result = crossVerify(combined_data)

        parsed_result = json.loads(result.text)
        if parsed_result['is_doc_verified']:
            message = "The document has been successfully verified."
        else:
            message = "The document verification failed."
            reasons = []
            if not parsed_result['is_name_verified']:
                reasons.append("Name does not match.")
            if not parsed_result['is_father_name_verified']:
                reasons.append("Father's name does not match.")
            if not parsed_result['is_dob_verified']:
                reasons.append("Date of birth does not match.")
            if not parsed_result['is_addhar_no_verified']:
                reasons.append("Aadhaar number does not match.")

            sub_status = "Reasons: " + ", ".join(reasons) if reasons else "No specific reason provided."
            message = f"{message} {sub_status}"

        return jsonify({"message": message}), 200

    except Exception as e:
        print(f"An error occurred: {e}")
        return jsonify({"error": str(e)}), 400


class VerifySchema(typing.TypedDict):
    doc_type: str
    is_name_verified: bool
    is_dob_verified: bool
    is_father_name_verified: bool
    is_addhar_no_verified: bool
    is_doc_verified: bool


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


def crossVerify(combined_data):
    chat_history = load_chat_history('chat_history.json')
    chat_session = model.start_chat(history=chat_history)
    result = chat_session.send_message(f"""{combined_data}""")
    print(result)
    return result


if __name__ == '__main__':
    app.run(debug=True)
