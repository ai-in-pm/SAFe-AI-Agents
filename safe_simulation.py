import json
import time
import random
from datetime import datetime, timedelta

from agents.safe_coach import SAFeCoach
from agents.scrum_master import ScrumMaster
from agents.developer import Developer
from config import DEFAULT_PI_LENGTH, DEFAULT_SPRINT_LENGTH, DEFAULT_CONFIGURATION, CONFIGURATIONS

class SAFeSimulation:
    """A simulation environment for SAFe Agile implementation with AI agents."""
    
    def __init__(self, config=DEFAULT_CONFIGURATION):
        """Initialize the SAFe simulation with the three AI agents.
        
        Args:
            config (str): SAFe configuration to use (essential, portfolio, full)
        """
        self.config = config.lower()
        if self.config not in CONFIGURATIONS:
            self.config = DEFAULT_CONFIGURATION
            
        # Initialize the three AI agents
        self.safe_coach = SAFeCoach(model_provider="openai")
        self.scrum_master = ScrumMaster(model_provider="anthropic")
        self.developer = Developer(model_provider="google")
        
        # Initialize project data
        self.product_backlog = []
        self.pi_scope = []
        self.current_pi = 0
        self.current_sprint = 0
        self.current_day = 0
        self.pi_length = DEFAULT_PI_LENGTH
        self.sprint_length = DEFAULT_SPRINT_LENGTH
        self.pi_start_date = datetime.now()
        self.sprint_start_date = datetime.now()
        
        # Initialize events and communication log
        self.events_log = []
        self.communication_log = []
        
        # Track metrics
        self.metrics = {}
        
        # Portfolio elements (for Portfolio and Full SAFe)
        if self.config in ["portfolio", "full"]:
            self.strategic_themes = []
            self.epics = []
            self.portfolio_backlog = []
        
        # Solution elements (for Full SAFe)
        if self.config == "full":
            self.solutions = []
            self.arts = []  # Agile Release Trains
    
    def setup_project(self, project_name, initial_backlog, strategic_themes=None):
        """Set up a new project.
        
        Args:
            project_name (str): Name of the project
            initial_backlog (list): Initial product backlog items
            strategic_themes (list, optional): Strategic themes for portfolio alignment
        """
        self.project_name = project_name
        self.product_backlog = initial_backlog
        
        # Log project setup
        self.log_event("Project Setup", f"Project '{project_name}' initialized with {len(initial_backlog)} backlog items")
        self.log_event("Configuration", f"Using {self.config.capitalize()} SAFe configuration")
        
        # Set up portfolio elements if applicable
        if self.config in ["portfolio", "full"] and strategic_themes:
            self.strategic_themes = strategic_themes
            self.log_event("Strategic Themes", f"Configured {len(strategic_themes)} strategic themes")
    
    def start_pi(self):
        """Start a new Program Increment."""
        self.current_pi += 1
        self.current_sprint = 0
        self.pi_start_date = datetime.now()
        
        # Log PI start
        self.log_event("PI Start", f"Starting PI {self.current_pi}")
        
        # SAFe Coach conducts PI Planning
        pi_planning_result = self.safe_coach.start_pi_planning(self.product_backlog, self.config)
        self.pi_scope = pi_planning_result[0]
        planning_response = pi_planning_result[1]
        
        # Log the planning result
        self.log_event("PI Planning", f"PI {self.current_pi} planning completed with {len(self.pi_scope)} items in scope")
        self.log_communication("SAFe Coach", "Team", planning_response)
        
        return {
            "pi_number": self.current_pi,
            "start_date": self.pi_start_date,
            "planned_end_date": self.pi_start_date + timedelta(weeks=self.pi_length * self.sprint_length),
            "scope": self.pi_scope,
            "planning_details": planning_response
        }
    
    def start_sprint(self):
        """Start a new sprint within the current PI."""
        self.current_sprint += 1
        self.current_day = 0
        self.sprint_start_date = datetime.now()
        
        # Log sprint start
        self.log_event("Sprint Start", f"Starting Sprint {self.current_sprint} of PI {self.current_pi}")
        
        # Scrum Master conducts Sprint Planning
        sprint_planning_result = self.scrum_master.start_sprint(self.current_pi, self.current_sprint, self.pi_scope)
        sprint_backlog = sprint_planning_result[0]
        planning_response = sprint_planning_result[1]
        
        # Log the planning result
        self.log_event("Sprint Planning", f"Sprint {self.current_sprint} planning completed with {len(sprint_backlog)} items")
        self.log_communication("Scrum Master", "Team", planning_response)
        
        return {
            "sprint_number": self.current_sprint,
            "pi_number": self.current_pi,
            "start_date": self.sprint_start_date,
            "planned_end_date": self.sprint_start_date + timedelta(weeks=self.sprint_length),
            "backlog": sprint_backlog,
            "planning_details": planning_response
        }
    
    def run_daily_standup(self):
        """Run a daily standup for the current sprint."""
        self.current_day += 1
        
        # Generate team updates (simplified for demo)
        team_updates = [
            {
                "member": "Developer",
                "status": "Working on task implementation",
                "impediment": None if random.random() > 0.2 else f"Technical issue #{self.current_day}"
            }
        ]
        
        # Developer reports progress
        dev_status, dev_impediment = self.developer.report_progress()
        if dev_impediment:
            team_updates[0]["impediment"] = dev_impediment
        
        # Log the developer's report
        self.log_communication("Developer", "Team", dev_status)
        
        # Scrum Master conducts daily standup
        sprint_backlog, standup_summary = self.scrum_master.daily_standup(self.current_day, team_updates)
        
        # Log the standup
        self.log_event("Daily Standup", f"Day {self.current_day} of Sprint {self.current_sprint}")
        self.log_communication("Scrum Master", "Team", standup_summary)
        
        # Handle impediments if any
        for update in team_updates:
            if update.get("impediment"):
                impediment = update["impediment"]
                resolution = self.scrum_master.resolve_impediment(impediment)
                self.log_event("Impediment Resolution", f"Scrum Master addressing: {impediment}")
                self.log_communication("Scrum Master", update["member"], resolution)
                
                # If Scrum Master can't resolve, escalate to SAFe Coach
                if "escalate" in resolution.lower() or "cannot resolve" in resolution.lower():
                    coach_response = self.safe_coach.handle_impediment(impediment, self.config)
                    self.log_event("Impediment Escalation", f"Escalated to SAFe Coach: {impediment}")
                    self.log_communication("SAFe Coach", "Scrum Master", coach_response)
        
        return {
            "day": self.current_day,
            "sprint": self.current_sprint,
            "pi": self.current_pi,
            "updates": team_updates,
            "standup_summary": standup_summary,
            "impediments_addressed": [u["impediment"] for u in team_updates if u.get("impediment")]
        }
    
    def end_sprint(self):
        """End the current sprint with review and retrospective."""
        # Simulate sprint completion (simplified for demo)
        # In real use, would track actual completed items throughout sprint
        completion_rate = random.uniform(0.7, 1.0)  # 70-100% completion
        sprint_backlog = self.scrum_master.sprint_backlog
        completed_items = sprint_backlog[:int(len(sprint_backlog) * completion_rate)]
        
        # For each completed item, have the Developer provide completion details
        completed_details = []
        for item in completed_items:
            completion_report, tech_debt = self.developer.complete_task(item)
            self.log_communication("Developer", "Team", completion_report)
            completed_details.append({
                "item": item,
                "report": completion_report,
                "technical_debt": tech_debt
            })
        
        # Scrum Master conducts sprint review and retrospective
        sprint_metrics, retro_response = self.scrum_master.end_sprint(completed_items)
        
        # Log the sprint end events
        self.log_event("Sprint Review", f"Completed Sprint {self.current_sprint} with {len(completed_items)}/{len(sprint_backlog)} items")
        self.log_event("Sprint Retrospective", f"Conducted retrospective for Sprint {self.current_sprint}")
        self.log_communication("Scrum Master", "Team", retro_response)
        
        # Store sprint metrics
        if self.current_pi not in self.metrics:
            self.metrics[self.current_pi] = {}
        self.metrics[self.current_pi][self.current_sprint] = sprint_metrics
        
        return {
            "sprint_number": self.current_sprint,
            "pi_number": self.current_pi,
            "metrics": sprint_metrics,
            "completed_items": completed_items,
            "completion_rate": sprint_metrics["completion_rate"],
            "retrospective": retro_response,
            "technical_debt": [d["technical_debt"] for d in completed_details if d["technical_debt"]]
        }
    
    def end_pi(self):
        """End the current Program Increment with System Demo and I&A workshop."""
        # Gather all achievements from the PI
        pi_metrics = self.metrics.get(self.current_pi, {})
        all_completed_items = []
        
        # Calculate overall PI metrics
        total_planned = 0
        total_completed = 0
        
        for sprint_num, metrics in pi_metrics.items():
            total_planned += metrics.get("planned_points", 0)
            total_completed += metrics.get("completed_points", 0)
        
        predictability = (total_completed / total_planned * 100) if total_planned > 0 else 100
        
        # Simulate business value and team satisfaction
        business_value = random.uniform(7, 10)  # Scale of 1-10
        team_satisfaction = random.uniform(6, 9)  # Scale of 1-10
        
        pi_summary_metrics = {
            "predictability": predictability,
            "business_value": business_value,
            "team_satisfaction": team_satisfaction
        }
        
        # Generate achievement list (simplified)
        achievements = [f"Feature {chr(65+i)}" for i in range(min(5, int(predictability/20)))]
        
        # SAFe Coach conducts Inspect & Adapt workshop
        ia_response = self.safe_coach.end_pi(achievements, pi_summary_metrics, self.config)
        
        # Log PI end events
        self.log_event("PI System Demo", f"Conducted System Demo for PI {self.current_pi}")
        self.log_event("Inspect & Adapt", f"Completed I&A workshop for PI {self.current_pi}")
        self.log_communication("SAFe Coach", "Organization", ia_response)
        
        return {
            "pi_number": self.current_pi,
            "sprints_completed": self.current_sprint,
            "metrics": pi_summary_metrics,
            "achievements": achievements,
            "inspect_and_adapt": ia_response
        }
    
    def handle_change_request(self, change_request):
        """Process a change request based on its urgency and scope."""
        # Determine if change is strategic (portfolio level) or tactical (team level)
        is_strategic = change_request.get("strategic", False) or change_request.get("priority", 5) >= 8
        
        if is_strategic and self.config in ["portfolio", "full"]:
            # Portfolio-level change, handled by SAFe Coach
            if "strategic_themes" in change_request and self.strategic_themes:
                # Strategic alignment check
                alignment_response = self.safe_coach.align_with_strategy(
                    self.strategic_themes, 
                    [{"name": change_request["description"]}], 
                    self.config
                )
                self.log_event("Strategic Change", f"Evaluating alignment of change: {change_request['description']}")
                self.log_communication("SAFe Coach", "Portfolio Management", alignment_response)
                return {
                    "level": "portfolio",
                    "handler": "SAFe Coach",
                    "response": alignment_response,
                    "accepted": "recommended" in alignment_response.lower() or "prioritize" in alignment_response.lower()
                }
            else:
                # General strategic change
                coach_response = self.safe_coach.handle_impediment(
                    f"Strategic change request: {change_request['description']}",
                    self.config
                )
                self.log_event("Strategic Change", f"Processing change: {change_request['description']}")
                self.log_communication("SAFe Coach", "Leadership", coach_response)
                return {
                    "level": "program",
                    "handler": "SAFe Coach",
                    "response": coach_response,
                    "accepted": "accept" in coach_response.lower() and "not" not in coach_response.lower()[:coach_response.lower().find("accept")]
                }
        else:
            # Tactical/Team-level change during sprint
            progress = (self.current_day / (self.sprint_length * 5)) * 100  # Assuming 5-day work week
            scrum_master_response = self.scrum_master.handle_change_request(change_request, progress)
            self.log_event("Sprint Change", f"Evaluating mid-sprint change: {change_request['description']}")
            self.log_communication("Scrum Master", "Team", scrum_master_response)
            
            # If change affects current work, get Developer input
            if self.developer.current_tasks:
                current_task = self.developer.current_tasks[0]
                dev_response = self.developer.handle_change_request(change_request, current_task)
                self.log_communication("Developer", "Scrum Master", dev_response)
                
                return {
                    "level": "team",
                    "handler": "Scrum Master & Developer",
                    "sm_response": scrum_master_response,
                    "dev_response": dev_response,
                    "accepted": "accept" in scrum_master_response.lower() and "not" not in scrum_master_response.lower()[:scrum_master_response.lower().find("accept")]
                }
            else:
                return {
                    "level": "team",
                    "handler": "Scrum Master",
                    "response": scrum_master_response,
                    "accepted": "accept" in scrum_master_response.lower() and "not" not in scrum_master_response.lower()[:scrum_master_response.lower().find("accept")]
                }
    
    def get_technical_guidance(self, topic):
        """Get technical guidance from the Developer agent."""
        response = self.developer.provide_technical_input(topic)
        self.log_communication("Developer", "Team", response)
        return response
    
    def log_event(self, event_type, description):
        """Log a simulation event."""
        timestamp = time.time()
        self.events_log.append({
            "timestamp": timestamp,
            "datetime": datetime.fromtimestamp(timestamp).strftime("%Y-%m-%d %H:%M:%S"),
            "type": event_type,
            "description": description,
            "pi": self.current_pi,
            "sprint": self.current_sprint,
            "day": self.current_day
        })
    
    def log_communication(self, sender, recipient, message):
        """Log communication between agents."""
        timestamp = time.time()
        self.communication_log.append({
            "timestamp": timestamp,
            "datetime": datetime.fromtimestamp(timestamp).strftime("%Y-%m-%d %H:%M:%S"),
            "sender": sender,
            "recipient": recipient,
            "message": message,
            "pi": self.current_pi,
            "sprint": self.current_sprint,
            "day": self.current_day
        })
    
    def get_simulation_state(self):
        """Get the current state of the simulation."""
        return {
            "project_name": getattr(self, "project_name", "Unnamed Project"),
            "configuration": self.config,
            "current_pi": self.current_pi,
            "current_sprint": self.current_sprint,
            "current_day": self.current_day,
            "backlog_size": len(self.product_backlog),
            "pi_scope_size": len(self.pi_scope),
            "pi_start_date": self.pi_start_date.strftime("%Y-%m-%d") if self.current_pi > 0 else None,
            "sprint_start_date": self.sprint_start_date.strftime("%Y-%m-%d") if self.current_sprint > 0 else None,
            "metrics": self.metrics,
            "events": len(self.events_log),
            "communications": len(self.communication_log)
        }
    
    def get_events_log(self, limit=None):
        """Get the events log, optionally limited to most recent events."""
        if limit:
            return self.events_log[-limit:]
        return self.events_log
    
    def get_communication_log(self, limit=None):
        """Get the communication log, optionally limited to most recent communications."""
        if limit:
            return self.communication_log[-limit:]
        return self.communication_log


