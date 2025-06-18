import { Component, Input, OnInit, OnDestroy, ChangeDetectionStrategy, inject } from '@angular/core';
import { Observable, Subject } from 'rxjs';
import { takeUntil } from 'rxjs/operators';
import { 
  ProgressService 
} from '../../core/services/progress.service';
import { 
  ProgressState, 
  AgentStatus, 
  ConnectionStatus 
} from '../../core/models/progress';

@Component({
  selector: 'app-progress',
  templateUrl: './progress.component.html',
  styleUrls: ['./progress.component.scss'],
  changeDetection: ChangeDetectionStrategy.OnPush,
  standalone: false
})
export class ProgressComponent implements OnInit, OnDestroy {
  @Input() sessionId: string = '';
  @Input() show: boolean = true;
  @Input() debug: boolean = false;

  private readonly progressService = inject(ProgressService);
  private destroy$ = new Subject<void>();

  // Reactive state
  progressState$: Observable<ProgressState>;
  connectionStatus$: Observable<ConnectionStatus>;
  
  // Local state for template
  ConnectionStatus = ConnectionStatus;

  constructor() {
    this.progressState$ = this.progressService.progressState$;
    this.connectionStatus$ = this.progressService.connectionStatus$;
  }

  ngOnInit(): void {
    if (this.sessionId) {
      // Enable debug mode if requested
      if (this.debug) {
        this.progressService.updateConfiguration({ debug: true });
      }
      
      // Always start progress tracking when we have a sessionId
      this.progressService.startProgressStream(this.sessionId);
    }
  }

  ngOnDestroy(): void {
    this.progressService.stopProgressStream();
    this.destroy$.next();
    this.destroy$.complete();
  }

  /**
   * Get display name for an agent
   */
  getAgentDisplayName(agentName: string): string {
    const displayNames: { [key: string]: string } = {
      'T1dInsightOrchestratorAgent': '🎯 T1D Insight Orchestrator',
      'AmbientContextSimulatorAgent': '🧠 Ambient Context Simulator',
      'CGMDataGeneratorAgent': '📊 CGM Data Generator',
      'RefinementLoopAgent': '🔄 Refinement Loop',
      'GlycemicRiskForecasterAgent': '📈 Glycemic Risk Forecaster',
      'ForecastVerifierAgent': '🔍 Forecast Verifier',
      'LoopExitEvaluatorAgent': '🎯 Loop Exit Evaluator',
      'InsightPresenterAgent': '📝 Insight Presenter'
    };
    
    return displayNames[agentName] || agentName;
  }

  /**
   * Get status icon for an agent
   */
  getStatusIcon(status: string): string {
    switch (status) {
      case 'waiting': return '⏳';
      case 'running': return '🔄';
      case 'complete': return '✅';
      case 'error': return '❌';
      default: return '🤖';
    }
  }

  /**
   * Get status color for an agent
   */
  getStatusColor(status: string): string {
    switch (status) {
      case 'waiting': return '#9aa0a6';
      case 'running': return '#8ab4f8';
      case 'complete': return '#34a853';
      case 'error': return '#ea4335';
      default: return '#9aa0a6';
    }
  }

  /**
   * Get connection status color
   */
  getConnectionColor(status: ConnectionStatus): string {
    switch (status) {
      case ConnectionStatus.CONNECTED: return '#34a853';
      case ConnectionStatus.CONNECTING: return '#fbbc04';
      case ConnectionStatus.DISCONNECTED: return '#9aa0a6';
      case ConnectionStatus.ERROR: return '#ea4335';
      default: return '#9aa0a6';
    }
  }

  /**
   * Get connection status icon
   */
  getConnectionIcon(status: ConnectionStatus): string {
    switch (status) {
      case ConnectionStatus.CONNECTED: return '🟢';
      case ConnectionStatus.CONNECTING: return '🟡';
      case ConnectionStatus.DISCONNECTED: return '⚫';
      case ConnectionStatus.ERROR: return '🔴';
      default: return '⚫';
    }
  }

  /**
   * Format duration
   */
  formatDuration(startTime?: Date, endTime?: Date): string {
    if (!startTime) return '';
    
    const end = endTime || new Date();
    const duration = end.getTime() - startTime.getTime();
    const seconds = Math.floor(duration / 1000);
    const minutes = Math.floor(seconds / 60);
    
    if (minutes > 0) {
      return `${minutes}m ${seconds % 60}s`;
    } else {
      return `${seconds}s`;
    }
  }

  /**
   * Check if agent has children
   */
  hasChildren(agent: AgentStatus): boolean {
    return agent.children && agent.children.length > 0;
  }

  /**
   * Track by function for ngFor
   */
  trackByAgentName(index: number, agent: AgentStatus): string {
    return agent.name;
  }

  /**
   * Force refresh progress (for manual testing)
   */
  refreshProgress(): void {
    if (this.sessionId) {
      this.progressService.startProgressStream(this.sessionId);
    }
  }
} 