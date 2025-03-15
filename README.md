# SAFe AI Agents Simulation

This project simulates the implementation of the Scaled Agile Framework (SAFe) using AI agents that represent key roles in the framework. The simulation demonstrates how SAFe principles and practices are applied in real-time to manage Agile software development at scale.

## Features

- **Three AI Agents**: SAFe Coach, Scrum Master, and Developer, each with specific roles and responsibilities
- **Multiple SAFe Configurations**: Choose between Essential, Portfolio, and Full SAFe implementations
- **Complete SAFe Ceremonies**: Including PI Planning, Daily Stand-ups, Sprint Reviews, and Inspect & Adapt workshops
- **Real-time Interaction**: All agents interact based on SAFe principles and respond dynamically to changes
- **Web Interface**: User-friendly interface to control the simulation and view agent responses

## Agents

### SAFe Coach
- Facilitates ART (Agile Release Train) events
- Manages portfolio-level decisions
- Handles strategic alignment
- Guides teams on SAFe implementation

### Scrum Master
- Manages team-level Agile practices
- Facilitates Scrum ceremonies
- Resolves impediments
- Manages sprint execution

### Developer
- Implements user stories
- Estimates work
- Provides technical expertise
- Ensures quality delivery

## Installation

1. Clone the repository
2. Create a virtual environment: `python -m venv venv`
3. Activate the virtual environment:
   - Windows: `venv\Scripts\activate`
   - macOS/Linux: `source venv/bin/activate`
4. Install dependencies: `pip install -r requirements.txt`
5. Create a `.env` file with the following API keys:
   ```
   OPENAI_API_KEY=your_openai_api_key
   ANTHROPIC_API_KEY=your_anthropic_api_key
   GOOGLE_API_KEY=your_google_api_key
   ```

## Running the Simulation

1. Ensure your virtual environment is activated
2. Run the web application: `python app.py`
3. Open your browser and navigate to: `http://localhost:5000`
4. Follow the on-screen instructions to set up and run the simulation

## Usage Flow

1. **Initialize Simulation**: Choose the SAFe configuration and project name
2. **Start a Program Increment (PI)**: The SAFe Coach will conduct PI Planning
3. **Start Sprints**: The Scrum Master will manage sprint planning
4. **Run Daily Stand-ups**: Team members report progress and impediments
5. **End Sprint with Review/Retro**: Review completed work and plan improvements
6. **End PI with System Demo**: Demonstrate completed work and conduct Inspect & Adapt

## Project Structure

- `agents/` - Contains all agent implementations
  - `base_agent.py` - Base class for all agents
  - `safe_coach.py` - SAFe Coach implementation
  - `scrum_master.py` - Scrum Master implementation
  - `developer.py` - Developer implementation
- `config.py` - Configuration settings
- `safe_simulation.py` - Simulation engine that coordinates agents
- `app.py` - Flask web application
- `templates/` - HTML templates
- `static/` - CSS and JavaScript files

## Output
![screencapture-127-0-0-1-56313-2025-03-15-15_49_08](https://github.com/user-attachments/assets/00f12472-e794-40ce-ac06-c01f577e831d)
![screencapture-127-0-0-1-56313-2025-03-15-15_49_54](https://github.com/user-attachments/assets/363e4194-792b-4d83-bbb0-ead26b5c4cd8)
![screencapture-127-0-0-1-56313-2025-03-15-15_50_14](https://github.com/user-attachments/assets/e708c2b4-b1f9-4eff-8924-d901f2c654ee)


## Requirements

See `requirements.txt` for a complete list of dependencies.

## License

MIT
