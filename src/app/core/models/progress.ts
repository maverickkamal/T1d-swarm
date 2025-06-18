// Progress tracking models for SSE integration

export interface ProgressEvent {
  event_type: 'agent_start' | 'agent_complete' | 'agent_progress' | 'agent_error' | 'session_complete' | 'connection' | 'heartbeat';
  agent_name: string;
  session_id: string;
  timestamp: string;
  progress_percentage?: number;
  message?: string;
  parent_agent?: string;
  metadata?: any;
}

export interface AgentStatus {
  name: string;
  displayName: string;
  status: 'waiting' | 'running' | 'complete' | 'error';
  progress: number;
  message?: string;
  parentAgent?: string;
  children: AgentStatus[];
  startTime?: Date;
  endTime?: Date;
  icon?: string;
}

export enum ConnectionStatus {
  DISCONNECTED = 'disconnected',
  CONNECTING = 'connecting', 
  CONNECTED = 'connected',
  ERROR = 'error'
}

export interface ProgressState {
  sessionId: string;
  overallProgress: number;
  isComplete: boolean;
  refinementIterations: number;
  agents: AgentStatus[];
  connectionStatus: ConnectionStatus;
  lastEvent?: ProgressEvent;
  startTime?: Date;
  endTime?: Date;
}

export interface ProgressConfiguration {
  autoReconnect: boolean;
  reconnectInterval: number;
  maxReconnectAttempts: number;
  debug: boolean;
  filterEventTypes?: string[];
  agentDisplayNames?: { [key: string]: string };
} 