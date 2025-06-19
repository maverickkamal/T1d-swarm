import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { BehaviorSubject, Observable } from 'rxjs';

export type AccessLevel = 'judge' | 'demo' | 'blocked' | null;

@Injectable({
  providedIn: 'root'
})
export class AccessControlService {
  private readonly DEMO_USES_KEY = 'demo_usage_count';
  private readonly JUDGE_CODE_KEY = 'judge_access_code';
  
  private accessLevelSubject = new BehaviorSubject<AccessLevel>(null);
  public accessLevel$ = this.accessLevelSubject.asObservable();

  constructor(private http: HttpClient) {
    this.checkAccess();
  }

  checkAccess(): void {
    // Check if judge code already saved
    const savedCode = localStorage.getItem(this.JUDGE_CODE_KEY);
    if (savedCode) {
      this.verifyJudgeCode(savedCode).subscribe({
        next: () => {
          // Success handled in verifyJudgeCode
        },
        error: () => {
          // Invalid saved code, remove it
          localStorage.removeItem(this.JUDGE_CODE_KEY);
          this.checkDemoAccess();
        }
      });
      return;
    }

    this.checkDemoAccess();
  }

  private checkDemoAccess(): void {
    // Check demo usage
    const demoCount = parseInt(localStorage.getItem(this.DEMO_USES_KEY) || '0');
    if (demoCount >= 1) {
      this.accessLevelSubject.next('blocked');
      return;
    }

    // Need to show prompt
    this.accessLevelSubject.next(null);
  }

  verifyJudgeCode(code: string): Observable<any> {
    return new Observable(observer => {
      this.http.post('/api/verify-judge', { code }).subscribe({
        next: (response) => {
          localStorage.setItem(this.JUDGE_CODE_KEY, code);
          this.accessLevelSubject.next('judge');
          observer.next(true);
          observer.complete();
        },
        error: (error) => {
          observer.error('Invalid judge code');
        }
      });
    });
  }

  useDemoAccess(): void {
    const currentCount = parseInt(localStorage.getItem(this.DEMO_USES_KEY) || '0');
    localStorage.setItem(this.DEMO_USES_KEY, (currentCount + 1).toString());
    this.accessLevelSubject.next('demo');
  }

  isJudgeAccess(): boolean {
    return this.accessLevelSubject.value === 'judge';
  }

  isDemoAccess(): boolean {
    return this.accessLevelSubject.value === 'demo';
  }

  isBlocked(): boolean {
    return this.accessLevelSubject.value === 'blocked';
  }

  getCurrentAccessLevel(): AccessLevel {
    return this.accessLevelSubject.value;
  }

  resetDemoUsage(): void {
    localStorage.removeItem(this.DEMO_USES_KEY);
    this.checkAccess();
  }

  clearJudgeCode(): void {
    localStorage.removeItem(this.JUDGE_CODE_KEY);
    this.checkAccess();
  }
} 