# Example usage (for testing)
def create_sample_backlog():
    """Create a sample product backlog for testing."""
    return [
        {"name": "User Authentication", "priority": 10, "estimate": 8, 
         "description": "Implement secure user authentication system"},
        {"name": "Dashboard UI", "priority": 8, "estimate": 5,
         "description": "Create responsive dashboard interface"},
        {"name": "Data Export", "priority": 6, "estimate": 3,
         "description": "Allow users to export data in multiple formats"},
        {"name": "API Integration", "priority": 7, "estimate": 8,
         "description": "Integrate with third-party payment processing API"},
        {"name": "Reporting Module", "priority": 5, "estimate": 13,
         "description": "Create customizable reporting system"},
        {"name": "User Preferences", "priority": 4, "estimate": 3,
         "description": "Allow users to customize their experience"},
        {"name": "Mobile Responsiveness", "priority": 7, "estimate": 5,
         "description": "Ensure application works well on mobile devices"},
        {"name": "Email Notifications", "priority": 6, "estimate": 5,
         "description": "Send email alerts for important events"},
        {"name": "Search Functionality", "priority": 5, "estimate": 8,
         "description": "Implement advanced search across all content"},
        {"name": "Admin Dashboard", "priority": 8, "estimate": 8,
         "description": "Create administration interface for system management"},
        {"name": "Performance Optimization", "priority": 4, "estimate": 5,
         "description": "Improve system response time and throughput"},
        {"name": "Data Visualization", "priority": 3, "estimate": 8,
         "description": "Add charts and graphs to represent data"},
    ]


