import { Injectable, inject } from '@angular/core';
import { BehaviorSubject, Observable, Subject, fromEvent, of } from 'rxjs';
import { map, catchError, takeUntil, retry, delay, share } from 'rxjs/operators';
import { 
  ProgressEvent, 
  AgentStatus, 
  ConnectionStatus, 
  ProgressState, 
  ProgressConfiguration 
} from '../models/progress';

@Injectable({
  providedIn: 'root'
})
export class ProgressService {
  private readonly baseUrl = 'http://localhost:8080';
  private eventSource: EventSource | null = null;
  private destroy$ = new Subject<void>();
  private reconnectAttempts = 0;
  private mockProgressTimer: any = null;
  
  // Configuration
  private config: ProgressConfiguration = {
    autoReconnect: true,
    reconnectInterval: 5000,
    maxReconnectAttempts: 10,
    debug: true,
    agentDisplayNames: {
      'T1dInsightOrchestratorAgent': '🎯 Master Controller',
      'AmbientContextSimulatorAgent': '🧠 Context Analyzer',
      'CGMDataGeneratorAgent': '📊 CGM Data Generator',
      'RefinementLoopAgent': '🔄 Refinement Loop',
      'GlycemicRiskForecasterAgent': '📈 Glycemic Risk Forecaster',
      'ForecastVerifierAgent': '🔍 Forecast Verifier',
      'LoopExitEvaluatorAgent': '🎯 Loop Exit Evaluator',
      'InsightPresenterAgent': '📝 Insight Presenter'
    }
  };

  // Reactive state
  private progressStateSubject = new BehaviorSubject<ProgressState>({
    sessionId: '',
    overallProgress: 0,
    isComplete: false,
    refinementIterations: 0,
    agents: [],
    connectionStatus: ConnectionStatus.DISCONNECTED
  });

  private progressEventsSubject = new BehaviorSubject<ProgressEvent[]>([]);
  private connectionStatusSubject = new BehaviorSubject<ConnectionStatus>(ConnectionStatus.DISCONNECTED);

  // Public observables
  public readonly progressState$ = this.progressStateSubject.asObservable();
  public readonly progressEvents$ = this.progressEventsSubject.asObservable();
  public readonly connectionStatus$ = this.connectionStatusSubject.asObservable();
  public readonly agentStatus$ = this.progressState$.pipe(
    map(state => state.agents)
  );

  constructor() {
    this.logDebug('ProgressService initialized');
  }

  /**
   * Test SSE connection for debugging
   */
  public testSSEConnection(sessionId: string): Promise<boolean> {
    return new Promise((resolve) => {
      const testUrl = `${this.baseUrl}/progress/${sessionId}`;
      console.log('🧪 Testing SSE connection to:', testUrl);
      
      const testEventSource = new EventSource(testUrl);
      
      const timeout = setTimeout(() => {
        console.log('❌ SSE connection test timed out');
        testEventSource.close();
        resolve(false);
      }, 10000);
      
      testEventSource.onopen = () => {
        console.log('✅ SSE connection test successful');
        clearTimeout(timeout);
        testEventSource.close();
        resolve(true);
      };
      
      testEventSource.onerror = (error) => {
        console.log('❌ SSE connection test failed:', error);
        clearTimeout(timeout);
        testEventSource.close();
        resolve(false);
      };
    });
  }

  /**
   * Start progress tracking for a session
   */
  public startProgressStream(sessionId: string): void {
    this.logDebug(`Starting progress stream for session: ${sessionId}`);
    
    if (this.eventSource) {
      this.stopProgressStream();
    }

    this.resetProgressState(sessionId);
    this.connectToSSE(sessionId);
  }

  /**
   * Stop progress tracking
   */
  public stopProgressStream(): void {
    this.logDebug('Stopping progress stream');
    
    if (this.eventSource) {
      this.eventSource.close();
      this.eventSource = null;
    }
    
    if (this.mockProgressTimer) {
      clearTimeout(this.mockProgressTimer);
      this.mockProgressTimer = null;
    }
    
    this.connectionStatusSubject.next(ConnectionStatus.DISCONNECTED);
    this.destroy$.next();
  }

  private stopProgressStreamWithoutReset(): void {
    this.logDebug('Stopping progress stream (preserving final state)');
    
    if (this.eventSource) {
      this.eventSource.close();
      this.eventSource = null;
    }
    
    if (this.mockProgressTimer) {
      clearTimeout(this.mockProgressTimer);
      this.mockProgressTimer = null;
    }
    
    // Update connection status but preserve progress state
    this.connectionStatusSubject.next(ConnectionStatus.DISCONNECTED);
    
    // Keep the final completed state visible
    console.log('✅ Progress tracking stopped - final state preserved');
  }

