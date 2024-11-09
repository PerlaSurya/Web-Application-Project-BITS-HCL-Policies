import google.generativeai as genai
from flask import Flask, render_template, request, redirect, url_for, session
import os

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Replace with a strong secret key for session management

# Set up API key for Gemini securely
os.environ["API_KEY"] = 'Your Secret API Key'  # Your actual API key
genai.configure(api_key=os.environ["API_KEY"])

# Load policies.txt content
def load_policy_file():
    try:
        with open('policies.txt', 'r', encoding='utf-8') as file:
            policies_content = file.read()
        return policies_content
    except FileNotFoundError:
        return "Policy file not found."

policies_content = load_policy_file()  # Load the policies at startup

# Add links for checking updated documentation
updated_documentation_links = (
    "For the latest policies, please check the updated documentation at the following links:\n"
    "1. [Policy Hub](https://wf5.myhcl.com/policyhub/home/policy)\n"
    "2. [SharePoint Policy Hub](https://hclo365.sharepoint.com/sites/policyhub)\n\n"
)

@app.route('/')
def index():
    # Check if user is logged in
    if 'logged_in' not in session:
        return redirect(url_for('login'))
    return render_template('index.html', response='', question='')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        # Check credentials (hardcoded for simplicity)
        if username == 'admin' and password == 'admin':  # Replace with actual authentication logic
            session['logged_in'] = True
            return redirect(url_for('index'))
        else:
            return "Invalid credentials. Please try again."

    return render_template('login.html')

@app.route('/ask', methods=['POST'])
def ask_question():
    user_question = request.form['question']
    
    # Generate response from Gemini API with policies context
    model = genai.GenerativeModel(model_name='gemini-1.5-flash')  # Ensure the model name is correct
    response = model.generate_content(f"Here is the policy information:\n{policies_content}\n\nUser's Question: {user_question}\nAI Response:")
    
    # Extract text from the response
    ai_answer = response.text.strip()

    # Format response for clarity and add links to updated documentation
    formatted_response = f"**User:** {user_question}\n\n**AI:** {ai_answer}\n\n{updated_documentation_links}"

    return render_template('index.html', response=formatted_response, question=user_question)

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
