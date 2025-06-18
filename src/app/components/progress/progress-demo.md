# Progress Component Demo & Testing

## Testing with Mock Data

If the backend SSE endpoint `/progress/{session_id}` is not yet available, you can test the progress component by manually adding progress events.

### Enable Debug Mode

In your HTML template:

```html
<app-progress 
  [sessionId]="sessionId"
  [show]="isGenerating"
  [debug]="true">
</app-progress>
```

### Add Mock Progress Events

In your component (for testing only):

```typescript
// Add this method to ChatComponent for testing
private simulateProgressEvents(): void {
  const sessionId = this.sessionId;
  
  // Start with orchestrator
  setTimeout(() => {
    this.progressService.addProgressEvent({
      event_type: 'agent_start',
      agent_name: 'T1dInsightOrchestratorAgent',
      session_id: sessionId,
      timestamp: new Date().toISOString(),
      message: 'Starting T1D analysis orchestration...'
    });
  }, 500);

  // Context simulator
  setTimeout(() => {
    this.progressService.addProgressEvent({
      event_type: 'agent_start',
      agent_name: 'AmbientContextSimulatorAgent',
      session_id: sessionId,
      timestamp: new Date().toISOString(),
      parent_agent: 'T1dInsightOrchestratorAgent',
      message: 'Analyzing ambient context...'
    });
  }, 1000);

  setTimeout(() => {
    this.progressService.addProgressEvent({
      event_type: 'agent_progress',
      agent_name: 'AmbientContextSimulatorAgent',
      session_id: sessionId,
      timestamp: new Date().toISOString(),
      progress_percentage: 75,
      message: 'Context analysis 75% complete...'
    });
  }, 2000);

  setTimeout(() => {
    this.progressService.addProgressEvent({
      event_type: 'agent_complete',
      agent_name: 'AmbientContextSimulatorAgent',
      session_id: sessionId,
      timestamp: new Date().toISOString(),
      message: 'Context analysis completed'
    });
  }, 3000);

  // CGM Data Generator
  setTimeout(() => {
    this.progressService.addProgressEvent({
      event_type: 'agent_start',
      agent_name: 'CGMDataGeneratorAgent',
      session_id: sessionId,
      timestamp: new Date().toISOString(),
      parent_agent: 'T1dInsightOrchestratorAgent',
      message: 'Generating CGM data patterns...'
    });
  }, 3500);

  setTimeout(() => {
    this.progressService.addProgressEvent({
      event_type: 'agent_complete',
      agent_name: 'CGMDataGeneratorAgent',
      session_id: sessionId,
      timestamp: new Date().toISOString(),
      message: 'CGM data generated successfully'
    });
  }, 5000);

  // Refinement Loop
  setTimeout(() => {
    this.progressService.addProgressEvent({
      event_type: 'agent_start',
      agent_name: 'RefinementLoopAgent',
      session_id: sessionId,
      timestamp: new Date().toISOString(),
      parent_agent: 'T1dInsightOrchestratorAgent',
      message: 'Starting refinement iterations...'
    });
  }, 5500);

  // Risk Forecaster (sub-agent of refinement loop)
  setTimeout(() => {
    this.progressService.addProgressEvent({
      event_type: 'agent_start',
      agent_name: 'GlycemicRiskForecasterAgent',
      session_id: sessionId,
      timestamp: new Date().toISOString(),
      parent_agent: 'RefinementLoopAgent',
      message: 'Analyzing glycemic risk patterns...'
    });
  }, 6000);

  setTimeout(() => {
    this.progressService.addProgressEvent({
      event_type: 'agent_complete',
      agent_name: 'GlycemicRiskForecasterAgent',
      session_id: sessionId,
      timestamp: new Date().toISOString(),
      message: 'Risk forecast completed'
    });
  }, 8000);

  // Verifier
  setTimeout(() => {
    this.progressService.addProgressEvent({
      event_type: 'agent_start',
      agent_name: 'ForecastVerifierAgent',
      session_id: sessionId,
      timestamp: new Date().toISOString(),
      parent_agent: 'RefinementLoopAgent',
      message: 'Verifying forecast accuracy...'
    });
  }, 8500);

  setTimeout(() => {
    this.progressService.addProgressEvent({
      event_type: 'agent_complete',
      agent_name: 'ForecastVerifierAgent',
      session_id: sessionId,
      timestamp: new Date().toISOString(),
      message: 'Verification completed'
    });
  }, 10000);

  // Complete refinement loop
  setTimeout(() => {
    this.progressService.addProgressEvent({
      event_type: 'agent_complete',
      agent_name: 'RefinementLoopAgent',
      session_id: sessionId,
      timestamp: new Date().toISOString(),
      message: 'Refinement iterations completed'
    });
  }, 10500);

  // Insight Presenter
  setTimeout(() => {
    this.progressService.addProgressEvent({
      event_type: 'agent_start',
      agent_name: 'InsightPresenterAgent',
      session_id: sessionId,
      timestamp: new Date().toISOString(),
      parent_agent: 'T1dInsightOrchestratorAgent',
      message: 'Preparing final insights...'
    });
  }, 11000);

  setTimeout(() => {
    this.progressService.addProgressEvent({
      event_type: 'agent_complete',
      agent_name: 'InsightPresenterAgent',
      session_id: sessionId,
      timestamp: new Date().toISOString(),
      message: 'Insights presentation ready'
    });
  }, 12000);

  // Complete orchestrator
  setTimeout(() => {
    this.progressService.addProgressEvent({
      event_type: 'agent_complete',
      agent_name: 'T1dInsightOrchestratorAgent',
      session_id: sessionId,
      timestamp: new Date().toISOString(),
      message: 'T1D analysis orchestration completed'
    });
  }, 12500);

  // Complete session
  setTimeout(() => {
    this.progressService.addProgressEvent({
      event_type: 'session_complete',
      agent_name: 'System',
      session_id: sessionId,
      timestamp: new Date().toISOString(),
      message: 'Analysis session completed successfully'
    });
  }, 13000);
}
```

