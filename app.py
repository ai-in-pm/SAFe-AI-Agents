import os
import sys
import json
import logging
import datetime
import markdown
from dotenv import load_dotenv
from flask import Flask, render_template, request, jsonify, session, send_file
from flask_socketio import SocketIO
from markdown import markdown

from safe_simulation import SAFeSimulation, create_sample_backlog

# Load environment variables
load_dotenv()

# Initialize Flask app and SocketIO
app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(24).hex()  # Random secret key for sessions
socketio = SocketIO(app)

# Global simulation instance
simulation = None

@app.route('/')
def index():
    """Render the main page."""
    return render_template('index.html')

@app.route('/api/initialize', methods=['POST'])
def initialize_simulation():
    """Initialize a new SAFe simulation."""
    global simulation
    
    data = request.json
    config = data.get('configuration', 'essential')
    project_name = data.get('project_name', 'Demo Project')
    
    # Create backlog (use sample or custom if provided)
    if data.get('use_sample_backlog', True):
        backlog = create_sample_backlog()
    else:
        backlog = data.get('custom_backlog', [])
    
    # Create strategic themes for Portfolio/Full SAFe configurations
    strategic_themes = None
    if config in ['portfolio', 'full']:
        strategic_themes = data.get('strategic_themes', [
            "Digital Transformation",
            "Customer Experience Enhancement",
            "Operational Excellence",
            "Market Expansion"
        ])
    
    # Initialize the simulation
    simulation = SAFeSimulation(config)
    simulation.setup_project(project_name, backlog, strategic_themes)
    
    return jsonify({
        'status': 'success',
        'message': f'Simulation initialized with {config} configuration',
        'state': simulation.get_simulation_state()
    })

@app.route('/api/start_pi', methods=['POST'])
def start_pi():
    """Start a new Program Increment."""
    if not simulation:
        return jsonify({'status': 'error', 'message': 'Simulation not initialized'}), 400
    
    result = simulation.start_pi()
    
    # Convert markdown to HTML for display
    if 'planning_details' in result:
        result['planning_details_html'] = markdown(result['planning_details'])
    
    # Emit event to connected clients
    socketio.emit('pi_started', {
        'pi_number': result['pi_number'],
        'state': simulation.get_simulation_state()
    })
    
    return jsonify({
        'status': 'success',
        'data': result,
        'state': simulation.get_simulation_state()
    })

@app.route('/api/start_sprint', methods=['POST'])
def start_sprint():
    """Start a new sprint within the current PI."""
    if not simulation:
        return jsonify({'status': 'error', 'message': 'Simulation not initialized'}), 400
    
    if simulation.current_pi == 0:
        return jsonify({'status': 'error', 'message': 'Must start a PI first'}), 400
    
    result = simulation.start_sprint()
    
    # Convert markdown to HTML for display
    if 'planning_details' in result:
        result['planning_details_html'] = markdown(result['planning_details'])
    
    # Emit event to connected clients
    socketio.emit('sprint_started', {
        'sprint_number': result['sprint_number'],
        'pi_number': result['pi_number'],
        'state': simulation.get_simulation_state()
    })
    
    return jsonify({
        'status': 'success',
        'data': result,
        'state': simulation.get_simulation_state()
    })

@app.route('/api/daily_standup', methods=['POST'])
def daily_standup():
    """Run a daily standup meeting."""
    if not simulation:
        return jsonify({'status': 'error', 'message': 'Simulation not initialized'}), 400
    
    if simulation.current_sprint == 0:
        return jsonify({'status': 'error', 'message': 'Must start a sprint first'}), 400
    
    result = simulation.run_daily_standup()
    
    # Convert markdown to HTML for display
    if 'standup_summary' in result:
        result['standup_summary_html'] = markdown(result['standup_summary'])
    
    # Emit event to connected clients
    socketio.emit('standup_completed', {
        'day': result['day'],
        'sprint': result['sprint'],
        'pi': result['pi'],
        'state': simulation.get_simulation_state()
    })
    
    return jsonify({
        'status': 'success',
        'data': result,
        'state': simulation.get_simulation_state()
    })