  /**
   * Update service configuration
   */
  public updateConfiguration(newConfig: Partial<ProgressConfiguration>): void {
    this.config = { ...this.config, ...newConfig };
    this.logDebug('Configuration updated:', this.config);
  }

  /**
   * Get current progress state
   */
  public getCurrentState(): ProgressState {
    return this.progressStateSubject.getValue();
  }

  /**
   * Manually add a progress event (for testing or fallback)
   */
  public addProgressEvent(event: ProgressEvent): void {
    this.processProgressEvent(event);
  }

  private connectToSSE(sessionId: string): void {
    const url = `${this.baseUrl}/progress/${sessionId}`;
    this.logDebug(`Connecting to SSE endpoint: ${url}`);
    
    this.connectionStatusSubject.next(ConnectionStatus.CONNECTING);
    
    try {
      this.eventSource = new EventSource(url);
      
      this.eventSource.onopen = () => {
        this.logDebug('SSE connection opened');
        this.connectionStatusSubject.next(ConnectionStatus.CONNECTED);
        this.reconnectAttempts = 0;
      };

      this.eventSource.onmessage = (event) => {
        this.handleSSEMessage(event);
      };

      this.eventSource.onerror = (error) => {
        this.handleSSEError(error, sessionId);
      };

    } catch (error) {
      this.logDebug('Error creating EventSource:', error);
      this.connectionStatusSubject.next(ConnectionStatus.ERROR);
      this.attemptReconnect(sessionId);
    }
  }

  private handleSSEMessage(event: MessageEvent): void {
    try {
      const progressEvent: ProgressEvent = JSON.parse(event.data);
      this.logDebug('Received progress event:', progressEvent);
      
      // Add detailed logging to debug the processing
      console.log('🔍 Processing event:', {
        agent_name: progressEvent.agent_name,
        event_type: progressEvent.event_type,
        session_id: progressEvent.session_id,
        timestamp: progressEvent.timestamp,
        parent_agent: progressEvent.parent_agent
      });
      
      this.processProgressEvent(progressEvent);
    } catch (error) {
      this.logDebug('Error parsing SSE message:', error);
      console.error('❌ Failed to parse SSE event:', event.data, error);
    }
  }

  private handleSSEError(error: Event, sessionId: string): void {
    this.logDebug('SSE connection error:', error);
    this.connectionStatusSubject.next(ConnectionStatus.ERROR);
    
    if (this.config.autoReconnect) {
      this.attemptReconnect(sessionId);
    }
  }

  private attemptReconnect(sessionId: string): void {
    if (this.reconnectAttempts >= this.config.maxReconnectAttempts) {
      this.logDebug('Max reconnection attempts reached');
      this.connectionStatusSubject.next(ConnectionStatus.ERROR);
      return;
    }

    this.reconnectAttempts++;
    this.logDebug(`Attempting reconnection ${this.reconnectAttempts}/${this.config.maxReconnectAttempts}`);
    
    setTimeout(() => {
      if (this.eventSource?.readyState === EventSource.CLOSED) {
        this.connectToSSE(sessionId);
      }
    }, this.config.reconnectInterval);
  }

  private processProgressEvent(event: ProgressEvent): void {
    // Add to events list
    const currentEvents = this.progressEventsSubject.getValue();
    const updatedEvents = [...currentEvents, event];
    this.progressEventsSubject.next(updatedEvents);

    // Update progress state
    const currentState = this.progressStateSubject.getValue();
    const updatedState = this.updateProgressState(currentState, event);
    this.progressStateSubject.next(updatedState);
  }