### Call Mock Events in executeScenarioRun

For testing, replace the progress service call in `executeScenarioRun`:

```typescript
private executeScenarioRun(scenarioText: string) {
  // For testing: Simulate progress events
  this.simulateProgressEvents();
  
  // Rest of the method...
}
```

## Expected UI Output

When working correctly, you'll see:

```
🎯 Analysis Progress                    🟢 Connected

Overall Progress: 85% (1 refinement iterations)

🎯 T1D Insight Orchestrator            ✅ COMPLETE
├─ 🧠 Ambient Context Simulator        ✅ COMPLETE  
├─ 📊 CGM Data Generator                ✅ COMPLETE
├─ 🔄 Refinement Loop                   ✅ COMPLETE
│   ├─ 📈 Glycemic Risk Forecaster     ✅ COMPLETE
│   ├─ 🔍 Forecast Verifier            ✅ COMPLETE
│   └─ 🎯 Loop Exit Evaluator          ⏳ WAITING
└─ 📝 Insight Presenter                 ✅ COMPLETE
```

## Backend Integration

When the backend is ready, ensure:

1. **SSE Endpoint**: `/progress/{session_id}` returns Server-Sent Events
2. **Event Format**: JSON events matching the `ProgressEvent` interface
3. **CORS**: Configure CORS to allow EventSource connections
4. **Event Types**: Use the supported event types: `agent_start`, `agent_progress`, `agent_complete`, `agent_error`, `session_complete`

## Configuration Options

Enable debug mode to see connection status and event details:

```typescript
// In ngOnInit
this.progressService.updateConfiguration({
  debug: true,
  autoReconnect: true,
  maxReconnectAttempts: 5
});
``` 