@app.route('/api/end_sprint', methods=['POST'])
def end_sprint():
    """End the current sprint."""
    if not simulation:
        return jsonify({'status': 'error', 'message': 'Simulation not initialized'}), 400
    
    if simulation.current_sprint == 0:
        return jsonify({'status': 'error', 'message': 'No active sprint to end'}), 400
    
    result = simulation.end_sprint()
    
    # Convert markdown to HTML for display
    if 'retrospective' in result:
        result['retrospective_html'] = markdown(result['retrospective'])
    
    # Emit event to connected clients
    socketio.emit('sprint_ended', {
        'sprint_number': result['sprint_number'],
        'completion_rate': result['completion_rate'],
        'state': simulation.get_simulation_state()
    })
    
    return jsonify({
        'status': 'success',
        'data': result,
        'state': simulation.get_simulation_state()
    })

@app.route('/api/end_pi', methods=['POST'])
def end_pi():
    """End the current Program Increment."""
    if not simulation:
        return jsonify({'status': 'error', 'message': 'Simulation not initialized'}), 400
    
    if simulation.current_pi == 0:
        return jsonify({'status': 'error', 'message': 'No active PI to end'}), 400
    
    result = simulation.end_pi()
    
    # Convert markdown to HTML for display
    if 'inspect_and_adapt' in result:
        result['inspect_and_adapt_html'] = markdown(result['inspect_and_adapt'])
    
    # Emit event to connected clients
    socketio.emit('pi_ended', {
        'pi_number': result['pi_number'],
        'predictability': result['metrics']['predictability'],
        'state': simulation.get_simulation_state()
    })
    
    return jsonify({
        'status': 'success',
        'data': result,
        'state': simulation.get_simulation_state()
    })

@app.route('/api/change_request', methods=['POST'])
def handle_change_request():
    """Process a change request."""
    if not simulation:
        return jsonify({'status': 'error', 'message': 'Simulation not initialized'}), 400
    
    data = request.json
    change_request = {
        'description': data.get('description', 'Unnamed change request'),
        'priority': data.get('priority', 5),
        'urgency': data.get('urgency', 'medium'),
        'estimate': data.get('estimate', 5),
        'strategic': data.get('strategic', False)
    }
    
    result = simulation.handle_change_request(change_request)
    
    # Convert markdown to HTML for display
    if 'response' in result:
        result['response_html'] = markdown(result['response'])
    if 'sm_response' in result:
        result['sm_response_html'] = markdown(result['sm_response'])
    if 'dev_response' in result:
        result['dev_response_html'] = markdown(result['dev_response'])
    
    # Emit event to connected clients
    socketio.emit('change_processed', {
        'change': change_request['description'],
        'accepted': result.get('accepted', False),
        'handler': result.get('handler', 'Unknown'),
        'state': simulation.get_simulation_state()
    })
    
    return jsonify({
        'status': 'success',
        'data': result,
        'state': simulation.get_simulation_state()
    })

@app.route('/api/technical_guidance', methods=['POST'])
def get_technical_guidance():
    """Get technical guidance from the Developer agent."""
    if not simulation:
        return jsonify({'status': 'error', 'message': 'Simulation not initialized'}), 400
    
    data = request.json
    topic = data.get('topic', 'general technical approach')
    
    response = simulation.get_technical_guidance(topic)
    
    return jsonify({
        'status': 'success',
        'data': {
            'topic': topic,
            'guidance': response,
            'guidance_html': markdown(response)
        },
        'state': simulation.get_simulation_state()
    })

@app.route('/api/events', methods=['GET'])
def get_events():
    """Get the simulation event log."""
    if not simulation:
        return jsonify({'status': 'error', 'message': 'Simulation not initialized'}), 400
    
    limit = request.args.get('limit', type=int)
    events = simulation.get_events_log(limit)
    
    return jsonify({
        'status': 'success',
        'data': events
    })

@app.route('/api/communications', methods=['GET'])
def get_communications():
    """Get the simulation communication log."""
    if not simulation:
        return jsonify({'status': 'error', 'message': 'Simulation not initialized'}), 400
    
    limit = request.args.get('limit', type=int)
    communications = simulation.get_communication_log(limit)
    
    # Convert markdown to HTML for display
    for comm in communications:
        comm['message_html'] = markdown(comm['message'])
    
    return jsonify({
        'status': 'success',
        'data': communications
    })

