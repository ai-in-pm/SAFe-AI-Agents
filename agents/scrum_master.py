from .base_agent import BaseAgent

class ScrumMaster(BaseAgent):
    """Scrum Master agent responsible for team-level agile practices and sprint management."""
    
    def __init__(self, name="Scrum Master", model_provider="anthropic", model_name=None):
        super().__init__(name, "Scrum Master", model_provider, model_name)
        self.sprint_counter = 0
        self.current_pi = 0
        self.sprint_backlog = []
        self.impediments = []
        self.velocity_history = []
    
    def _load_system_prompt(self):
        """Load the specialized system prompt for the Scrum Master."""
        return f"""
        You are {self.name}, a Scrum Master in a SAFe (Scaled Agile Framework) implementation. 
        Your responsibilities include:
        
        1. Facilitating Scrum events (Sprint Planning, Daily Stand-ups, Sprint Review, Retrospective)
        2. Coaching the team on Agile and Scrum practices
        3. Removing impediments for the team
        4. Protecting the team from external interference
        5. Helping the team improve their processes
        6. Coordinating with the SAFe Coach (RTE) during program events
        7. Ensuring alignment between team goals and program objectives
        8. Tracking and reporting team-level metrics
        9. Participating in Scrum of Scrums as needed
        10. Supporting the team in creating high-quality increments
        
        Always respond according to SAFe and Scrum principles and practices, using proper terminology.
        Your goal is to help the team deliver value while continuously improving their process.
        """
    
    def generate_response(self, user_input):
        """Generate a response based on the Scrum Master's expertise."""
        messages = self._prepare_conversation_history()
        
        if self.model_provider == "openai":
            return self.call_openai(messages)
        elif self.model_provider == "anthropic":
            return self.call_anthropic(messages)
        elif self.model_provider == "google":
            return self.call_google(messages)
    
    def start_sprint(self, pi_number, sprint_number, pi_scope):
        """Start a new sprint.
        
        Args:
            pi_number (int): Program Increment number
            sprint_number (int): Sprint number within the PI
            pi_scope (list): Available PI scope to plan from
            
        Returns:
            tuple: Sprint backlog and planning response
        """
        self.current_pi = pi_number
        self.sprint_counter = sprint_number
        
        # Calculate team velocity based on history (or use default for first sprint)
        velocity = self._calculate_velocity()
        
        prompt = f"""
        As a Scrum Master, facilitate Sprint Planning for Sprint {sprint_number} of PI {pi_number}.
        
        Available items from PI scope:
        {self._format_backlog(pi_scope)}
        
        Team's average velocity: {velocity} story points
        
        Please:
        1. Select appropriate items for the sprint backlog based on velocity
        2. Break down items into tasks where needed
        3. Identify any risks or impediments for this sprint
        4. Outline the sprint goal
        5. Present a clear sprint plan
        """
        
        self.conversation_history.append({"role": "user", "content": prompt})
        response = self.generate_response(prompt)
        self.conversation_history.append({"role": "assistant", "content": response})
        
        # For simulation, select items from PI scope based on velocity
        total_points = 0
        sprint_backlog = []
        
        for item in pi_scope:
            if 'estimate' not in item:
                item['estimate'] = 5  # Default estimate if not provided
                
            if total_points + item['estimate'] <= velocity:
                sprint_backlog.append(item)
                total_points += item['estimate']
                
            if len(sprint_backlog) >= velocity / 3:  # Limit number of items
                break
        
        self.sprint_backlog = sprint_backlog
        
        return sprint_backlog, response
    
    def daily_standup(self, day, team_updates):
        """Conduct a daily standup meeting.
        
        Args:
            day (int): Day of the sprint
            team_updates (list): Updates from team members
            
        Returns:
            tuple: Updated sprint backlog and standup summary
        """
        prompt = f"""
        As a Scrum Master, facilitate the Daily Standup for day {day} of Sprint {self.sprint_counter} (PI {self.current_pi}).
        
        Team updates:
        {self._format_updates(team_updates)}
        
        Current impediments: {', '.join(self.impediments) if self.impediments else 'None'}
        
        Please:
        1. Summarize the team's progress
        2. Identify any new impediments that need addressing
        3. Determine if any adjustments to the sprint plan are needed
        4. Provide guidance to keep the team on track
        """
        
        self.conversation_history.append({"role": "user", "content": prompt})
        response = self.generate_response(prompt)
        self.conversation_history.append({"role": "assistant", "content": response})
        
        # Extract any new impediments from updates
        for update in team_updates:
            if 'impediment' in update and update['impediment'] and update['impediment'] not in self.impediments:
                self.impediments.append(update['impediment'])
        
        return self.sprint_backlog, response
    
    def resolve_impediment(self, impediment):
        """Resolve a team impediment.
        
        Args:
            impediment (str): The impediment to resolve
            
        Returns:
            str: Resolution strategy
        """
        prompt = f"""
        As a Scrum Master, address this impediment for your team:
        
        Impediment: {impediment}
        
        Please:
        1. Analyze the impact of this impediment on the team
        2. Propose a specific strategy to resolve it
        3. Identify any stakeholders who need to be involved
        4. Suggest preventive measures for the future
        """
        
        self.conversation_history.append({"role": "user", "content": prompt})
        response = self.generate_response(prompt)
        self.conversation_history.append({"role": "assistant", "content": response})
        
        # Remove the impediment if it was in the list
        if impediment in self.impediments:
            self.impediments.remove(impediment)
        
        return response
    
    def end_sprint(self, completed_items):
        """Conclude a sprint with review and retrospective.
        
        Args:
            completed_items (list): Items completed during the sprint
            
        Returns:
            tuple: Sprint metrics and retrospective insights
        """
        # Calculate metrics
        planned = len(self.sprint_backlog)
        completed = len(completed_items)
        planned_points = sum(item.get('estimate', 3) for item in self.sprint_backlog)
        completed_points = sum(item.get('estimate', 3) for item in completed_items)
        
        # Update velocity history
        self.velocity_history.append(completed_points)
        
        metrics = {
            "planned_items": planned,
            "completed_items": completed,
            "planned_points": planned_points,
            "completed_points": completed_points,
            "completion_rate": completed / planned * 100 if planned > 0 else 100,
            "velocity": completed_points
        }
        
        prompt = f"""
        As a Scrum Master, conduct a Sprint Review and Retrospective for Sprint {self.sprint_counter} of PI {self.current_pi}.
        
        Sprint metrics:
        - Planned items: {planned}
        - Completed items: {completed}
        - Planned story points: {planned_points}
        - Completed story points: {completed_points}
        - Completion rate: {metrics['completion_rate']:.1f}%
        - Sprint velocity: {completed_points}
        
        Completed items:
        {self._format_backlog(completed_items)}
        
        Impediments encountered: {', '.join(self.impediments) if self.impediments else 'None'}
        
        Please:
        1. Summarize the sprint achievements
        2. Identify what went well and what could be improved
        3. Propose specific actions for the next sprint
        4. Provide insights on team performance trends
        """
        
        self.conversation_history.append({"role": "user", "content": prompt})
        response = self.generate_response(prompt)
        self.conversation_history.append({"role": "assistant", "content": response})
        
        # Reset sprint backlog for next sprint
        self.sprint_backlog = []
        
        return metrics, response
    
    def _calculate_velocity(self):
        """Calculate the team's velocity based on history."""
        if not self.velocity_history:
            return 20  # Default starting velocity
        
        # Use average of last 3 sprints, or fewer if not enough history
        recent_velocities = self.velocity_history[-3:]
        return sum(recent_velocities) / len(recent_velocities)
    
    def _format_backlog(self, backlog):
        """Format backlog items for display in prompts."""
        formatted = ""
        for i, item in enumerate(backlog):
            formatted += f"{i+1}. {item['name']} (Priority: {item['priority']}"
            if 'estimate' in item:
                formatted += f", Estimate: {item['estimate']}"
            formatted += ")\n"
        return formatted
    
    def _format_updates(self, updates):
        """Format team updates for display in prompts."""
        formatted = ""
        for i, update in enumerate(updates):
            formatted += f"{update['member']}: {update['status']}\n"
            if 'impediment' in update and update['impediment']:
                formatted += f"  Impediment: {update['impediment']}\n"
        return formatted
    
    def handle_change_request(self, change_request, current_sprint_progress):
        """Handle a mid-sprint change request.
        
        Args:
            change_request (dict): Details of the change request
            current_sprint_progress (float): Percentage of sprint completed
            
        Returns:
            tuple: Decision and explanation
        """
        prompt = f"""
        As a Scrum Master, a change request has come in during Sprint {self.sprint_counter} of PI {self.current_pi}:
        
        Change request: {change_request['description']}
        Priority: {change_request['priority']}/10
        Size estimate: {change_request.get('estimate', 'Unknown')} story points
        
        Current sprint is {current_sprint_progress:.0f}% complete.
        Current sprint backlog: {self._format_backlog(self.sprint_backlog)}
        Current impediments: {', '.join(self.impediments) if self.impediments else 'None'}
        
        Please:
        1. Assess the impact of this change on the sprint
        2. Decide whether to accept, defer, or reject the change
        3. If accepting, explain what adjustments would be needed
        4. Provide a clear rationale for your decision based on Agile principles
        """
        
        self.conversation_history.append({"role": "user", "content": prompt})
        response = self.generate_response(prompt)
        self.conversation_history.append({"role": "assistant", "content": response})
        
        return response
