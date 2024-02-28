@app.route('/pdf-lesson-planner', methods=['POST'])
def pdf_lesson_planner():
    try:
        if 'file' not in request.files:
            return jsonify({'message': 'No file part'}), 400

        file = request.files['file']
        if file.filename == '':
            return jsonify({'message': 'No selected file'}), 400

        if file and allowed_file(file.filename):
            # Read the PDF file and extract text content
            pdfReader = PyPDF2.PdfFileReader(io.BytesIO(file.read()))
            text = ""
            for page in range(pdfReader.numPages):
                text += pdfReader.getPage(page).extractText()

            # Generate a lesson plan using OpenAI API
            response = generate_lesson_plan(text)

            return jsonify(response), 200
        else:
            return jsonify({'message': 'Invalid file type'}), 400

    except Exception as e:
        print(e)
        return jsonify({'message': str(e)}), 500


def generate_lesson_plan(text):
    try:
        # Generate a lesson plan using OpenAI API
        system_message_pdf = "Create a lesson plan based on the text extracted from the PDF file."
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": system_message_pdf},
                {"role": "user", "content": text},
            ],
            response_format={"type": "json_object"},
        )

        json_format = json.loads(response.choices[0].message.content)
        return json_format

    except Exception as e:
        print(e)
        raise CustomError("Error generating lesson plan from PDF.")
    