@app.route('/api/state', methods=['GET'])
def get_state():
    """Get the current state of the simulation."""
    if not simulation:
        return jsonify({'status': 'error', 'message': 'Simulation not initialized'}), 400
    
    return jsonify({
        'status': 'success',
        'data': simulation.get_simulation_state()
    })

@app.route('/api/ask_agent', methods=['POST'])
def ask_agent():
    """Ask a specific agent a question."""
    if not simulation:
        return jsonify({'status': 'error', 'message': 'Simulation not initialized'}), 400
    
    data = request.json
    agent_type = data.get('agent_type')
    question = data.get('question')
    
    if not agent_type or not question:
        return jsonify({'status': 'error', 'message': 'Missing agent_type or question'}), 400
    
    # Get the right agent based on type
    agent = None
    if agent_type == 'safe_coach':
        agent = simulation.safe_coach
    elif agent_type == 'scrum_master':
        agent = simulation.scrum_master
    elif agent_type == 'developer':
        agent = simulation.developer
    else:
        return jsonify({'status': 'error', 'message': f'Unknown agent type: {agent_type}'}), 400
    
    # Generate the response from the agent
    try:
        response = agent.generate_response(question)
        
        # Convert markdown to HTML for display
        response_html = markdown(response)
        
        # Add the communication to the simulation log
        simulation.add_communication('User', agent_type, question)
        simulation.add_communication(agent_type, 'User', response)
        
        # Log the interaction as an event
        simulation.add_event(f'Question to {agent_type}', question)
        
        return jsonify({
            'status': 'success',
            'response': response,
            'response_html': response_html,
            'timestamp': simulation.current_time.strftime('%Y-%m-%d %H:%M:%S'),
            'state': simulation.get_simulation_state()
        })
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/demonstrate_safe_config', methods=['POST'])
def demonstrate_safe_configuration():
    """Demonstrate a specific SAFe configuration with step-by-step explanations from all agents."""
    if not simulation:
        return jsonify({'status': 'error', 'message': 'Simulation not initialized'}), 400
    
    data = request.json
    config_type = data.get('config_type')  # 'big_picture', 'core_competencies', 'essential', 'large_solution', 'portfolio', 'full'
    
    if not config_type:
        return jsonify({'status': 'error', 'message': 'Missing config_type'}), 400
    
    # Get all three agents
    safe_coach = simulation.safe_coach
    scrum_master = simulation.scrum_master
    developer = simulation.developer
    
    # Define the configuration-specific questions
    config_questions = {
        'big_picture': {
            'safe_coach': 'Explain the SAFe Big Picture configuration. What are the key components and how do they work together?',
            'scrum_master': 'How would you use the SAFe Big Picture to help teams understand their place in the organization?',
            'developer': 'From a developer perspective, what aspects of the SAFe Big Picture are most relevant to your daily work?'
        },
        'core_competencies': {
            'safe_coach': 'Explain the Core Competencies in SAFe and why they are important for business agility.',
            'scrum_master': 'How would you help teams develop these core competencies in their daily practices?',
            'developer': 'Which core competencies directly impact development teams and how can developers contribute to them?'
        },
        'essential': {
            'safe_coach': 'Explain the Essential SAFe configuration. What are the minimal elements needed for SAFe implementation?',
            'scrum_master': 'How would you implement Essential SAFe practices in a team that is new to SAFe?',
            'developer': 'What changes would developers experience when moving from traditional development to Essential SAFe?'
        },
        'large_solution': {
            'safe_coach': 'Explain the Large Solution SAFe configuration. How does it extend Essential SAFe?',
            'scrum_master': 'What additional ceremonies and practices would you introduce when scaling to Large Solution SAFe?',
            'developer': 'How does development work change when moving from Essential to Large Solution SAFe?'
        },
        'portfolio': {
            'safe_coach': 'Explain the Portfolio SAFe configuration. How does it help align strategy with execution?',
            'scrum_master': 'How would you explain the connection between portfolio-level decisions and team-level work?',
            'developer': 'How do portfolio-level concerns like strategic themes affect developers in their daily work?'
        },
        'full': {
            'safe_coach': 'Explain the Full SAFe configuration. What challenges does it address for the largest enterprises?',
            'scrum_master': 'What are the key challenges when implementing Full SAFe and how would you address them?',
            'developer': 'How do developers maintain agility and avoid bureaucracy in a Full SAFe implementation?'
        }
    }
    
    try:
        # Generate responses from each agent
        coach_response = safe_coach.generate_chain_of_thought_response(config_questions[config_type]['safe_coach'])
        scrum_master_response = scrum_master.generate_chain_of_thought_response(config_questions[config_type]['scrum_master'])
        developer_response = developer.generate_chain_of_thought_response(config_questions[config_type]['developer'])
        
        # Convert markdown to HTML for display
        coach_thought_html = [markdown.markdown(step) for step in coach_response['thought_process']]
        coach_conclusion_html = markdown.markdown(coach_response['conclusion'])
        
        sm_thought_html = [markdown.markdown(step) for step in scrum_master_response['thought_process']]
        sm_conclusion_html = markdown.markdown(scrum_master_response['conclusion'])
        
        dev_thought_html = [markdown.markdown(step) for step in developer_response['thought_process']]
        dev_conclusion_html = markdown.markdown(developer_response['conclusion'])
        
        # Log the interaction
        simulation.add_event(f"SAFe {config_type.capitalize()} Configuration Demonstration", "All agents provided explanations")
        
        return jsonify({
            'status': 'success',
            'config_type': config_type,
            'coach': {
                'thought_process': coach_response['thought_process'],
                'thought_process_html': coach_thought_html,
                'conclusion': coach_response['conclusion'],
                'conclusion_html': coach_conclusion_html
            },
            'scrum_master': {
                'thought_process': scrum_master_response['thought_process'],
                'thought_process_html': sm_thought_html,
                'conclusion': scrum_master_response['conclusion'],
                'conclusion_html': sm_conclusion_html
            },
            'developer': {
                'thought_process': developer_response['thought_process'],
                'thought_process_html': dev_thought_html,
                'conclusion': developer_response['conclusion'],
                'conclusion_html': dev_conclusion_html
            },
            'timestamp': simulation.current_time.strftime('%Y-%m-%d %H:%M:%S'),
            'state': simulation.get_simulation_state()
        })
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/demonstrate_cot', methods=['POST'])
def demonstrate_cot():
    """Demonstrate Chain of Thought reasoning for a specific agent."""
    print("\n[DEBUG] /api/demonstrate_cot endpoint called")
    if not simulation:
        print("[DEBUG] Error: Simulation not initialized")
        return jsonify({'status': 'error', 'message': 'Simulation not initialized'}), 400
    
    data = request.json
    print(f"[DEBUG] Request data: {data}")
    agent_type = data.get('agent_type')  # 'safe_coach', 'scrum_master', or 'developer'
    question = data.get('question')
    
    if not agent_type or not question:
        print(f"[DEBUG] Error: Missing agent_type or question. agent_type: {agent_type}, question: {question}")
        return jsonify({'status': 'error', 'message': 'Missing agent_type or question'}), 400
    
    # Get the right agent based on type
    agent = None
    if agent_type == 'safe_coach':
        agent = simulation.safe_coach
    elif agent_type == 'scrum_master':
        agent = simulation.scrum_master
    elif agent_type == 'developer':
        agent = simulation.developer
    else:
        print(f"[DEBUG] Error: Unknown agent type: {agent_type}")
        return jsonify({'status': 'error', 'message': f'Unknown agent type: {agent_type}'}), 400
    
    print(f"[DEBUG] Using agent: {agent_type}, Question: {question}")
    
    # Generate the chain of thought response from the agent
    try:
        print("[DEBUG] Calling generate_chain_of_thought_response")
        cot_response = agent.generate_chain_of_thought_response(question)
        print(f"[DEBUG] Response received: {str(cot_response)[:200]}...")
        
        # Convert markdown to HTML for display
        print("[DEBUG] Converting to HTML")
        thought_process_html = [markdown.markdown(step) for step in cot_response['thought_process']]
        conclusion_html = markdown.markdown(cot_response['conclusion'])
        
        # Add the communication to the simulation log
        simulation.add_communication('User', agent.role, question)
        simulation.add_communication(agent.role, 'User', cot_response['conclusion'])
        
        # Log the interaction as an event
        simulation.add_event(f"CoT Question to {agent.role}", question)
        
        response_data = {
            'status': 'success',
            'agent_type': agent_type,
            'question': question,
            'thought_process': cot_response['thought_process'],
            'thought_process_html': thought_process_html,
            'conclusion': cot_response['conclusion'],
            'conclusion_html': conclusion_html,
            'timestamp': simulation.current_time.strftime('%Y-%m-%d %H:%M:%S'),
            'state': simulation.get_simulation_state()
        }
        print("[DEBUG] Sending successful response")
        return jsonify(response_data)
    except Exception as e:
        import traceback
        print("[DEBUG] Error in Chain of Thought generation:")
        traceback.print_exc()
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/upload_safe_config_image/<config_type>', methods=['POST'])
def upload_safe_config_image(config_type):
    """Upload a SAFe configuration image."""
    if not request.files or 'image' not in request.files:
        return jsonify({'status': 'error', 'message': 'No image provided'}), 400
        
    file = request.files['image']
    if file.filename == '':
        return jsonify({'status': 'error', 'message': 'No image selected'}), 400
        
    if file:
        # Validate config_type
        valid_configs = ['big_picture', 'core_competencies', 'essential', 'large_solution', 'portfolio', 'full']
        if config_type not in valid_configs:
            return jsonify({'status': 'error', 'message': 'Invalid configuration type'}), 400
            
        # Ensure directory exists
        config_dir = os.path.join(app.static_folder, 'images', 'safe_configurations')
        os.makedirs(config_dir, exist_ok=True)
        
        # Save file
        filename = f"{config_type}.jpg"
        file_path = os.path.join(config_dir, filename)
        file.save(file_path)
        
        return jsonify({
            'status': 'success', 
            'message': 'Image uploaded successfully',
            'path': f"/static/images/safe_configurations/{filename}"
        })
        
    return jsonify({'status': 'error', 'message': 'Failed to upload image'}), 500

