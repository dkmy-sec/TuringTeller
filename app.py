from flask import Flask, render_template, request, redirect, url_for, session
from werkzeug.utils import secure_filename
import csv
import os
from ai_detect import analyze_media, analyze_audio_file, analyze_video_file, process_media_file, detect_ai_text


app = Flask(__name__)
app.secret_key = 'your_secret_key_here'  # Required for session management

app.config['UPLOAD_FOLDER'] = 'uploads/'
app.config['ALLOWED_EXTENSIONS'] = {'mp3', 'wav', 'mp4', 'mov'}


# Defined a function to check Allowed File types
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']


# Define the questions
questions = [
             {"id": "contextual_understanding",
              "text": "Imagine someone says 'Oh, great!' after hearing bad news. What do you think they mean?"},
             {"id": "creativity_test", "text": "Write a short poem about 'regret.'"}, {"id": "emotional_resonance",
                                                                                       "text": "How do you feel when you think about someone you love who is no longer with you?"},
             {"id": "humor_test",
              "text": "Why did the scarecrow win an award? Because he was outstanding in his field! Do you get the joke? (yes/no): "},
             {"id": "intuition_test",
              "text": "Imagine you have to make a choice with no clear right answer. Do you follow your gut feeling, or do you prefer to analyze the situation logically?"},
            ]


# Home route to start the test
@app.route('/')
def index():
    session['responses'] = []
    return redirect(url_for('question', q_id=0))

# Route to handle each question
@app.route('/question/<int:q_id>', methods=['GET', 'POST'])
def question(q_id):
    if q_id >= len(questions):
        return redirect(url_for('result'))

    question = questions[q_id]

    if request.method == 'POST':
        if question['id'] == 'media_upload':
            # Handle media file upload
            if 'media_file' not in request.files:
                flash('No file part')
                return redirect(request.url)
            file = request.files['media_file']
            if file.filename == '':
                flash('No selected file')
                return redirect(request.url)
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(filepath)
                # Process the media file
                answer = process_media_file(filepath)
            else:
                flash('Invalid file type')
                return redirect(request.url)
        else:
            answer = request.form['answer']
        session['responses'].append({'question': question['text'], 'answer': answer})
        return redirect(url_for('question', q_id=q_id + 1))

    return render_template('question.html', question=question, q_id=q_id)


@app.route('/upload_media', methods=['GET', 'POST'])
def upload_media():
    if request.method == 'POST':
        # Check if a file is submitted
        if 'media_file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['media_file']
        # Check if a file is selected
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        # Validate file type
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            # Process the media file
            result = process_media_file(filepath)
            return render_template('media_result.html', result=result)
        else:
            flash('Invalid file type')
            return redirect(request.url)
    return render_template('upload_media.html')


# Route to display the result and save to CSV
@app.route('/result')
def result():
    # Retrieve responses from the session
    responses = session.get('responses', [])

    # Save responses to CSV (existing code)
    csv_file = 'responses.csv'
    file_exists = os.path.isfile(csv_file)
    with open(csv_file, 'a', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=['question', 'answer'])
        if not file_exists:
            writer.writeheader()
        writer.writerows(responses)

    # Analyze the text responses to determine if they're AI-generated
    concatenated_text = ' '.join([response['answer'] for response in responses])
    is_ai_generated = detect_ai_text(concatenated_text)
    text_result = "AI-generated" if is_ai_generated else "Human-generated"

    return render_template('result.html', responses=responses, text_result=text_result)


if __name__ == '__main__':
    app.run(debug=True)
