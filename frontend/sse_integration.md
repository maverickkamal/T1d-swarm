# T1D Progress Tracking - Angular Integration Guide

## 🚀 Quick Setup

### 1. Add to your Angular Module

```typescript
// app.module.ts
import { ProgressComponent } from './progress/progress.component';
import { ProgressService } from './progress/progress.service';

@NgModule({
  declarations: [
    // ... your components
    ProgressComponent
  ],
  providers: [
    // ... your services
    ProgressService
  ],
  // ...
})
export class AppModule { }
```

### 2. Use in your main component

```typescript
// your-main.component.ts
import { Component } from '@angular/core';
import { ProgressService } from './progress/progress.service';

@Component({
  selector: 'app-main',
  template: `
    <div class="container">
      <!-- Your scenario selection -->
      <div class="scenario-section">
        <button (click)="startAnalysis()">Start T1D Analysis</button>
      </div>

      <!-- Progress tracking component -->
      <app-progress 
        [sessionId]="currentSessionId"
        *ngIf="showProgress">
      </app-progress>

      <!-- Results section -->
      <div class="results-section" *ngIf="analysisComplete">
        <!-- Your results display -->
      </div>
    </div>
  `
})
export class MainComponent {
  currentSessionId: string = '';
  showProgress: boolean = false;
  analysisComplete: boolean = false;

  constructor(private progressService: ProgressService) {}

  async startAnalysis(): Promise<void> {
    // Generate session ID
    this.currentSessionId = 'session_' + Date.now();
    this.showProgress = true;
    this.analysisComplete = false;

    // Start progress tracking
    this.progressService.startProgressStream(this.currentSessionId);

    // Monitor completion
    this.progressService.agentStatus$.subscribe(statuses => {
      const isComplete = statuses.length > 0 && 
                        statuses.every(agent => agent.status === 'complete');
      if (isComplete) {
        this.analysisComplete = true;
        // Optionally stop progress tracking after a delay
        setTimeout(() => {
          this.showProgress = false;
          this.progressService.stopProgressStream();
        }, 3000);
      }
    });

    // Start your actual analysis
    await this.callT1dAnalysisAPI();
  }

  private async callT1dAnalysisAPI(): Promise<void> {
    // Your API call to start T1D analysis
    const response = await fetch('http://localhost:8080/run', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        session_id: this.currentSessionId,
        // ... your analysis parameters
      })
    });
    
    const result = await response.json();
    console.log('Analysis result:', result);
  }
}
```

## 🎨 Customization Options

### Custom Styling

You can override the CSS by adding your own styles:

```css
/* In your component's CSS file */
::ng-deep .progress-container {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

::ng-deep .agent-item {
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(10px);
}
```

### Custom Agent Names

Update the `getAgentDisplayName()` method in `progress.component.ts`:

```typescript
getAgentDisplayName(agentName: string): string {
  const displayNames: { [key: string]: string } = {
    'T1dInsightOrchestratorAgent': '🎯 Master Controller',
    'AmbientContextSimulatorAgent': '🧠 Context Analyzer',
    // ... customize as needed
  };
  
  return displayNames[agentName] || agentName;
}
```

### Progress Event Filtering

Filter events in your component:

```typescript
// Only show certain event types
ngOnInit(): void {
  this.progressService.progress$.subscribe(events => {
    this.filteredEvents = events.filter(event => 
      ['agent_start', 'agent_complete'].includes(event.event_type)
    );
  });
}
```

## 🔧 Advanced Usage

### Multiple Sessions

```typescript
// Handle multiple concurrent sessions
private activeSessions = new Map<string, boolean>();

startNewSession(): void {
  const sessionId = 'session_' + Date.now();
  this.activeSessions.set(sessionId, true);
  this.progressService.startProgressStream(sessionId);
}
```

### Custom Event Handlers

```typescript
ngOnInit(): void {
  // React to specific events
  this.progressService.progress$.subscribe(events => {
    const lastEvent = events[events.length - 1];
    
    if (lastEvent?.event_type === 'agent_complete' && 
        lastEvent?.agent_name === 'InsightPresenterAgent') {
      this.showResultsModal();
    }
  });
}
```

### Error Handling

```typescript
ngOnInit(): void {
  this.progressService.connectionStatus$.subscribe(status => {
    if (status === 'disconnected') {
      this.handleConnectionLost();
    }
  });
}

private handleConnectionLost(): void {
  // Show user-friendly error message
  this.showNotification('Connection lost. Attempting to reconnect...');
  
  // Auto-retry logic
  setTimeout(() => {
    if (this.currentSessionId) {
      this.progressService.startProgressStream(this.currentSessionId);
    }
  }, 5000);
}
```

## 🎯 Backend Configuration

Make sure your FastAPI backend has the progress system enabled:

```python
# main.py
from progress_system import setup_progress_tracking

# After creating your FastAPI app
setup_progress_tracking(app)
```

## 📱 Mobile Responsiveness

The component is fully responsive. For custom mobile layouts:

```css
@media (max-width: 768px) {
  ::ng-deep .progress-container {
    margin: 5px;
    padding: 10px;
  }
  
  ::ng-deep .agent-icon {
    font-size: 1.2rem;
  }
}
```

## 🔍 Debugging

