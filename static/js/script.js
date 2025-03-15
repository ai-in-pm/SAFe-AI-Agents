// SAFe AI Agents Simulation JavaScript

// Initialize components and event listeners
document.addEventListener('DOMContentLoaded', function() {
    // Connect to WebSocket server
    const socket = io();
    
    // Track simulation state
    let simulationState = {
        initialized: false,
        project_name: '',
        configuration: '',
        current_pi: 0,
        current_sprint: 0,
        current_day: 0,
        pi_scope: [],
        sprint_backlog: [],
        full_backlog: [],
        metrics: {
            velocity: 0,
            points_completed: 0,
            impediments: 0,
            pi_predictability: 'N/A'
        }
    };
    
    // Navigation elements
    const navSetup = document.getElementById('nav-setup');
    const navSimulation = document.getElementById('nav-simulation');
    const navCommunication = document.getElementById('nav-communication');
    const navEvents = document.getElementById('nav-events');
    
    // Panel elements
    const setupPanel = document.getElementById('setup-panel');
    const simulationPanel = document.getElementById('simulation-panel');
    const communicationPanel = document.getElementById('communication-panel');
    const eventsPanel = document.getElementById('events-panel');
    
    // Control elements
    const piControls = document.getElementById('pi-controls');
    const sprintControls = document.getElementById('sprint-controls');
    const changeRequestControls = document.getElementById('change-request-controls');
    const technicalInputControls = document.getElementById('technical-input-controls');
    
    // Display elements
    const simulationStatus = document.getElementById('simulation-status');
    const piDisplay = document.getElementById('pi-display');
    const sprintDisplay = document.getElementById('sprint-display');
    const dayDisplay = document.getElementById('day-display');
    const activityContent = document.getElementById('activity-content');
    const responseContent = document.getElementById('response-content');
    
    // Progress bars
    const piProgressBar = document.getElementById('pi-progress-bar');
    const sprintProgressBar = document.getElementById('sprint-progress-bar');
    const storyCompletionBar = document.getElementById('story-completion-bar');
    
    // Metric displays
    const velocityMetric = document.getElementById('velocity-metric');
    const pointsCompletedMetric = document.getElementById('points-completed-metric');
    const impedimentsMetric = document.getElementById('impediments-metric');
    const piPredictabilityMetric = document.getElementById('pi-predictability-metric');
    
    // Backlog elements
    const backlogItems = document.getElementById('backlog-items');
    const viewPiScopeBtn = document.getElementById('view-pi-scope');
    const viewSprintBacklogBtn = document.getElementById('view-sprint-backlog');
    const viewFullBacklogBtn = document.getElementById('view-full-backlog');
    
    // Agent interaction elements
    const safeCoachStatus = document.getElementById('safe-coach-status');
    const scrumMasterStatus = document.getElementById('scrum-master-status');
    const developerStatus = document.getElementById('developer-status');
    const askSafeCoachBtn = document.getElementById('ask-safe-coach');
    const askScrumMasterBtn = document.getElementById('ask-scrum-master');
    const askDeveloperBtn = document.getElementById('ask-developer');
    
    // Form elements
    const initForm = document.getElementById('init-form');
    const changeRequestForm = document.getElementById('change-request-form');
    const technicalInputForm = document.getElementById('technical-input-form');
    
    // Button elements
    const startPiBtn = document.getElementById('start-pi');
    const endPiBtn = document.getElementById('end-pi');
    const startSprintBtn = document.getElementById('start-sprint');
    const runStandupBtn = document.getElementById('run-standup');
    const endSprintBtn = document.getElementById('end-sprint');
    
    // Table elements
    const communicationsTableBody = document.getElementById('communications-table-body');
    const eventsTableBody = document.getElementById('events-table-body');
    
    // Modal elements
    const responseModal = new bootstrap.Modal(document.getElementById('responseModal'));
    const responseModalTitle = document.getElementById('responseModalTitle');
    const responseModalBody = document.getElementById('responseModalBody');
    
    // SAFe Demonstration Buttons
    const demonstrateEssentialBtn = document.getElementById('demonstrate-essential');
    const demonstratePortfolioBtn = document.getElementById('demonstrate-portfolio');
    const demonstrateFullBtn = document.getElementById('demonstrate-full');
    const demonstrationResults = document.getElementById('demonstration-results');
    const demonstrationTitle = document.getElementById('demonstration-title');
    const safeCoachDemoResponse = document.getElementById('safe-coach-demo-response');
    const scrumMasterDemoResponse = document.getElementById('scrum-master-demo-response');
    const developerDemoResponse = document.getElementById('developer-demo-response');
    
    // Chain of Thought Demonstration Elements
    const demonstrateCoachCotBtn = document.getElementById('demonstrate-coach-cot');
    const demonstrateScrumMasterCotBtn = document.getElementById('demonstrate-scrum-master-cot');
    const demonstrateDeveloperCotBtn = document.getElementById('demonstrate-developer-cot');
    
    const coachQuestion = document.getElementById('coach-cot-question');
    const scrumMasterQuestion = document.getElementById('scrum-master-cot-question');
    const developerQuestion = document.getElementById('developer-cot-question');
    
    const cotResults = document.getElementById('cot-results');
    const cotTitle = document.getElementById('cot-title');
    const cotAgentType = document.getElementById('cot-agent-type');
    const cotStatus = document.getElementById('cot-status');
    const cotQuestion = document.getElementById('cot-question');
    const cotThinkingSteps = document.getElementById('cot-thinking-steps');
    const cotConclusion = document.getElementById('cot-conclusion');
    
    // Navigation handling
    function showPanel(panel) {
        // Hide all panels
        setupPanel.classList.add('d-none');
        simulationPanel.classList.add('d-none');
        communicationPanel.classList.add('d-none');
        eventsPanel.classList.add('d-none');
        
        // Remove active class from all nav items
        navSetup.classList.remove('active');
        navSimulation.classList.remove('active');
        navCommunication.classList.remove('active');
        navEvents.classList.remove('active');
        
        // Show selected panel and activate nav item
        if (panel === 'setup') {
            setupPanel.classList.remove('d-none');
            navSetup.classList.add('active');
        } else if (panel === 'simulation') {
            simulationPanel.classList.remove('d-none');
            navSimulation.classList.add('active');
        } else if (panel === 'communication') {
            communicationPanel.classList.remove('d-none');
            navCommunication.classList.add('active');
            loadCommunications();
        } else if (panel === 'events') {
            eventsPanel.classList.remove('d-none');
            navEvents.classList.add('active');
            loadEvents();
        }
    }
    
    // Attach navigation event listeners
    navSetup.addEventListener('click', function(e) {
        e.preventDefault();
        showPanel('setup');
    });
    
    navSimulation.addEventListener('click', function(e) {
        e.preventDefault();
        showPanel('simulation');
    });
    
    navCommunication.addEventListener('click', function(e) {
        e.preventDefault();
        showPanel('communication');
    });
    
    navEvents.addEventListener('click', function(e) {
        e.preventDefault();
        showPanel('events');
    });
    
    // Initialize simulation
    initForm.addEventListener('submit', function(e) {
        e.preventDefault();
        
        const projectName = document.getElementById('project-name').value || 'SAFe Demo Project';
        const configuration = document.getElementById('configuration').value;
        const useSampleBacklog = document.getElementById('use-sample-backlog').checked;
        
        fetch('/api/initialize', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                project_name: projectName,
                configuration: configuration,
                use_sample_backlog: useSampleBacklog
            })
        })
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                simulationState = data.state;
                updateSimulationStatus();
                showControls();
                showPanel('simulation');
                
                activityContent.innerHTML = `
                    <div class="alert alert-success">
                        <h6>Simulation Initialized</h6>
                        <p>Project: ${projectName}<br>
                        Configuration: ${configuration}<br>
                        Backlog Items: ${data.state.backlog_size}</p>
                    </div>
                `;
                
                responseContent.innerHTML = `
                    <div class="alert alert-info">
                        <p>The simulation has been initialized. You can now start a Program Increment (PI).</p>
                    </div>
                `;
            }
        })
        .catch(error => console.error('Error initializing simulation:', error));
    });
    
    // Start PI
    startPiBtn.addEventListener('click', function() {
        fetch('/api/start_pi', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({})
        })
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                simulationState = data.state;
                updateSimulationStatus();
                
                activityContent.innerHTML = `
                    <div class="alert alert-primary">
                        <h6>PI ${data.data.pi_number} Started</h6>
                        <p>Start Date: ${data.data.start_date}<br>
                        Planned End: ${data.data.planned_end_date}<br>
                        Scope Items: ${data.data.scope.length}</p>
                    </div>
                `;
                
                responseContent.innerHTML = `
                    <div class="rendered-markdown">
                        ${data.data.planning_details_html}
                    </div>
                    <button class="btn btn-sm btn-outline-primary mt-2" onclick="showFullResponse('PI Planning', '${encodeURIComponent(data.data.planning_details_html)}')">
                        View Full Details
                    </button>
                `;
            }
        })
        .catch(error => console.error('Error starting PI:', error));
    });
    
    // Start Sprint
    startSprintBtn.addEventListener('click', function() {
        fetch('/api/start_sprint', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({})
        })
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                simulationState = data.state;
                updateSimulationStatus();
                
                activityContent.innerHTML = `
                    <div class="alert alert-success">
                        <h6>Sprint ${data.data.sprint_number} Started</h6>
                        <p>PI: ${data.data.pi_number}<br>
                        Start Date: ${data.data.start_date}<br>
                        Planned End: ${data.data.planned_end_date}<br>
                        Backlog Items: ${data.data.backlog.length}</p>
                    </div>
                `;
                
                responseContent.innerHTML = `
                    <div class="rendered-markdown">
                        ${data.data.planning_details_html}
                    </div>
                    <button class="btn btn-sm btn-outline-primary mt-2" onclick="showFullResponse('Sprint Planning', '${encodeURIComponent(data.data.planning_details_html)}')">
                        View Full Details
                    </button>
                `;
            }
        })
        .catch(error => console.error('Error starting Sprint:', error));
    });
    
    // Run Daily Standup
    runStandupBtn.addEventListener('click', function() {
        fetch('/api/daily_standup', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({})
        })
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                simulationState = data.state;
                updateSimulationStatus();
                
                // Create updates HTML
                let updatesHtml = '';
                data.data.updates.forEach(update => {
                    updatesHtml += `<p><strong>${update.member}:</strong> ${update.status}`;
                    if (update.impediment) {
                        updatesHtml += `<br><span class="text-danger">Impediment: ${update.impediment}</span>`;
                    }
                    updatesHtml += '</p>';
                });
                
                activityContent.innerHTML = `
                    <div class="alert alert-info">
                        <h6>Daily Standup - Day ${data.data.day}</h6>
                        <p>Sprint: ${data.data.sprint}<br>
                        PI: ${data.data.pi}</p>
                        <div class="mt-2">
                            <strong>Team Updates:</strong>
                            ${updatesHtml}
                        </div>
                        ${data.data.impediments_addressed.length > 0 ? 
                            `<div class="mt-2 text-danger">
                                <strong>Impediments Addressed:</strong>
                                <ul>${data.data.impediments_addressed.map(imp => `<li>${imp}</li>`).join('')}</ul>
                            </div>` : ''}
                    </div>
                `;
                
                responseContent.innerHTML = `
                    <div class="rendered-markdown">
                        ${data.data.standup_summary_html}
                    </div>
                    <button class="btn btn-sm btn-outline-primary mt-2" onclick="showFullResponse('Daily Standup', '${encodeURIComponent(data.data.standup_summary_html)}')">
                        View Full Details
                    </button>
                `;
            }
        })
        .catch(error => console.error('Error running standup:', error));
    });
    
    // End Sprint
    endSprintBtn.addEventListener('click', function() {
        fetch('/api/end_sprint', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({})
        })
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                simulationState = data.state;
                updateSimulationStatus();
                
                activityContent.innerHTML = `
                    <div class="alert alert-warning">
                        <h6>Sprint ${data.data.sprint_number} Ended</h6>
                        <p>PI: ${data.data.pi_number}<br>
                        Completion Rate: ${data.data.completion_rate.toFixed(1)}%<br>
                        Completed Items: ${data.data.completed_items.length}</p>
                        ${data.data.technical_debt.length > 0 ? 
                            `<div class="mt-2">
                                <strong>Technical Debt Generated:</strong>
                                <ul>${data.data.technical_debt.map(debt => `<li>${debt}</li>`).join('')}</ul>
                            </div>` : ''}
                    </div>
                `;
                
                responseContent.innerHTML = `
                    <div class="rendered-markdown">
                        ${data.data.retrospective_html}
                    </div>
                    <button class="btn btn-sm btn-outline-primary mt-2" onclick="showFullResponse('Sprint Retrospective', '${encodeURIComponent(data.data.retrospective_html)}')">
                        View Full Details
                    </button>
                `;
            }
        })
        .catch(error => console.error('Error ending sprint:', error));
    });
    
    // End PI
    endPiBtn.addEventListener('click', function() {
        fetch('/api/end_pi', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({})
        })
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                simulationState = data.state;
                updateSimulationStatus();
                
                activityContent.innerHTML = `
                    <div class="alert alert-secondary">
                        <h6>PI ${data.data.pi_number} Ended</h6>
                        <p>Sprints Completed: ${data.data.sprints_completed}<br>
                        Predictability: ${data.data.metrics.predictability.toFixed(1)}%<br>
                        Business Value: ${data.data.metrics.business_value.toFixed(1)}/10</p>
                        <div class="mt-2">
                            <strong>Achievements:</strong>
                            <ul>${data.data.achievements.map(ach => `<li>${ach}</li>`).join('')}</ul>
                        </div>
                    </div>
                `;
                
                responseContent.innerHTML = `
                    <div class="rendered-markdown">
                        ${data.data.inspect_and_adapt_html}
                    </div>
                    <button class="btn btn-sm btn-outline-primary mt-2" onclick="showFullResponse('Inspect & Adapt', '${encodeURIComponent(data.data.inspect_and_adapt_html)}')">
                        View Full Details
                    </button>
                `;
            }
        })
        .catch(error => console.error('Error ending PI:', error));
    });
    
    // Handle Change Request
    changeRequestForm.addEventListener('submit', function(e) {
        e.preventDefault();
        
        const description = document.getElementById('change-description').value;
        const priority = parseInt(document.getElementById('change-priority').value) || 5;
        const strategic = document.getElementById('change-strategic').checked;
        
        if (!description) {
            alert('Please enter a change description');
            return;
        }
        
        fetch('/api/change_request', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                description: description,
                priority: priority,
                strategic: strategic
            })
        })
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                // Clear form
                document.getElementById('change-description').value = '';
                document.getElementById('change-priority').value = '5';
                document.getElementById('change-strategic').checked = false;
                
                activityContent.innerHTML = `
                    <div class="alert ${data.data.accepted ? 'alert-success' : 'alert-danger'}">
                        <h6>Change Request ${data.data.accepted ? 'Accepted' : 'Rejected'}</h6>
                        <p>Description: ${description}<br>
                        Priority: ${priority}<br>
                        Strategic: ${strategic ? 'Yes' : 'No'}<br>
                        Handled by: ${data.data.handler}</p>
                    </div>
                `;
                
                if (data.data.response_html) {
                    responseContent.innerHTML = `
                        <div class="rendered-markdown">
                            ${data.data.response_html}
                        </div>
                        <button class="btn btn-sm btn-outline-primary mt-2" onclick="showFullResponse('Change Request Response', '${encodeURIComponent(data.data.response_html)}')">
                            View Full Details
                        </button>
                    `;
                } else if (data.data.sm_response_html && data.data.dev_response_html) {
                    responseContent.innerHTML = `
                        <div class="mb-2">
                            <h6>Scrum Master:</h6>
                            <div class="rendered-markdown">
                                ${data.data.sm_response_html}
                            </div>
                        </div>
                        <div>
                            <h6>Developer:</h6>
                            <div class="rendered-markdown">
                                ${data.data.dev_response_html}
                            </div>
                        </div>
                        <button class="btn btn-sm btn-outline-primary mt-2" onclick="showFullResponse('Change Request Responses', '${encodeURIComponent('<h5>Scrum Master:</h5>' + data.data.sm_response_html + '<hr><h5>Developer:</h5>' + data.data.dev_response_html)}')">
                            View Full Details
                        </button>
                    `;
                }
            }
        })
        .catch(error => console.error('Error submitting change request:', error));
    });
    
    // Handle Technical Guidance
    technicalInputForm.addEventListener('submit', function(e) {
        e.preventDefault();
        
        const topic = document.getElementById('technical-topic').value;
        
        if (!topic) {
            alert('Please enter a technical topic');
            return;
        }
        
        fetch('/api/technical_guidance', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                topic: topic
            })
        })
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                // Clear form
                document.getElementById('technical-topic').value = '';
                
                activityContent.innerHTML = `
                    <div class="alert alert-info">
                        <h6>Technical Guidance Requested</h6>
                        <p>Topic: ${data.data.topic}</p>
                    </div>
                `;
                
                responseContent.innerHTML = `
                    <div class="rendered-markdown">
                        ${data.data.guidance_html}
                    </div>
                    <button class="btn btn-sm btn-outline-primary mt-2" onclick="showFullResponse('Technical Guidance', '${encodeURIComponent(data.data.guidance_html)}')">
                        View Full Details
                    </button>
                `;
            }
        })
        .catch(error => console.error('Error requesting technical guidance:', error));
    });
    
    // Load communications
    function loadCommunications() {
        fetch('/api/communications')
            .then(response => response.json())
            .then(data => {
                if (data.status === 'success' && data.data.length > 0) {
                    communicationsTableBody.innerHTML = '';
                    
                    data.data.forEach(comm => {
                        const truncatedMessage = truncateHTML(comm.message_html, 100);
                        const row = document.createElement('tr');
                        row.innerHTML = `
                            <td>${comm.datetime}</td>
                            <td>${comm.sender}</td>
                            <td>${comm.recipient}</td>
                            <td>
                                <div class="message-content">${truncatedMessage}</div>
                                ${comm.message.length > 100 ? 
                                    `<div class="expand-message" onclick="showFullResponse('${comm.sender} to ${comm.recipient}', '${encodeURIComponent(comm.message_html)}')">View full message</div>` : ''}
                            </td>
                            <td>${comm.pi}</td>
                            <td>${comm.sprint}</td>
                        `;
                        communicationsTableBody.appendChild(row);
                    });
                } else {
                    communicationsTableBody.innerHTML = '<tr><td colspan="6" class="text-center">No communications yet</td></tr>';
                }
            })
            .catch(error => console.error('Error loading communications:', error));
    }
    
    // Load events
    function loadEvents() {
        fetch('/api/events')
            .then(response => response.json())
            .then(data => {
                if (data.status === 'success' && data.data.length > 0) {
                    eventsTableBody.innerHTML = '';
                    
                    data.data.forEach(event => {
                        const row = document.createElement('tr');
                        row.classList.add('event-row');
                        row.innerHTML = `
                            <td>${event.datetime}</td>
                            <td>${event.type}</td>
                            <td>${event.description}</td>
                            <td>${event.pi}</td>
                            <td>${event.sprint}</td>
                            <td>${event.day}</td>
                        `;
                        eventsTableBody.appendChild(row);
                    });
                } else {
                    eventsTableBody.innerHTML = '<tr><td colspan="6" class="text-center">No events yet</td></tr>';
                }
            })
            .catch(error => console.error('Error loading events:', error));
    }
    
    /**
     * Update simulation status displays
     */
    function updateSimulationStatus() {
        // Update basic status info
        if (simulationState.initialized) {
            simulationStatus.innerHTML = `
                <strong>Project:</strong> ${simulationState.project_name}<br>
                <strong>Configuration:</strong> ${simulationState.configuration}<br>
                <strong>Current PI:</strong> ${simulationState.current_pi || 'Not started'}<br>
                <strong>Current Sprint:</strong> ${simulationState.current_sprint || 'Not started'}<br>
                <strong>Current Day:</strong> ${simulationState.current_day || 'Not started'}
            `;
            
            // Update progress displays
            piDisplay.textContent = simulationState.current_pi ? `PI ${simulationState.current_pi}` : 'Not started';
            sprintDisplay.textContent = simulationState.current_sprint ? `Sprint ${simulationState.current_sprint}` : 'Not started';
            dayDisplay.textContent = simulationState.current_day ? `Day ${simulationState.current_day}` : 'Not started';
            
            // Update progress bars
            if (simulationState.pi_progress !== undefined) {
                const piProgress = Math.round(simulationState.pi_progress * 100);
                piProgressBar.style.width = `${piProgress}%`;
                piProgressBar.setAttribute('aria-valuenow', piProgress);
                piProgressBar.textContent = `PI Progress: ${piProgress}%`;
            }
            
            if (simulationState.sprint_progress !== undefined) {
                const sprintProgress = Math.round(simulationState.sprint_progress * 100);
                sprintProgressBar.style.width = `${sprintProgress}%`;
                sprintProgressBar.setAttribute('aria-valuenow', sprintProgress);
                sprintProgressBar.textContent = `Sprint Progress: ${sprintProgress}%`;
            }
            
            if (simulationState.story_completion !== undefined) {
                const storyCompletion = Math.round(simulationState.story_completion * 100);
                storyCompletionBar.style.width = `${storyCompletion}%`;
                storyCompletionBar.setAttribute('aria-valuenow', storyCompletion);
                storyCompletionBar.textContent = `Story Completion: ${storyCompletion}%`;
            }
            
            // Update metrics
            if (simulationState.metrics) {
                velocityMetric.textContent = simulationState.metrics.velocity || '0';
                pointsCompletedMetric.textContent = simulationState.metrics.points_completed || '0';
                impedimentsMetric.textContent = simulationState.metrics.impediments || '0';
                piPredictabilityMetric.textContent = simulationState.metrics.pi_predictability || 'N/A';
            }
            
            // Store backlog information
            if (simulationState.pi_scope) {
                simulationState.pi_scope = simulationState.pi_scope;
            }
            
            if (simulationState.sprint_backlog) {
                simulationState.sprint_backlog = simulationState.sprint_backlog;
            }
            
            if (simulationState.full_backlog) {
                simulationState.full_backlog = simulationState.full_backlog;
            }
            
            // If backlog visualization is currently showing, refresh it
            const backlogHeading = backlogItems.querySelector('h6');
            if (backlogHeading) {
                const title = backlogHeading.textContent.split(' ')[0];
                if (title === 'PI') {
                    displayBacklog('pi_scope', simulationState.pi_scope || []);
                } else if (title === 'Sprint') {
                    displayBacklog('sprint_backlog', simulationState.sprint_backlog || []);
                } else if (title === 'Full') {
                    displayBacklog('full_backlog', simulationState.full_backlog || []);
                }
            }
        } else {
            simulationStatus.textContent = 'Not initialized';
        }
    }
    
    /**
     * Show appropriate controls based on simulation state
     */
    function showControls() {
        // Setup form is always shown before initialization
        const setupForm = document.getElementById('setup-form');
        setupForm.style.display = simulationState.initialized ? 'none' : 'block';
        
        // Show/hide PI controls
        piControls.classList.toggle('d-none', !simulationState.initialized);
        
        // Show/hide Sprint controls based on whether PI is active
        sprintControls.classList.toggle('d-none', !simulationState.current_pi);
        
        // Show/hide Change Request and Technical Input based on whether Sprint is active
        changeRequestControls.classList.toggle('d-none', !simulationState.current_sprint);
        technicalInputControls.classList.toggle('d-none', !simulationState.current_sprint);
        
        // Enable/disable buttons based on state
        startPiBtn.disabled = simulationState.current_pi > 0;
        endPiBtn.disabled = simulationState.current_pi === 0;
        
        startSprintBtn.disabled = simulationState.current_sprint > 0 || simulationState.current_pi === 0;
        runStandupBtn.disabled = simulationState.current_sprint === 0;
        endSprintBtn.disabled = simulationState.current_sprint === 0;
        
        // Update agent interaction buttons
        askSafeCoachBtn.disabled = !simulationState.initialized;
        askScrumMasterBtn.disabled = !simulationState.initialized;
        askDeveloperBtn.disabled = !simulationState.initialized;
    }
    
    // Helper function to truncate HTML content
    function truncateHTML(html, maxLength) {
        const tempDiv = document.createElement('div');
        tempDiv.innerHTML = html;
        const text = tempDiv.textContent || tempDiv.innerText || '';
        
        if (text.length <= maxLength) {
            return html;
        }
        
        return text.substring(0, maxLength) + '...';
    }
    
    // Socket event handlers
    socket.on('simulation_state', function(data) {
        simulationState = data.state;
        updateSimulationStatus();
        showControls();
    });
    
    socket.on('pi_started', function(data) {
        simulationState = data.state;
        updateSimulationStatus();
    });
    
    socket.on('sprint_started', function(data) {
        simulationState = data.state;
        updateSimulationStatus();
    });
    
    socket.on('standup_completed', function(data) {
        simulationState = data.state;
        updateSimulationStatus();
    });
    
    socket.on('sprint_ended', function(data) {
        simulationState = data.state;
        updateSimulationStatus();
    });
    
    socket.on('pi_ended', function(data) {
        simulationState = data.state;
        updateSimulationStatus();
    });
    
    // Show full response in modal
    window.showFullResponse = function(title, contentHtml) {
        responseModalTitle.textContent = title;
        responseModalBody.innerHTML = decodeURIComponent(contentHtml);
        responseModal.show();
    };
    
    // Backlog visualization event handlers
    viewPiScopeBtn.addEventListener('click', function() {
        displayBacklog('pi_scope', simulationState.pi_scope || []);
    });
    
    viewSprintBacklogBtn.addEventListener('click', function() {
        displayBacklog('sprint_backlog', simulationState.sprint_backlog || []);
    });
    
    viewFullBacklogBtn.addEventListener('click', function() {
        displayBacklog('full_backlog', simulationState.full_backlog || []);
    });
    
    // Agent interaction event handlers
    askSafeCoachBtn.addEventListener('click', function() {
        const question = prompt('What would you like to ask the SAFe Coach?');
        if (question && question.trim()) {
            askAgent('safe_coach', question);
        }
    });
    
    askScrumMasterBtn.addEventListener('click', function() {
        const question = prompt('What would you like to ask the Scrum Master?');
        if (question && question.trim()) {
            askAgent('scrum_master', question);
        }
    });
    
    askDeveloperBtn.addEventListener('click', function() {
        const question = prompt('What would you like to ask the Developer?');
        if (question && question.trim()) {
            askAgent('developer', question);
        }
    });
    
    /**
     * Display backlog items in the UI
     * @param {string} type - Type of backlog ('pi_scope', 'sprint_backlog', or 'full_backlog')
     * @param {Array} items - Backlog items to display
     */
    function displayBacklog(type, items) {
        if (!items || items.length === 0) {
            backlogItems.innerHTML = `<div class="text-muted">No items in the ${type.replace('_', ' ')} yet</div>`;
            return;
        }
        
        // Set appropriate title based on backlog type
        let title = '';
        let badgeClass = '';
        
        if (type === 'pi_scope') {
            title = 'PI Scope';
            badgeClass = 'bg-primary';
        } else if (type === 'sprint_backlog') {
            title = 'Sprint Backlog';
            badgeClass = 'bg-success';
        } else {
            title = 'Full Backlog';
            badgeClass = 'bg-secondary';
        }
        
        // Generate HTML for backlog items
        let html = `<h6>${title} <span class="badge ${badgeClass}">${items.length} items</span></h6><div class="list-group">`;
        
        items.forEach(item => {
            const priorityClass = item.priority <= 3 ? 'bg-danger' :
                                 item.priority <= 6 ? 'bg-warning' : 'bg-info';
            
            let status = item.status || 'Not Started';
            let statusBadge = '';
            
            if (status === 'Completed') {
                statusBadge = '<span class="badge bg-success ms-2">Completed</span>';
            } else if (status === 'In Progress') {
                statusBadge = '<span class="badge bg-primary ms-2">In Progress</span>';
            } else if (status === 'Blocked') {
                statusBadge = '<span class="badge bg-danger ms-2">Blocked</span>';
            }
            
            html += `
                <div class="list-group-item d-flex justify-content-between align-items-center">
                    <div>
                        <h6>${item.name} ${statusBadge}</h6>
                        <small class="text-muted">${item.description || 'No description'}</small>
                    </div>
                    <div>
                        <span class="badge ${priorityClass} me-2">P${item.priority}</span>
                        ${item.estimate ? `<span class="badge bg-dark">${item.estimate} pts</span>` : ''}
                    </div>
                </div>
            `;
        });
        
        html += '</div>';
        backlogItems.innerHTML = html;
    }
    
    /**
     * Send a question to a specific agent
     * @param {string} agent_type - Type of agent ('safe_coach', 'scrum_master', or 'developer')
     * @param {string} question - Question to ask the agent
     */
    function askAgent(agent_type, question) {
        // Update agent status to show it's processing
        updateAgentStatus(agent_type, 'Thinking...');
        
        fetch('/api/ask_agent', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                agent_type: agent_type,
                question: question
            })
        })
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                // Update response UI
                responseContent.innerHTML = `
                    <div class="alert alert-info">
                        <strong>You asked:</strong> ${question}
                    </div>
                    <div class="rendered-markdown">
                        ${data.response_html || data.response}
                    </div>
                    <button class="btn btn-sm btn-outline-primary mt-2" onclick="showFullResponse('Agent Response', '${encodeURIComponent(data.response_html || data.response)}')">
                        View Full Response
                    </button>
                `;
                
                // Add to communication log
                addCommunication('User', agent_type, question, data.timestamp);
                addCommunication(agent_type, 'User', data.response, data.timestamp);
                
                // Update agent status
                updateAgentStatus(agent_type, 'Ready');
            } else {
                responseContent.innerHTML = `<div class="alert alert-danger">Error: ${data.message}</div>`;
                updateAgentStatus(agent_type, 'Error');
            }
        })
        .catch(error => {
            console.error(`Error asking ${agent_type}:`, error);
            responseContent.innerHTML = `<div class="alert alert-danger">Error communicating with the agent</div>`;
            updateAgentStatus(agent_type, 'Error');
        });
    }
    
    /**
     * Update the status display for an agent
     * @param {string} agent_type - Type of agent ('safe_coach', 'scrum_master', or 'developer')
     * @param {string} status - Status message to display
     */
    function updateAgentStatus(agent_type, status) {
        if (agent_type === 'safe_coach') {
            safeCoachStatus.innerHTML = status;
            if (status === 'Thinking...') {
                safeCoachStatus.className = 'text-primary';
            } else if (status === 'Error') {
                safeCoachStatus.className = 'text-danger';
            } else {
                safeCoachStatus.className = '';
            }
        } else if (agent_type === 'scrum_master') {
            scrumMasterStatus.innerHTML = status;
            if (status === 'Thinking...') {
                scrumMasterStatus.className = 'text-primary';
            } else if (status === 'Error') {
                scrumMasterStatus.className = 'text-danger';
            } else {
                scrumMasterStatus.className = '';
            }
        } else if (agent_type === 'developer') {
            developerStatus.innerHTML = status;
            if (status === 'Thinking...') {
                developerStatus.className = 'text-primary';
            } else if (status === 'Error') {
                developerStatus.className = 'text-danger';
            } else {
                developerStatus.className = '';
            }
        }
    }
    
    /**
     * Add a communication entry to the communications log
     * @param {string} from - Sender
     * @param {string} to - Recipient
     * @param {string} message - Communication message
     * @param {string} timestamp - Timestamp of the communication
     */
    function addCommunication(from, to, message, timestamp) {
        const truncatedMessage = truncateHTML(message, 50);
        const row = document.createElement('tr');
        row.innerHTML = `
            <td>${timestamp || new Date().toLocaleTimeString()}</td>
            <td>${from}</td>
            <td>${to}</td>
            <td>${truncatedMessage}</td>
            <td>${simulationState.current_pi || 'N/A'}</td>
            <td>${simulationState.current_sprint || 'N/A'}</td>
        `;
        
        // Remove "No communications yet" row if it exists
        if (communicationsTableBody.querySelector('td[colspan="6"]')) {
            communicationsTableBody.innerHTML = '';
        }
        
        communicationsTableBody.prepend(row);
    }
    
    // SAFe Demonstration event handlers
    demonstrateEssentialBtn.addEventListener('click', function() {
        demonstrateSafeConfig('essential');
    });
    
    demonstratePortfolioBtn.addEventListener('click', function() {
        demonstrateSafeConfig('portfolio');
    });
    
    demonstrateFullBtn.addEventListener('click', function() {
        demonstrateSafeConfig('full');
    });
    
    /**
     * Demonstrate a specific SAFe configuration with agent explanations
     * @param {string} configType - Type of SAFe configuration ('essential', 'portfolio', or 'full')
     */
    function demonstrateSafeConfig(configType) {
        // Update UI to show loading state
        demonstrationTitle.textContent = `${configType.charAt(0).toUpperCase() + configType.slice(1)} SAFe Configuration Demonstration (Loading...)`;
        safeCoachDemoResponse.innerHTML = '<div class="spinner-border text-primary" role="status"><span class="visually-hidden">Loading...</span></div>';
        scrumMasterDemoResponse.innerHTML = '<div class="spinner-border text-primary" role="status"><span class="visually-hidden">Loading...</span></div>';
        developerDemoResponse.innerHTML = '<div class="spinner-border text-primary" role="status"><span class="visually-hidden">Loading...</span></div>';
        
        // Show the demonstration results section
        demonstrationResults.classList.remove('d-none');
        
        // Scroll to the demonstration results
        demonstrationResults.scrollIntoView({ behavior: 'smooth' });
        
        // Make API call to get the agent explanations
        fetch('/api/demonstrate_safe_config', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                config_type: configType
            })
        })
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                // Update the demonstration title
                demonstrationTitle.textContent = `${configType.charAt(0).toUpperCase() + configType.slice(1)} SAFe Configuration Demonstration`;
                
                // Update the agent responses
                safeCoachDemoResponse.innerHTML = data.safe_coach.html;
                scrumMasterDemoResponse.innerHTML = data.scrum_master.html;
                developerDemoResponse.innerHTML = data.developer.html;
                
                // Update simulation state if needed
                if (data.state) {
                    updateSimulationState(data.state);
                }
            } else {
                // Show error message
                demonstrationTitle.textContent = `Error: ${data.message}`;
                safeCoachDemoResponse.innerHTML = '<div class="alert alert-danger">Failed to load SAFe Coach response</div>';
                scrumMasterDemoResponse.innerHTML = '<div class="alert alert-danger">Failed to load Scrum Master response</div>';
                developerDemoResponse.innerHTML = '<div class="alert alert-danger">Failed to load Developer response</div>';
            }
        })
        .catch(error => {
            console.error('Error demonstrating SAFe configuration:', error);
            demonstrationTitle.textContent = 'Error Demonstrating SAFe Configuration';
            safeCoachDemoResponse.innerHTML = '<div class="alert alert-danger">An error occurred while communicating with the server</div>';
            scrumMasterDemoResponse.innerHTML = '<div class="alert alert-danger">An error occurred while communicating with the server</div>';
            developerDemoResponse.innerHTML = '<div class="alert alert-danger">An error occurred while communicating with the server</div>';
        });
    }
    
    // Chain of Thought Demonstration event handlers
    demonstrateCoachCotBtn.addEventListener('click', function() {
        demonstrateChainOfThought('safe_coach', coachQuestion.value);
    });
    
    demonstrateScrumMasterCotBtn.addEventListener('click', function() {
        demonstrateChainOfThought('scrum_master', scrumMasterQuestion.value);
    });
    
    demonstrateDeveloperCotBtn.addEventListener('click', function() {
        demonstrateChainOfThought('developer', developerQuestion.value);
    });
    
    /**
     * Demonstrate the Chain of Thought for a specific agent
     * @param {string} agent_type - Type of agent ('safe_coach', 'scrum_master', or 'developer')
     * @param {string} question - Question to ask the agent
     */
    function demonstrateChainOfThought(agent_type, question) {
        // Update UI to show loading state
        let agentDisplayName = '';
        if (agent_type === 'safe_coach') {
            agentDisplayName = 'SAFe Coach';
        } else if (agent_type === 'scrum_master') {
            agentDisplayName = 'Scrum Master';
        } else if (agent_type === 'developer') {
            agentDisplayName = 'Developer';
        }
        
        cotTitle.textContent = `${agentDisplayName} Chain of Thought Reasoning`;
        cotAgentType.textContent = agentDisplayName;
        cotStatus.textContent = 'Thinking...';
        cotStatus.className = 'badge bg-info';
        cotQuestion.textContent = question;
        cotThinkingSteps.innerHTML = '<div class="text-center"><div class="spinner-border text-primary" role="status"><span class="visually-hidden">Loading...</span></div></div>';
        cotConclusion.innerHTML = '<div class="text-center"><div class="spinner-border text-primary" role="status"><span class="visually-hidden">Loading...</span></div></div>';
        
        // Show the Chain of Thought section
        cotResults.classList.remove('d-none');
        
        // Scroll to the Chain of Thought results
        cotResults.scrollIntoView({ behavior: 'smooth' });
        
        console.log(`Sending CoT request for agent: ${agent_type}, question: ${question}`);
        
        // Make API call to get the Chain of Thought
        fetch('/api/demonstrate_cot', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                agent_type: agent_type,
                question: question
            })
        })
        .then(response => {
            console.log('CoT response status:', response.status);
            return response.json();
        })
        .then(data => {
            console.log('CoT response data:', data);
            if (data.status === 'success') {
                // Update the status
                cotStatus.textContent = 'Complete';
                cotStatus.className = 'badge bg-success';
                
                // Clear the thinking steps container
                cotThinkingSteps.innerHTML = '';
                
                // Display thinking steps one by one with animation
                if (data.thought_process && data.thought_process.length > 0) {
                    // Create a function to add steps with delay
                    const addStepWithDelay = (index) => {
                        if (index < data.thought_process.length) {
                            const stepDiv = document.createElement('div');
                            stepDiv.className = 'reasoning-step';
                            stepDiv.innerHTML = data.thought_process_html[index];
                            cotThinkingSteps.appendChild(stepDiv);
                            
                            // Trigger animation
                            setTimeout(() => {
                                stepDiv.classList.add('visible');
                            }, 10);
                            
                            // Schedule next step
                            setTimeout(() => {
                                addStepWithDelay(index + 1);
                            }, 500);
                        }
                    };
                    
                    // Start adding steps
                    addStepWithDelay(0);
                } else {
                    cotThinkingSteps.innerHTML = '<div class="alert alert-warning">No thinking steps provided</div>';
                }
                
                // Update the conclusion
                cotConclusion.innerHTML = data.conclusion_html;
                
                // Update simulation state if needed
                if (data.state) {
                    updateSimulationState(data.state);
                }
            } else {
                // Show error message
                cotStatus.textContent = 'Error';
                cotStatus.className = 'badge bg-danger';
                cotThinkingSteps.innerHTML = `<div class="alert alert-danger">Failed to load thinking steps: ${data.message}</div>`;
                cotConclusion.innerHTML = `<div class="alert alert-danger">Failed to load conclusion: ${data.message}</div>`;
            }
        })
        .catch(error => {
            console.error('Error demonstrating Chain of Thought:', error);
            cotStatus.textContent = 'Error';
            cotStatus.className = 'badge bg-danger';
            cotThinkingSteps.innerHTML = '<div class="alert alert-danger">An error occurred while communicating with the server</div>';
            cotConclusion.innerHTML = '<div class="alert alert-danger">An error occurred while communicating with the server</div>';
        });
    }
    
    // SAFe Configuration Demonstration Functions
    function demonstrateSafeConfiguration(configType) {
        // Update UI with sophisticated visualization paradigm
        $('#config-image-container').removeClass('d-none');
        $('#config-explanation').removeClass('d-none');
        
        // Configuration nomenclature mapping for enhanced semantic context
        const configurationNomenclature = {
            'big_picture': 'SAFe Big Picture - Comprehensive Framework Overview',
            'core_competencies': 'Core Competencies - Business Agility Enablers',
            'essential': 'Essential SAFe - Foundational Implementation Paradigm',
            'large_solution': 'Large Solution SAFe - Complex Systems Development Framework',
            'portfolio': 'Portfolio SAFe - Strategic Alignment Architecture',
            'full': 'Full SAFe - Enterprise-scale Transformation Methodology'
        };
        
        // Map the config_type to the image number based on the user-provided images
        const configImageMapping = {
            'big_picture': 1,      // First image
            'core_competencies': 2, // Second image
            'essential': 3,         // Third image
            'large_solution': 4,    // Fourth image
            'portfolio': 5,         // Fifth image
            'full': 6               // Sixth image
        };
        
        // Set configuration title with enhanced semantic description
        $('#config-title').text(configurationNomenclature[configType]);
        
        // Use the mapped image number to load the correct image
        const imgNum = configImageMapping[configType];
        $('#config-image').attr('src', `/static/images/safe_config_${imgNum}.jpg`);
        $('#config-loading').show();
        
        // Reset all agent tabs with methodologically sound initialization
        resetConfigurationTabContent();
        
        // Execute sophisticated API request with appropriate error handling protocol
        $.ajax({
            url: '/api/demonstrate_safe_config',
            type: 'POST',
            contentType: 'application/json',
            data: JSON.stringify({ config_type: configType }),
            success: function(response) {
                $('#config-loading').hide();
                
                if (response.status === 'success') {
                    // Update SAFe Coach tab with in-depth cognitive analysis
                    updateAgentConfigTab('coach', response.coach);
                    
                    // Update Scrum Master tab with implementation-focused methodological insights
                    updateAgentConfigTab('sm', response.scrum_master);
                    
                    // Update Developer tab with practical engineering implications
                    updateAgentConfigTab('dev', response.developer);
                    
                    // Update simulation state with comprehensive data integration
                    updateSimulationState(response.state);
                    
                    // Log analytical data for subsequent meta-analysis
                    console.log(`Configuration demonstration complete: ${configType}`);
                    console.log(`Response structure verification: ${Object.keys(response).join(', ')}`);
                } else {
                    // Implement sophisticated error handling with diagnostic capabilities
                    showError(`Failed to demonstrate ${configType} configuration: ${response.message}`);
                    console.error('Error details:', response);
                }
            },
            error: function(xhr, status, error) {
                $('#config-loading').hide();
                // Execute comprehensive error diagnostics
                console.error('Error demonstrating SAFe configuration:', error);
                console.log('Diagnostic response data:', xhr.responseText);
                // Implement user-facing error communication
                showError(`Error demonstrating ${configType} configuration: ${error}. See diagnostic console output for detailed analysis.`);
            }
        });
    }
    
    function resetConfigurationTabContent() {
        // Reset agent statuses
        $('#coach-status, #sm-status, #dev-status').text('Loading...').removeClass('bg-success').addClass('bg-secondary');
        
        // Reset thinking sections with loading spinners
        const loadingSpinner = `
            <div class="text-center">
                <div class="spinner-border text-primary" role="status">
                    <span class="visually-hidden">Loading...</span>
                </div>
            </div>
        `;
        
        $('#coach-thinking, #sm-thinking, #dev-thinking').html(loadingSpinner);
        $('#coach-conclusion, #sm-conclusion, #dev-conclusion').html(loadingSpinner);
    }
    
    function updateAgentConfigTab(agentPrefix, agentData) {
        // Update status
        $(`#${agentPrefix}-status`).text('Complete').removeClass('bg-secondary').addClass('bg-success');
        
        // Clear thinking section
        $(`#${agentPrefix}-thinking`).empty();
        
        // Add thinking steps with sequential animation
        agentData.thought_process_html.forEach((step, index) => {
            const stepDiv = $(`<div class="reasoning-step mb-3 opacity-0"></div>`).html(step);
            $(`#${agentPrefix}-thinking`).append(stepDiv);
            
            // Animate each step with a delay
            setTimeout(() => {
                stepDiv.addClass('animate__animated animate__fadeIn');
                stepDiv.removeClass('opacity-0');
            }, index * 300);
        });
        
        // Update conclusion with animation
        $(`#${agentPrefix}-conclusion`).html(agentData.conclusion_html);
        $(`#${agentPrefix}-conclusion`).addClass('animate__animated animate__fadeIn');
    }
    
    // Event listeners for SAFe configuration buttons
    $(document).ready(function() {
        $('.config-btn').on('click', function() {
            const configType = $(this).data('config');
            // Highlight the active button
            $('.config-btn').removeClass('active');
            $(this).addClass('active');
            
            // Demonstrate the selected configuration
            demonstrateSafeConfiguration(configType);
        });
    });
    
    // Start with setup panel visible
    showPanel('setup');
});

