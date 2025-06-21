import { Component, OnInit, OnDestroy } from '@angular/core';
import { Router } from '@angular/router';
import { Subscription } from 'rxjs';
import { AuthService } from '../../core/services/auth.service';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { SessionInfo } from '../../core/models/auth.types';

@Component({
  selector: 'app-landing-page',
  templateUrl: './landing-page.component.html',
  styleUrls: ['./landing-page.component.scss'],
  standalone: true,
  imports: [CommonModule, FormsModule],
})
export class LandingPageComponent implements OnInit, OnDestroy {
  judgeCode = '';
  isVerifying = false;
  message = '';
  messageType: 'success' | 'error' = 'error';
  sessionsRemaining = 3; // Default assumption
  private sessionSub!: Subscription;

  constructor(private authService: AuthService, private router: Router) {}

  ngOnInit(): void {
    // Subscribe to session updates to keep the UI fresh.
    this.sessionSub = this.authService.sessionInfo$.subscribe(info => {
      if (info) {
        this.sessionsRemaining = info.sessions_remaining;
        // If a user with judge access lands here, send them away.
        if (info.is_judge) {
          this.router.navigate(['/chat']);
        }
      }
    });
    // Trigger the initial check.
    this.authService.checkSessionStatus().subscribe();
  }

  ngOnDestroy(): void {
    if (this.sessionSub) {
      this.sessionSub.unsubscribe();
    }
  }

  verifyJudgeCode(): void {
    if (!this.judgeCode.trim()) return;

    this.isVerifying = true;
    this.message = '';

    this.authService.verifyJudgeCode(this.judgeCode).subscribe({
      next: (sessionInfo) => {
        this.isVerifying = false;
        if (sessionInfo?.is_judge) {
          this.message = 'Success! Redirecting to the application...';
          this.messageType = 'success';
          setTimeout(() => this.router.navigate(['/chat']), 1500);
        } else {
          this.message = 'Invalid judge code. Please try again.';
          this.messageType = 'error';
        }
      },
      error: () => {
        this.isVerifying = false;
        this.message = 'An error occurred during verification.';
        this.messageType = 'error';
      }
    });
  }

  continueAsGuest(): void {
    // The AuthGuard will handle the redirection logic. We just need to navigate.
    // We check the latest value from the service to prevent users from clicking
    // the button if they have no sessions left.
    if (this.sessionsRemaining > 0) {
      this.router.navigate(['/chat']);
    } else {
      this.message = 'No guest sessions remaining. Please use a judge code.';
      this.messageType = 'error';
    }
  }
} 