Enable debug mode by setting the debug flag in the progress component:

```html
<app-progress 
  [sessionId]="currentSessionId"
  [debug]="true">  <!-- Set to true for debugging -->
</app-progress>
```

## 🎉 That's it!

Your Angular app now has real-time progress tracking for your T1D analysis system! The progress will show:

- ✅ **Live connection status**
- ✅ **Real-time agent progress**  
- ✅ **Nested sub-agent tracking**
- ✅ **Refinement loop iterations**
- ✅ **Error handling**
- ✅ **Completion notifications**

The UI will look like this:

```
🎯 T1D Analysis Progress                    🟢 Live

Overall Progress: 75% (2 refinement iterations)

🎯 T1D Insight Orchestrator              ✅ COMPLETE
├─ 🧠 Ambient Context Simulator         ✅ COMPLETE  
├─ 📊 CGM Data Generator                 ✅ COMPLETE
├─ 🔄 Refinement Loop                    🔄 RUNNING
│   ├─ 📈 Glycemic Risk Forecaster      ✅ COMPLETE
│   ├─ 🔍 Forecast Verifier             🔄 RUNNING
│   └─ 🎯 Loop Exit Evaluator           ⏳ WAITING
└─ 📝 Insight Presenter                  ⏳ WAITING
```

Perfect for showing users exactly what's happening behind the scenes! 🚀 

## 🔧 Backend Integration Requirements

### Required Event Format

Your backend's `progress_tracker.get_events_stream()` should emit events in this format:

```python
# Event format that frontend expects
event_data = {
    "session_id": session_id,
    "agent_name": "T1dInsightOrchestratorAgent",  # Agent class name
    "event_type": "agent_start",  # or "agent_complete", "agent_error"
    "timestamp": datetime.now().isoformat(),
    "parent_agent": "ParentAgentName",  # Optional, for nested agents
    "data": {  # Optional additional data
        "progress": 0.75,
        "message": "Processing glycemic data..."
    }
}

# Send as SSE event
yield f"data: {json.dumps(event_data)}\n\n"
```

### Integration with Agent Execution

Your backend should emit events at these key points:

```python
async def run_t1d_analysis(session_id: str, scenario_text: str):
    # 1. Emit start event
    await progress_tracker.emit_event(session_id, {
        "agent_name": "T1dInsightOrchestratorAgent",
        "event_type": "agent_start",
        "timestamp": datetime.now().isoformat()
    })
    
    # 2. For each sub-agent
    for agent_name in ["AmbientContextSimulatorAgent", "CGMDataGeneratorAgent"]:
        await progress_tracker.emit_event(session_id, {
            "agent_name": agent_name,
            "event_type": "agent_start",
            "timestamp": datetime.now().isoformat(),
            "parent_agent": "T1dInsightOrchestratorAgent"
        })
        
        # ... agent processing ...
        
        await progress_tracker.emit_event(session_id, {
            "agent_name": agent_name,
            "event_type": "agent_complete",
            "timestamp": datetime.now().isoformat(),
            "parent_agent": "T1dInsightOrchestratorAgent"
        })
    
    # 3. Emit completion
    await progress_tracker.emit_event(session_id, {
        "agent_name": "T1dInsightOrchestratorAgent",
        "event_type": "agent_complete",
        "timestamp": datetime.now().isoformat()
    })
```

## CRITICAL: Backend Implementation

The SSE endpoint exists but **no events are being emitted**. You need to add these calls to your agent execution:

### 1. Add to your main agent execution function:

```python
# In your main run/agent execution endpoint
async def run_agent(request: AgentRunRequest):
    session_id = request.sessionId
    
    # START: Emit orchestrator start
    await progress_tracker.emit_event(session_id, {
        "session_id": session_id,
        "agent_name": "T1dInsightOrchestratorAgent", 
        "event_type": "agent_start",
        "timestamp": datetime.now().isoformat()
    })
    
    # Your existing agent processing...
    results = []
    
    # FOR EACH AGENT: Emit start/complete events
    agents = ["SimulatedCGMFeedAgent", "AmbientContextAgent", "GlycemicRiskForecasterAgent", 
              "ForecastVerifierAgent", "ConfidenceChecker", "InsightPresenterAgent"]
    
    for agent_name in agents:
        # Emit start
        await progress_tracker.emit_event(session_id, {
            "session_id": session_id,
            "agent_name": agent_name,
            "event_type": "agent_start", 
            "timestamp": datetime.now().isoformat(),
            "parent_agent": "T1dInsightOrchestratorAgent"
        })
        
        # Execute agent (your existing code)
        result = await execute_agent(agent_name, ...)
        results.append(result)
        
        # Emit complete
        await progress_tracker.emit_event(session_id, {
            "session_id": session_id,
            "agent_name": agent_name,
            "event_type": "agent_complete",
            "timestamp": datetime.now().isoformat(), 
            "parent_agent": "T1dInsightOrchestratorAgent"
        })
    
    # END: Emit orchestrator complete
    await progress_tracker.emit_event(session_id, {
        "session_id": session_id,
        "agent_name": "T1dInsightOrchestratorAgent",
        "event_type": "agent_complete", 
        "timestamp": datetime.now().isoformat()
    })
    
    return results
```

 