from .base_agent import BaseAgent

class Developer(BaseAgent):
    """Developer agent responsible for implementing work and providing technical expertise."""
    
    def __init__(self, name="Developer", model_provider="google", model_name=None):
        super().__init__(name, "Developer", model_provider, model_name)
        self.current_tasks = []
        self.completed_tasks = []
        self.technical_debt_items = []
        self.skills = ["coding", "testing", "design", "refactoring"]
    
    def _load_system_prompt(self):
        """Load the specialized system prompt for the Developer."""
        return f"""
        You are {self.name}, a Developer in a SAFe (Scaled Agile Framework) implementation. 
        Your responsibilities include:
        
        1. Estimating user stories and tasks
        2. Implementing user stories with built-in quality
        3. Participating in team events (planning, daily stand-ups, reviews, retrospectives)
        4. Collaborating with other team members
        5. Maintaining technical excellence and addressing technical debt
        6. Testing and integrating your work continuously
        7. Supporting system demos and PI planning
        8. Providing technical insights on feasibility and implementation approaches
        9. Ensuring your work meets the Definition of Done
        10. Contributing to continuous improvement
        
        Always respond according to SAFe principles and engineering best practices.
        Your goal is to deliver high-quality, working software that meets customer needs.
        You should balance delivery of new features with maintaining technical health.
        """
    
    def generate_response(self, user_input):
        """Generate a response based on the Developer's expertise."""
        messages = self._prepare_conversation_history()
        
        if self.model_provider == "openai":
            return self.call_openai(messages)
        elif self.model_provider == "anthropic":
            return self.call_anthropic(messages)
        elif self.model_provider == "google":
            return self.call_google(messages)
    
    def estimate_story(self, story, team_skills=None):
        """Estimate a user story.
        
        Args:
            story (dict): The user story to estimate
            team_skills (list, optional): Skills available in the team
            
        Returns:
            tuple: Estimated points and explanation
        """
        team_skills = team_skills or self.skills
        
        prompt = f"""
        As a Developer, estimate this user story:
        
        Story: {story['name']}
        Description: {story.get('description', 'No detailed description provided')}
        Acceptance Criteria: {story.get('acceptance_criteria', ['None provided'])}
        
        Team skills: {', '.join(team_skills)}
        Technical debt considerations: {', '.join(self.technical_debt_items) if self.technical_debt_items else 'None noted'}
        
        Please:
        1. Analyze the complexity of this story
        2. Consider technical risks and dependencies
        3. Provide a story point estimate (1, 2, 3, 5, 8, 13, 20) using relative sizing
        4. Explain your reasoning for this estimate
        5. Identify any clarifications needed
        """
        
        self.conversation_history.append({"role": "user", "content": prompt})
        response = self.generate_response(prompt)
        self.conversation_history.append({"role": "assistant", "content": response})
        
        # For simulation purposes, extract a numeric estimate from the response or use default
        estimate = 5  # Default estimate
        
        # Simple extraction of estimate from response (could be enhanced)
        if "1 point" in response or "1 story point" in response:
            estimate = 1
        elif "2 point" in response or "2 story point" in response:
            estimate = 2
        elif "3 point" in response or "3 story point" in response:
            estimate = 3
        elif "5 point" in response or "5 story point" in response:
            estimate = 5
        elif "8 point" in response or "8 story point" in response:
            estimate = 8
        elif "13 point" in response or "13 story point" in response:
            estimate = 13
        elif "20 point" in response or "20 story point" in response:
            estimate = 20
        
        return estimate, response
    
    def start_work(self, task):
        """Start working on a task.
        
        Args:
            task (dict): The task to work on
            
        Returns:
            str: Implementation approach
        """
        prompt = f"""
        As a Developer, you're starting work on this task:
        
        Task: {task['name']}
        Description: {task.get('description', 'No detailed description provided')}
        Acceptance Criteria: {task.get('acceptance_criteria', ['None provided'])}
        
        Please:
        1. Outline your implementation approach
        2. Identify the key components or classes needed
        3. Highlight any potential technical challenges
        4. Describe how you'll ensure quality (testing approach)
        5. Estimate how long this will take to implement
        """
        
        self.conversation_history.append({"role": "user", "content": prompt})
        response = self.generate_response(prompt)
        self.conversation_history.append({"role": "assistant", "content": response})
        
        # Add task to current tasks
        if task not in self.current_tasks:
            self.current_tasks.append(task)
        
        return response
    
    def report_progress(self):
        """Report progress on current tasks for daily stand-up.
        
        Returns:
            tuple: Progress report and any impediments
        """
        if not self.current_tasks:
            return "No tasks currently in progress.", None
        
        task_list = ', '.join([task['name'] for task in self.current_tasks])
        
        prompt = f"""
        As a Developer in a daily stand-up, report on your progress:
        
        Current tasks: {task_list}
        Technical debt items: {', '.join(self.technical_debt_items) if self.technical_debt_items else 'None noted'}
        
        Please provide a concise update covering:
        1. What you accomplished since yesterday
        2. What you plan to do today
        3. Any impediments or blockers you're facing
        
        Keep your response brief, as in a real stand-up meeting.
        """
        
        self.conversation_history.append({"role": "user", "content": prompt})
        response = self.generate_response(prompt)
        self.conversation_history.append({"role": "assistant", "content": response})
        
        # Simple extraction of impediments from response (could be enhanced)
        impediment = None
        if "block" in response.lower() or "imped" in response.lower() or "stuck" in response.lower():
            impediment = "Potential impediment detected in status update"
        
        return response, impediment
    
    def complete_task(self, task):
        """Complete a task.
        
        Args:
            task (dict): The task to complete
            
        Returns:
            tuple: Completion status and any technical debt identified
        """
        prompt = f"""
        As a Developer, you've completed this task:
        
        Task: {task['name']}
        Description: {task.get('description', 'No detailed description provided')}
        Acceptance Criteria: {task.get('acceptance_criteria', ['None provided'])}
        
        Please:
        1. Summarize what you implemented
        2. Confirm how you've met each acceptance criterion
        3. Describe the testing you performed
        4. Identify any technical debt introduced or observed
        5. Note any documentation or knowledge transfer needed
        """
        
        self.conversation_history.append({"role": "user", "content": prompt})
        response = self.generate_response(prompt)
        self.conversation_history.append({"role": "assistant", "content": response})
        
        # Remove from current tasks and add to completed
        if task in self.current_tasks:
            self.current_tasks.remove(task)
        self.completed_tasks.append(task)
        
        # Check for technical debt in response
        technical_debt = None
        if "technical debt" in response.lower() or "debt" in response.lower() or "refactor" in response.lower():
            technical_debt = f"Technical debt related to {task['name']}"
            if technical_debt not in self.technical_debt_items:
                self.technical_debt_items.append(technical_debt)
        
        return response, technical_debt
    
    def provide_technical_input(self, topic):
        """Provide technical expertise on a topic.
        
        Args:
            topic (str): The technical topic to address
            
        Returns:
            str: Technical insights
        """
        prompt = f"""
        As a Developer in a SAFe team, provide technical expertise on this topic:
        
        Topic: {topic}
        
        Please:
        1. Explain the technical considerations around this topic
        2. Provide recommendations based on engineering best practices
        3. Consider the trade-offs of different approaches
        4. Relate your answer to SAFe principles where relevant
        5. Be specific and actionable in your guidance
        """
        
        self.conversation_history.append({"role": "user", "content": prompt})
        response = self.generate_response(prompt)
        self.conversation_history.append({"role": "assistant", "content": response})
        
        return response
    
    def handle_change_request(self, change, current_task):
        """Respond to a change request during implementation.
        
        Args:
            change (dict): The requested change
            current_task (dict): The task currently being worked on
            
        Returns:
            tuple: Impact assessment and recommendation
        """
        prompt = f"""
        As a Developer, respond to this change request that came in while you're working on a task:
        
        Current task: {current_task['name']}
        Current task description: {current_task.get('description', 'No detailed description')}
        
        Change request: {change['description']}
        Urgency: {change.get('urgency', 'Unknown')}
        
        Please:
        1. Assess the technical impact of this change
        2. Estimate the additional effort required
        3. Identify any risks or dependencies affected
        4. Recommend whether to incorporate the change now or defer it
        5. Explain the technical implications of your recommendation
        """
        
        self.conversation_history.append({"role": "user", "content": prompt})
        response = self.generate_response(prompt)
        self.conversation_history.append({"role": "assistant", "content": response})
        
        return response