  private updateProgressState(state: ProgressState, event: ProgressEvent): ProgressState {
    const updatedState = { ...state };
    updatedState.lastEvent = event;

    // Skip connection and heartbeat events - these aren't actual agent progress
    if (event.event_type === 'connection' || event.event_type === 'heartbeat') {
      console.log('⏭️ Skipping non-progress event:', event.event_type);
      return updatedState;
    }

    // Find or create agent
    let agent = this.findOrCreateAgent(updatedState.agents, event.agent_name, event.parent_agent);

    console.log('🤖 Agent update:', {
      agentName: event.agent_name,
      eventType: event.event_type,
      previousStatus: agent.status,
      parentAgent: event.parent_agent
    });

    // Update agent based on event type - follow backend events exactly
    switch (event.event_type) {
      case 'agent_start':
        agent.status = 'running';
        agent.startTime = new Date();
        // Don't artificially set progress - wait for backend progress events
        break;
      case 'agent_complete':
        agent.status = 'complete';
        agent.endTime = new Date();
        agent.progress = 100; // Only set to 100 when actually complete
        break;
      case 'agent_error':
        agent.status = 'error';
        agent.endTime = new Date();
        break;
      case 'agent_progress':
        if (event.progress_percentage !== undefined) {
          agent.progress = event.progress_percentage;
        }
        break;
    }

    console.log('🤖 Agent after update:', {
      agentName: agent.name,
      status: agent.status,
      progress: agent.progress
    });

    // Update overall progress
    updatedState.overallProgress = this.calculateOverallProgress(updatedState.agents);
    updatedState.refinementIterations = this.countRefinementIterations(updatedState.agents);
    updatedState.isComplete = this.areAllAgentsComplete(updatedState.agents);

    console.log('📈 State updated:', {
      overallProgress: updatedState.overallProgress,
      agentCount: updatedState.agents.length,
      isComplete: updatedState.isComplete
    });

    // Auto-stop progress tracking when all agents are complete
    if (updatedState.isComplete && updatedState.agents.length > 0) {
      console.log('🎉 All agents complete! Auto-stopping progress tracking in 5 seconds...');
      updatedState.endTime = new Date(); // Mark completion time
      setTimeout(() => {
        // Don't reset state - just stop SSE connection but preserve final state
        this.stopProgressStreamWithoutReset();
      }, 5000); // Give user 5 seconds to see completion
    }

    return updatedState;
  }

  private findOrCreateAgent(agents: AgentStatus[], agentName: string, parentAgent?: string): AgentStatus {
    // Search in flat structure first
    let agent = agents.find(a => a.name === agentName);
    
    if (!agent) {
      // Search in nested structure
      agent = this.findAgentInTree(agents, agentName);
    }
    
    if (!agent) {
      // Create new agent
      agent = {
        name: agentName,
        displayName: this.getAgentDisplayName(agentName),
        status: 'waiting',
        progress: 0,
        parentAgent,
        children: [],
        icon: this.getAgentIcon(agentName)
      };

      // Add to appropriate parent or root
      if (parentAgent) {
        const parent = this.findOrCreateAgent(agents, parentAgent);
        parent.children.push(agent);
      } else {
        agents.push(agent);
      }
    }

    return agent;
  }

  private findAgentInTree(agents: AgentStatus[], agentName: string): AgentStatus | undefined {
    for (const agent of agents) {
      if (agent.name === agentName) {
        return agent;
      }
      const found = this.findAgentInTree(agent.children, agentName);
      if (found) {
        return found;
      }
          }
      return undefined;
  }

  private getAgentDisplayName(agentName: string): string {
    return this.config.agentDisplayNames?.[agentName] || agentName;
  }

  private getAgentIcon(agentName: string): string {
    // Extract emoji from display name if available
    const displayName = this.getAgentDisplayName(agentName);
    const emojiMatch = displayName.match(/^(\p{Emoji})/u);
    return emojiMatch ? emojiMatch[1] : '🤖';
  }

  private calculateOverallProgress(agents: AgentStatus[]): number {
    if (agents.length === 0) {
      console.log('📊 Overall progress: 0% (no agents)');
      return 0;
    }

    const totalAgents = this.countTotalAgents(agents);
    const completedAgents = this.countCompletedAgents(agents);
    const runningAgents = this.countRunningAgents(agents);
    
    // Progress based ONLY on completed agents - no partial credit for running
    const progress = (completedAgents / totalAgents) * 100;
    
    console.log('📊 Progress calculation:', {
      totalAgents,
      completedAgents,
      runningAgents,
      progress: Math.round(progress)
    });
    
    return Math.round(progress);
  }

  private countTotalAgents(agents: AgentStatus[]): number {
    return agents.reduce((count, agent) => {
      return count + 1 + this.countTotalAgents(agent.children);
    }, 0);
  }

  private countCompletedAgents(agents: AgentStatus[]): number {
    return agents.reduce((count, agent) => {
      const isComplete = agent.status === 'complete' ? 1 : 0;
      return count + isComplete + this.countCompletedAgents(agent.children);
    }, 0);
  }

  private countRunningAgents(agents: AgentStatus[]): number {
    return agents.reduce((count, agent) => {
      const isRunning = agent.status === 'running' ? 1 : 0;
      return count + isRunning + this.countRunningAgents(agent.children);
    }, 0);
  }

