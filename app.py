from flask import Flask, render_template, request, redirect, url_for, session
import csv
import os

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'  # Required for session management

# Define the questions
questions = [
    {"id": "contextual_understanding", "text": "Imagine someone says 'Oh, great!' after hearing bad news. What do you think they mean?"},
    {"id": "creativity_test", "text": "Write a short poem about 'regret.'"},
    {"id": "emotional_resonance", "text": "How do you feel when you think about someone you love who is no longer with you?"},
    {"id": "humor_test", "text": "Why did the scarecrow win an award? Because he was outstanding in his field! Do you get the joke? (yes/no): "},
    {"id": "intuition_test", "text": "Imagine you have to make a choice with no clear right answer. Do you follow your gut feeling, or do you prefer to analyze the situation logically?"},
    {"id": "pattern_recognition_test", "text": "Here's an abstract image. What do you see? (Describe it in a few words)"},
    {"id": "memory_test", "text": "Earlier, I mentioned a specific word. Do you remember what it was?"},
    {"id": "ambiguity_test", "text": "What do you think is the meaning of life?"},
    {"id": "problem_solving_test", "text": "How would you solve the problem of climate change?"},
    {"id": "cultural_knowledge_test", "text": "What was the cultural impact of the 1960s civil rights movement?"}
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
        answer = request.form['answer']
        session['responses'].append({'question': question['text'], 'answer': answer})
        return redirect(url_for('question', q_id=q_id + 1))

    return render_template('question.html', question=question, q_id=q_id)

# Route to display the result and save to CSV
@app.route('/result')
def result():
    # Retrieve responses from the session
    responses = session.get('responses', [])

    # Define the CSV file path
    csv_file = 'responses.csv'
    file_exists = os.path.isfile(csv_file)

    # Save responses to CSV
    with open(csv_file, 'a', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=['question', 'answer'])
        if not file_exists:
            writer.writeheader()  # Write header only if file does not exist
        writer.writerows(responses)

    return render_template('result.html', responses=responses)

if __name__ == '__main__':
    app.run(debug=True)
