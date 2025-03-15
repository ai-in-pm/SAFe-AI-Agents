from .base_agent import BaseAgent

class SAFeCoach(BaseAgent):
    """SAFe Coach (Release Train Engineer) agent responsible for high-level facilitation and mentoring."""
    
    def __init__(self, name="SAFe Coach", model_provider="openai", model_name=None):
        super().__init__(name, "Release Train Engineer (RTE)", model_provider, model_name)
        self.pi_counter = 0
        self.metrics = {}
        # Portfolio-level elements (for Portfolio and Full SAFe)
        self.portfolio_backlog = []
        self.strategic_themes = []
        
    def _load_system_prompt(self):
        """Load the specialized system prompt for the SAFe Coach."""
        return f"""
        You are {self.name}, a Release Train Engineer (RTE) in a SAFe (Scaled Agile Framework) implementation. 
        Your responsibilities include:
        
        1. Facilitating Agile Release Train (ART) events and processes
        2. Supporting teams in their agile practices
        3. Ensuring alignment between teams and strategic objectives
        4. Guiding PI Planning, System Demos, and Inspect & Adapt workshops
        5. Removing impediments at the program level
        6. Mentoring Scrum Masters and teams on SAFe practices
        7. Tracking and reporting program-level metrics
        
        In Portfolio SAFe, you also:
        8. Manage portfolio-level decision-making
        9. Prioritize work using Lean Portfolio Management principles
        10. Align work with enterprise strategy and value streams
        
        In Full SAFe, you additionally:
        11. Coordinate across all levels (team, program, portfolio)
        12. Manage multiple ARTs and coordinate with Solution Trains
        13. Apply all seven core competencies for business agility
        
        Always respond according to SAFe principles and practices, using SAFe terminology correctly.
        Your goal is to maximize business value delivery while maintaining sustainable pace and quality.
        """
    
    def generate_response(self, user_input):
        """Generate a response based on the SAFe Coach's expertise."""
        messages = self._prepare_conversation_history()
        
        if self.model_provider == "openai":
            return self.call_openai(messages)
        elif self.model_provider == "anthropic":
            return self.call_anthropic(messages)
        elif self.model_provider == "google":
            return self.call_google(messages)
    
    def start_pi_planning(self, backlog, configuration="essential"):
        """Start PI Planning session.
        
        Args:
            backlog (list): The product backlog
            configuration (str): SAFe configuration (essential, portfolio, full)
            
        Returns:
            list: Selected PI scope
        """
        self.pi_counter += 1
        
        prompt = f"""
        As a SAFe Coach, conduct PI Planning for PI {self.pi_counter} using {configuration} SAFe configuration.
        
        The current backlog includes:
        {self._format_backlog(backlog)}
        
        Please:
        1. Share the vision and objectives for this PI
        2. Prioritize the backlog items
        3. Select an appropriate scope for the PI
        4. Identify key dependencies and risks
        5. Output a structured PI plan
        """
        
        self.conversation_history.append({"role": "user", "content": prompt})
        response = self.generate_response(prompt)
        self.conversation_history.append({"role": "assistant", "content": response})
        
        # For simulation purposes, just return a subset of the backlog as PI scope
        pi_scope = backlog[:min(len(backlog), 10)]  # Take up to 10 items
        
        return pi_scope, response
    
    def _format_backlog(self, backlog):
        """Format backlog items for display in prompts."""
        formatted = ""
        for i, item in enumerate(backlog):
            formatted += f"{i+1}. {item['name']} (Priority: {item['priority']}"
            if 'estimate' in item:
                formatted += f", Estimate: {item['estimate']}"
            formatted += ")\n"
        return formatted
    
    def handle_impediment(self, impediment, configuration="essential"):
        """Handle program-level impediments.
        
        Args:
            impediment (str): Description of the impediment
            configuration (str): SAFe configuration level
            
        Returns:
            str: Response with resolution strategy
        """
        prompt = f"""
        As a SAFe Coach operating in {configuration} SAFe configuration, address this impediment:
        
        Impediment: {impediment}
        
        How would you resolve this impediment at the program level? What actions would you take?
        """
        
        self.conversation_history.append({"role": "user", "content": prompt})
        response = self.generate_response(prompt)
        self.conversation_history.append({"role": "assistant", "content": response})
        
        return response
    
    def end_pi(self, achievements, metrics, configuration="essential"):
        """Conclude a Program Increment with an Inspect & Adapt workshop.
        
        Args:
            achievements (list): List of achievements/completed features
            metrics (dict): PI metrics including predictability
            configuration (str): SAFe configuration level
            
        Returns:
            str: Inspect & Adapt insights and improvements
        """
        prompt = f"""
        As a SAFe Coach operating in {configuration} SAFe configuration, conduct an Inspect & Adapt workshop 
        for PI {self.pi_counter} which has just concluded.
        
        Achievements:
        {', '.join(achievements)}
        
        Metrics:
        - Predictability: {metrics.get('predictability', 'N/A')}%
        - Delivered business value: {metrics.get('business_value', 'N/A')}
        - Team satisfaction: {metrics.get('team_satisfaction', 'N/A')}/10
        
        Please:
        1. Analyze the PI performance
        2. Identify key learnings and insights
        3. Propose specific improvements for the next PI
        4. Provide actionable recommendations for each level
        """
        
        self.conversation_history.append({"role": "user", "content": prompt})
        response = self.generate_response(prompt)
        self.conversation_history.append({"role": "assistant", "content": response})
        
        # Store metrics for this PI
        self.metrics[self.pi_counter] = metrics
        
        return response
    
    # Portfolio SAFe specific methods
    def align_with_strategy(self, strategic_themes, epics, configuration="portfolio"):
        """Align work with strategic themes (Portfolio SAFe).
        
        Args:
            strategic_themes (list): List of strategic themes
            epics (list): List of epics to align
            configuration (str): SAFe configuration level
            
        Returns:
            dict: Mapping of epics to strategic themes with priorities
        """
        if configuration not in ["portfolio", "full"]:
            return "This function requires Portfolio or Full SAFe configuration."
        
        prompt = f"""
        As a SAFe Coach operating in {configuration} SAFe configuration, align these epics with strategic themes:
        
        Strategic Themes:
        {', '.join(strategic_themes)}
        
        Epics:
        {', '.join([epic['name'] for epic in epics])}
        
        Please:
        1. Analyze how each epic supports the strategic themes
        2. Prioritize the epics based on strategic alignment
        3. Recommend which epics to fund and implement
        4. Explain your decision-making process using Lean Portfolio Management principles
        """
        
        self.conversation_history.append({"role": "user", "content": prompt})
        response = self.generate_response(prompt)
        self.conversation_history.append({"role": "assistant", "content": response})
        
        return response
    
    # Full SAFe specific methods
    def coordinate_solution_train(self, solution_name, arts, configuration="full"):
        """Coordinate a Solution Train across multiple ARTs (Full SAFe).
        
        Args:
            solution_name (str): Name of the solution
            arts (list): List of Agile Release Trains involved
            configuration (str): SAFe configuration level
            
        Returns:
            str: Coordination strategy
        """
        if configuration != "full":
            return "This function requires Full SAFe configuration."
        
        prompt = f"""
        As a SAFe Coach operating in Full SAFe configuration, coordinate this Solution Train:
        
        Solution: {solution_name}
        
        Agile Release Trains involved:
        {', '.join(arts)}
        
        Please:
        1. Outline the coordination strategy across these ARTs
        2. Describe how you would handle dependencies between ARTs
        3. Explain how you would ensure alignment with portfolio vision
        4. Suggest a cadence for Solution Train events
        5. Propose metrics to track solution-level progress
        """
        
        self.conversation_history.append({"role": "user", "content": prompt})
        response = self.generate_response(prompt)
        self.conversation_history.append({"role": "assistant", "content": response})
        
        return response
