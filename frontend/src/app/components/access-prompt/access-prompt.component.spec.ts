import { ComponentFixture, TestBed } from '@angular/core/testing';
import { FormsModule } from '@angular/forms';
import { HttpClientTestingModule } from '@angular/common/http/testing';

import { AccessPromptComponent } from './access-prompt.component';
import { AccessControlService } from '../../core/services/access-control.service';

describe('AccessPromptComponent', () => {
  let component: AccessPromptComponent;
  let fixture: ComponentFixture<AccessPromptComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ AccessPromptComponent ],
      imports: [ FormsModule, HttpClientTestingModule ],
      providers: [ AccessControlService ]
    })
    .compileComponents();

    fixture = TestBed.createComponent(AccessPromptComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
}); 