@app.route('/api/safe_config_image/<config_type>')
def get_safe_config_image(config_type):
    """Return a SAFe configuration image."""
    # Validate config_type
    valid_configs = ['big_picture', 'core_competencies', 'essential', 'large_solution', 'portfolio', 'full']
    if config_type not in valid_configs:
        return jsonify({'status': 'error', 'message': 'Invalid configuration type'}), 400
    
    # Map the config_type to a specific file number (based on the order of images provided)
    config_map = {
        'big_picture': 1,      # Image 1
        'core_competencies': 2, # Image 2
        'essential': 3,         # Image 3
        'large_solution': 4,    # Image 4
        'portfolio': 5,         # Image 5
        'full': 6               # Image 6
    }
    
    img_num = config_map[config_type]
    img_path = os.path.join(app.static_folder, f"images/safe_config_{img_num}.jpg")
    
    # Return the image if it exists, otherwise return a default image
    if os.path.exists(img_path):
        return send_file(img_path, mimetype='image/jpeg')
    else:
        # Return a default image from the static folder
        default_img = os.path.join(app.static_folder, "images/default_safe_config.jpg")
        return send_file(default_img, mimetype='image/jpeg')

@socketio.on('connect')
def handle_connect():
    """Handle client connection to WebSocket."""
    if simulation:
        socketio.emit('simulation_state', {
            'state': simulation.get_simulation_state()
        })

if __name__ == '__main__':
    # Create templates directory if it doesn't exist
    if not os.path.exists('templates'):
        os.makedirs('templates')
        
    # Create static directory if it doesn't exist
    if not os.path.exists('static'):
        os.makedirs('static')
        
    socketio.run(app, debug=True, host='0.0.0.0', port=5000)
