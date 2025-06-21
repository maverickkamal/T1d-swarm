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

/**
 * Represents the response from the /api/check-access endpoint.
 */
export interface SessionInfo {
  can_access: boolean;
  message: string;
  sessions_remaining: number;
  device_id: string;
  is_judge: boolean;
}

/**
 * Represents the response from the /api/verify-judge endpoint.
 */
export interface JudgeVerificationResponse {
  valid: boolean;
  message: string;
  sessions_remaining?: number;
  is_judge?: boolean;
}

/**
 * Represents the request body for judge verification.
 */
export interface JudgeVerificationRequest {
  code: string;
}

/**
 * Represents the error response when session limit is exceeded.
 */
export interface SessionLimitError {
  error: string;
  message: string;
  sessions_remaining: number;
  solution: string;
} 