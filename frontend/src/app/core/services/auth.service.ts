/**
 * @license
 * Copyright 2025 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *     http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

import { Injectable } from '@angular/core';
import { HttpClient, HttpErrorResponse } from '@angular/common/http';
import { BehaviorSubject, Observable, throwError, of, firstValueFrom } from 'rxjs';
import { catchError, switchMap, tap, map } from 'rxjs/operators';
import { SessionInfo, JudgeVerificationResponse, JudgeVerificationRequest, SessionLimitError } from '../models/auth.types';
import { Router } from '@angular/router';
import { URLUtil } from '../../../utils/url-util';

@Injectable({
  providedIn: 'root'
})
export class AuthService {
  private sessionInfoSubject = new BehaviorSubject<SessionInfo | null>(null);
  public sessionInfo$ = this.sessionInfoSubject.asObservable();

  constructor(private http: HttpClient, private router: Router) {}

  /**
   * Get the full API URL for a given endpoint
   */
  private getApiUrl(endpoint: string): string {
    const baseUrl = URLUtil.getApiServerBaseUrl();
    if (!baseUrl) {
      console.warn('No backend URL configured, using relative URL');
      return endpoint;
    }
    // Remove trailing slash from baseUrl and leading slash from endpoint if present
    const cleanBaseUrl = baseUrl.replace(/\/$/, '');
    const cleanEndpoint = endpoint.replace(/^\//, '');
    return `${cleanBaseUrl}/${cleanEndpoint}`;
  }

  /**
   * Checks the session status with the backend.
   * This is the single source of truth for session state. It handles all error
   * conditions and updates the sessionInfo$ stream.
   */
  checkSessionStatus(): Observable<SessionInfo> {
    const url = this.getApiUrl('api/check-access');
    console.log('Checking session status at:', url);
    
    return this.http.get<SessionInfo>(url).pipe(
      catchError((error: HttpErrorResponse) => {
        console.error('Session status check failed:', error);
        
        if (error.status === 429) {
          // No sessions left. Create a valid SessionInfo object reflecting this.
          const sessionError = error.error as SessionLimitError;
          const noAccessInfo: SessionInfo = {
            can_access: false,
            message: sessionError.message || 'No sessions remaining.',
            sessions_remaining: 0,
            is_judge: false,
            device_id: 'unknown',
          };
          return of(noAccessInfo);
        }
        if (error.status === 0 || error.status === 404) {
          // Backend is not available. Provide mock data for development.
          console.warn('Backend not available, using mock session data.');
          const mockSession: SessionInfo = {
            can_access: true,
            message: 'Dev mode: Backend not found.',
            sessions_remaining: 3,
            is_judge: false,
            device_id: 'dev-device'
          };
          return of(mockSession);
        }
        // For any other errors, create a default "no access" state.
        const errorInfo: SessionInfo = {
          can_access: false,
          message: 'An unknown error occurred.',
          sessions_remaining: 0,
          is_judge: false,
          device_id: 'error'
        };
        return of(errorInfo);
      }),
      tap(sessionInfo => {
        // Update the central state.
        console.log('Session info updated:', sessionInfo);
        this.sessionInfoSubject.next(sessionInfo);
      })
    );
  }

  /**
   * Verifies a judge code and then immediately refreshes the session state.
   * Uses switchMap to avoid race conditions, ensuring the session check
   * completes before this observable chain finishes.
   */
  verifyJudgeCode(code: string): Observable<SessionInfo> {
    const url = this.getApiUrl('api/verify-judge');
    console.log('Verifying judge code at:', url);
    
    const request: JudgeVerificationRequest = { code };
    return this.http.post<JudgeVerificationResponse>(url, request).pipe(
      switchMap(response => {
        console.log('Judge verification response:', response);
        if (response.valid) {
          // If the code is valid, immediately fetch the new session status.
          return this.checkSessionStatus();
        }
        // If the code is invalid, return an observable that emits the current
        // (unchanged) session state, or a default if the state is null.
        return of(this.sessionInfoSubject.getValue() ?? this.getNoAccessState());
      }),
      catchError((error: HttpErrorResponse) => {
        console.error('Judge code verification failed:', error);
        // If the verification fails, return the current state or a default.
        return of(this.sessionInfoSubject.getValue() ?? this.getNoAccessState());
      })
    );
  }

  /**
   * Checks if the user is authorized to access the main application.
   * This is used by the AuthGuard.
   */
  async isAuthorized(): Promise<boolean> {
    // Get the most recent session info, or fetch if it doesn't exist yet.
    let info = this.sessionInfoSubject.getValue();
    if (!info) {
      info = await firstValueFrom(this.checkSessionStatus());
    }
    return info.can_access;
  }

  /**
   * Handles API errors for session-consuming endpoints.
   */
  handleApiError(error: HttpErrorResponse): Observable<never> {
    if (error.status === 429) {
      console.error('Session limit exceeded. Redirecting to landing page.');
      // Update our own state to reflect the lockout.
      this.checkSessionStatus().subscribe(() => {
        this.router.navigate(['/']);
      });
    }
    return throwError(() => error);
  }

  private getNoAccessState(): SessionInfo {
    return {
      can_access: false,
      message: 'Authentication state not available.',
      sessions_remaining: 0,
      is_judge: false,
      device_id: 'error'
    };
  }
} 