// Image upload handling for SAFe configurations
function uploadSafeConfigImage(configType, imageFile) {
    const formData = new FormData();
    formData.append('image', imageFile);
    
    $.ajax({
        url: `/api/upload_safe_config_image/${configType}`,
        type: 'POST',
        data: formData,
        processData: false,
        contentType: false,
        success: function(response) {
            if (response.status === 'success') {
                console.log(`Successfully uploaded ${configType} configuration image`);
                // Update the image src with a timestamp to avoid caching issues
                $(`#config-image[data-config="${configType}"]`).attr('src', `${response.path}?t=${new Date().getTime()}`);
            } else {
                showError(`Failed to upload ${configType} image: ${response.message}`);
            }
        },
        error: function(xhr, status, error) {
            console.error('Error uploading image:', error);
            showError(`Error uploading ${configType} image: ${error}`);
        }
    });
}

// Function to programmatically load sample SAFe configuration images
function preloadSafeConfigImages() {
    // Map of configuration types to image URLs
    const configImages = {
        'big_picture': '/static/images/safe_configurations/big_picture.jpg',
        'core_competencies': '/static/images/safe_configurations/core_competencies.jpg',
        'essential': '/static/images/safe_configurations/essential.jpg',
        'large_solution': '/static/images/safe_configurations/large_solution.jpg',
        'portfolio': '/static/images/safe_configurations/portfolio.jpg',
        'full': '/static/images/safe_configurations/full.jpg'
    };
    
    // Display a notification to let the user know the system is ready
    showNotification('SAFe Configuration images are ready. Click on any configuration button to see explanations from all three AI agents.');
}

// Call preload function when document is ready
$(document).ready(function() {
    // Add this to your existing document ready function
    preloadSafeConfigImages();
});