  private countRefinementIterations(agents: AgentStatus[]): number {
    // Count completed refinement loops
    let iterations = 0;
    for (const agent of agents) {
      if (agent.name.includes('Refinement') && agent.status === 'complete') {
        iterations++;
      }
      iterations += this.countRefinementIterations(agent.children);
    }
    return iterations;
  }

  private areAllAgentsComplete(agents: AgentStatus[]): boolean {
    if (agents.length === 0) {
      return false; // No agents means not complete
    }
    
    return agents.every(agent => {
      // Agent must be complete
      const isAgentComplete = agent.status === 'complete';
      // All children (if any) must also be complete
      const areChildrenComplete = this.areAllAgentsComplete(agent.children);
      
      return isAgentComplete && (agent.children.length === 0 || areChildrenComplete);
    });
  }

  private resetProgressState(sessionId: string): void {
    const initialState: ProgressState = {
      sessionId,
      overallProgress: 0,
      isComplete: false,
      refinementIterations: 0,
      agents: [],
      connectionStatus: ConnectionStatus.DISCONNECTED,
      startTime: new Date()
    };
    
    this.progressStateSubject.next(initialState);
    this.progressEventsSubject.next([]);
  }

  private logDebug(...args: any[]): void {
    if (this.config.debug) {
      console.log('[ProgressService]', ...args);
    }
  }

  private startMockProgress(sessionId: string): void {
    this.logDebug('Starting mock progress for demonstration');
    this.connectionStatusSubject.next(ConnectionStatus.CONNECTED);
    
    // Simulate agent progress over time
    const mockEvents = [
      { agent_name: 'T1dInsightOrchestratorAgent', event_type: 'agent_start', timestamp: Date.now() },
      { agent_name: 'AmbientContextSimulatorAgent', event_type: 'agent_start', timestamp: Date.now() + 1000 },
      { agent_name: 'AmbientContextSimulatorAgent', event_type: 'agent_complete', timestamp: Date.now() + 3000 },
      { agent_name: 'CGMDataGeneratorAgent', event_type: 'agent_start', timestamp: Date.now() + 3500 },
      { agent_name: 'CGMDataGeneratorAgent', event_type: 'agent_complete', timestamp: Date.now() + 6000 },
      { agent_name: 'RefinementLoopAgent', event_type: 'agent_start', timestamp: Date.now() + 6500 },
      { agent_name: 'GlycemicRiskForecasterAgent', event_type: 'agent_start', timestamp: Date.now() + 7000, parent_agent: 'RefinementLoopAgent' },
      { agent_name: 'GlycemicRiskForecasterAgent', event_type: 'agent_complete', timestamp: Date.now() + 10000, parent_agent: 'RefinementLoopAgent' },
      { agent_name: 'ForecastVerifierAgent', event_type: 'agent_start', timestamp: Date.now() + 10500, parent_agent: 'RefinementLoopAgent' },
      { agent_name: 'ForecastVerifierAgent', event_type: 'agent_complete', timestamp: Date.now() + 13000, parent_agent: 'RefinementLoopAgent' },
      { agent_name: 'RefinementLoopAgent', event_type: 'agent_complete', timestamp: Date.now() + 13500 },
      { agent_name: 'InsightPresenterAgent', event_type: 'agent_start', timestamp: Date.now() + 14000 },
      { agent_name: 'InsightPresenterAgent', event_type: 'agent_complete', timestamp: Date.now() + 16000 },
      { agent_name: 'T1dInsightOrchestratorAgent', event_type: 'agent_complete', timestamp: Date.now() + 16500 }
    ];

    let eventIndex = 0;
    const emitNextEvent = () => {
      if (eventIndex < mockEvents.length && this.connectionStatusSubject.getValue() === ConnectionStatus.CONNECTED) {
        const event = mockEvents[eventIndex];
        this.processProgressEvent({
          session_id: sessionId,
          agent_name: event.agent_name,
          event_type: event.event_type as any,
          timestamp: new Date().toISOString(),
          parent_agent: event.parent_agent,
          metadata: {}
        });
        eventIndex++;
        
        // Schedule next event
        if (eventIndex < mockEvents.length) {
          const delay = mockEvents[eventIndex].timestamp - mockEvents[eventIndex - 1].timestamp;
          this.mockProgressTimer = setTimeout(emitNextEvent, delay);
        }
      }
    };

    // Start emitting events after a short delay
    this.mockProgressTimer = setTimeout(emitNextEvent, 1000);
  }

  ngOnDestroy(): void {
    this.stopProgressStream();
    this.destroy$.complete();
  }
} 