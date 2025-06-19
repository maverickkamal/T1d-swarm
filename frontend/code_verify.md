Perfect! Here's the Angular version:

**Create a service (access-control.service.ts):**
```typescript
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
      this.verifyJudgeCode(savedCode);
      return;
    }

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
}
```

**Create access prompt component (access-prompt.component.ts):**
```typescript
import { Component, EventEmitter, Output } from '@angular/core';
import { AccessControlService } from './access-control.service';

@Component({
  selector: 'app-access-prompt',
  template: `
    <div class="overlay">
      <div class="prompt-container">
        <h3>Access Demo</h3>
        <p>Enter judge code for full access, or leave blank for demo (1 use only)</p>
        <input 
          type="text" 
          [(ngModel)]="judgeCode"
          placeholder="Judge code (optional)"
          class="code-input"
          (keyup.enter)="handleSubmit()"
        />
        <br />
        <button (click)="handleSubmit()" class="continue-btn">
          Continue
        </button>
      </div>
    </div>
  `,
  styles: [`
    .overlay {
      position: fixed;
      top: 0; left: 0; right: 0; bottom: 0;
      background: rgba(0,0,0,0.8);
      display: flex;
      align-items: center;
      justify-content: center;
      z-index: 1000;
    }
    .prompt-container {
      background: white;
      padding: 30px;
      border-radius: 10px;
      text-align: center;
      max-width: 400px;
    }
    .code-input {
      padding: 10px;
      width: 200px;
      margin: 10px;
      border: 1px solid #ccc;
      border-radius: 5px;
    }
    .continue-btn {
      padding: 10px 20px;
      background: #007bff;
      color: white;
      border: none;
      border-radius: 5px;
      cursor: pointer;
    }
  `]
})
export class AccessPromptComponent {
  judgeCode: string = '';

  constructor(private accessService: AccessControlService) {}

  handleSubmit(): void {
    if (!this.judgeCode || this.judgeCode.trim() === '') {
      this.accessService.useDemoAccess();
    } else {
      this.accessService.verifyJudgeCode(this.judgeCode).subscribe({
        next: () => {
          // Success handled in service
        },
        error: (error) => {
          alert(error);
        }
      });
    }
  }
}
```

**Update your main app component (app.component.ts):**
```typescript
import { Component, OnInit } from '@angular/core';
import { AccessControlService, AccessLevel } from './access-control.service';

@Component({
  selector: 'app-root',
  template: `
    <!-- Access prompt -->
    <app-access-prompt *ngIf="accessLevel === null"></app-access-prompt>
    
    <!-- Blocked message -->
    <div *ngIf="accessLevel === 'blocked'" class="blocked-message">
      <h2>Demo Usage Limit Reached</h2>
      <p>This demo has already been used on this device. Contact organizers for judge access.</p>
    </div>

    <!-- Main app -->
    <div *ngIf="accessLevel === 'demo' || accessLevel === 'judge'">
      <!-- Status banner -->
      <div *ngIf="accessLevel === 'demo'" class="demo-banner">
        ⚠️ Demo Mode - Limited functionality
      </div>
      <div *ngIf="accessLevel === 'judge'" class="judge-banner">
        ✅ Judge Access - All features enabled
      </div>

      <!-- Your existing app content -->
      <router-outlet></router-outlet>
    </div>
  `,
  styles: [`
    .blocked-message {
      text-align: center;
      padding: 50px;
    }
    .demo-banner {
      background: #fff3cd;
      padding: 10px;
      text-align: center;
      border-bottom: 1px solid #ffeaa7;
    }
    .judge-banner {
      background: #d4edda;
      padding: 10px;
      text-align: center;
      border-bottom: 1px solid #c3e6cb;
    }
  `]
})
export class AppComponent implements OnInit {
  accessLevel: AccessLevel = null;

  constructor(private accessService: AccessControlService) {}

  ngOnInit(): void {
    this.accessService.accessLevel$.subscribe(level => {
      this.accessLevel = level;
    });
  }
}
```

**Don't forget to add FormsModule to your app.module.ts:**
```typescript
import { FormsModule } from '@angular/forms';

@NgModule({
  imports: [FormsModule, /* other imports */],
  // ...
})
```

**Backend stays the same:**
```python
from fastapi import FastAPI
from pydantic import BaseModel
import os

app = FastAPI()

class JudgeCodeRequest(BaseModel):
    code: str

JUDGE_CODES = os.getenv("JUDGE_CODES", "").split(",")

@app.post("/api/verify-judge")
def verify_judge_code(request: JudgeCodeRequest):
    if request.code in JUDGE_CODES:
        return {"valid": True}
    else:
        return {"valid": False}, 401
```

This gives you the same functionality - judges get unlimited access, public gets 1 demo use that persists across browser sessions!