if __name__ == "__main__":
    # Simple test of the simulation
    simulation = SAFeSimulation("essential")
    simulation.setup_project("Demo Project", create_sample_backlog())
    
    # Start a PI
    pi_result = simulation.start_pi()
    print(f"Started PI {pi_result['pi_number']}")
    
    # Start a sprint
    sprint_result = simulation.start_sprint()
    print(f"Started Sprint {sprint_result['sprint_number']}")
    
    # Run a few daily standups
    for _ in range(3):
        standup_result = simulation.run_daily_standup()
        print(f"Completed Day {standup_result['day']} standup")
    
    # End the sprint
    sprint_end = simulation.end_sprint()
    print(f"Ended Sprint {sprint_end['sprint_number']} with {sprint_end['completion_rate']:.1f}% completion")
    
    # Start another sprint
    sprint_result = simulation.start_sprint()
    print(f"Started Sprint {sprint_result['sprint_number']}")
    
    # End the PI
    pi_end = simulation.end_pi()
    print(f"Ended PI {pi_end['pi_number']} with {pi_end['metrics']['predictability']:.1f}% predictability")
    
    # Test a change request
    change = {
        "description": "Add two-factor authentication",
        "priority": 9,
        "urgency": "high",
        "estimate": 8
    }
    change_result = simulation.handle_change_request(change)
    print(f"Change request handled by {change_result['handler']}")
    
    # Print event log summary
    events = simulation.get_events_log()
    print(f"\nEvent Log ({len(events)} events):")
    for event in events:
        print(f"[{event['datetime']}] {event['type']}: {event['description']}")
