import { Component, EventEmitter, Output } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { CommonModule } from '@angular/common';
import { AccessControlService } from '../../core/services/access-control.service';

@Component({
  selector: 'app-access-prompt',
  templateUrl: './access-prompt.component.html',
  styleUrls: ['./access-prompt.component.scss'],
  standalone: true,
  imports: [CommonModule, FormsModule]
})
export class AccessPromptComponent {
  judgeCode: string = '';
  isLoading: boolean = false;
  errorMessage: string = '';

  constructor(private accessService: AccessControlService) {}

  handleSubmit(): void {
    if (this.isLoading) return;

    this.errorMessage = '';
    this.isLoading = true;

    if (!this.judgeCode || this.judgeCode.trim() === '') {
      // Use demo access
      this.accessService.useDemoAccess();
      this.isLoading = false;
    } else {
      // Verify judge code
      this.accessService.verifyJudgeCode(this.judgeCode).subscribe({
        next: () => {
          this.isLoading = false;
        },
        error: (error) => {
          this.errorMessage = error;
          this.isLoading = false;
        }
      });
    }
  }

  onKeyPress(event: KeyboardEvent): void {
    if (event.key === 'Enter') {
      this.handleSubmit();
    }
  }
} 