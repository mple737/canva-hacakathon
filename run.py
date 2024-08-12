from flask import Flask, render_template, request, redirect, url_for, session, jsonify, flash
import requests
import os
import bcrypt

import model
app = Flask(__name__)

# Set up database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SECRET_KEY'] = os.urandom(24)

CANVA_API_KEY = os.getenv('CANVA_API_KEY')

@app.route('/')
def index():
    if 'user_id' in session:
        return render_template('index.html', auth='user_id' in session)
    return redirect(url_for('landing'))

@app.route('/landing')
def landing():
    return render_template('landing.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        return login_user()
    return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        return signup_user()
    return render_template('signup.html')

@app.route('/profile')
def profile():
    if 'user_id' in session:
        return render_template('profile.html')
    return redirect(url_for('landing'))

@app.route('/educational_resources')
def educational_resources():
    return render_template('educational_resources.html')

@app.route('/screen_reader_compatibility_preview')
def screen_reader_compatibility_preview():
    return render_template('screen_reader_compatibility.html')

@app.route('/accessibility_mode_toggle')
def accessibility_mode_toggle():
    return render_template('accessibility_mode_toggle.html')

@app.route('/emotion_palette_selector')
def emotion_palette():
    return render_template('emotion_palette_selector.html')

@app.route('/accessibility')
def real_time_accessibility_checker():
    return render_template('accessibility.html')

@app.route('/design_element_suggestions', methods=['GET', 'POST'])
def design_element_suggestions():
    if request.method == 'POST':
        prompt = request.form['prompt']
        # Integrate Canva API logic for design element suggestions here
        return jsonify({'suggestions': []})  # Replace with actual suggestions
    return render_template('design_element_suggestions.html')

@app.route('/generate_palette/<emotion>')
def generate_palette(emotion):
    # Using Canva API to generate a color palette based on the selected emotion
    url = f"https://api.canva.com/v1/colors/generate"
    headers = {
        'Authorization': f'Bearer {CANVA_API_KEY}',
        'Content-Type': 'application/json'
    }
    payload = {
        'emotion': emotion,
        'numPalettes': 3,  # Generate 3 palettes
        'colorsPerPalette': 5  # 5 colors per palette
    }

    try:
        response = requests.post(url, headers=headers, json=payload)
        response_data = response.json()
        palettes = []

        if response.status_code == 200 and 'palettes' in response_data:
            for palette in response_data['palettes']:
                palettes.append({'colors': palette['colors']})
        else:
            return jsonify({'error': 'Failed to generate palettes from Canva API.'})

        return jsonify({'palettes': palettes})
    except Exception as e:
        return jsonify({'error': str(e)})

@app.route('/check_accessibility', methods=['POST'])
def check_accessibility():
    url = request.form['url']
    # Use the Canva API or other services for accessibility checking
    if url:
        check_url = f"https://api.canva.com/v1/accessibility/check"
        headers = {
            'Authorization': f'Bearer {CANVA_API_KEY}',
            'Content-Type': 'application/json'
        }
        payload = {
            'url': url
        }

        try:
            response = requests.post(check_url, headers=headers, json=payload)
            response_data = response.json()

            if response.status_code == 200:
                errors = response_data.get('errors', [])
                return jsonify({'errors': errors})
            else:
                return jsonify({'errors': ['Error checking accessibility with Canva API.']})

        except Exception as e:
            return jsonify({'errors': [str(e)]})

    return jsonify({'errors': ['Invalid URL']})

@app.route('/toggle_accessibility', methods=['POST'])
def toggle_accessibility():
    # Logic for toggling accessibility mode
    return jsonify({'message': 'Accessibility mode toggled!'})

@app.route('/signup_user', methods=['POST'])
def signup_user():
    username = request.form['username']
    password = request.form['password']
    email = request.form['email']
    
    # Check if the username already exists
    existing_user = model.get_user_session(username=username)
    if existing_user:
        flash('Username already exists. Please choose another.', 'error')
        return redirect(url_for('signup'))

    credential = model.Credential(email=email, password=password)
    new_user = model.User(username=username, credential=credential)
    model.add_user_session(user=new_user)

    flash('Signup successful! You can now log in.', 'success')
    return redirect(url_for('login'))

@app.route('/login_user', methods=['POST'])
def login_user():
    username = request.form['username']
    password = request.form['password']
    
    user = model.get_user_session(username=username)

    if user and bcrypt.checkpw(password.encode('utf-8'), user.credential.hash_password):
        session['user_id'] = user.id
        return redirect(url_for('index'))

    flash('Invalid credentials. Please try again.', 'error')
    return redirect(url_for("login"))

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect(url_for('landing'))

if __name__ == '__main__':
    with app.app_context():
        model.init(app=app)
    app.run(debug=True)
