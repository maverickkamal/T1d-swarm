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

import {platformBrowserDynamic} from '@angular/platform-browser-dynamic';
import {AppModule} from './app/app.module';

fetch('./assets/config/runtime-config.json')
  .then((response) => response.json())
  .then((config) => {
    console.log('Runtime config loaded:', config);
    (window as any)['runtimeConfig'] = config;
    return platformBrowserDynamic().bootstrapModule(AppModule);
  })
  .catch((err) => {
    console.error('Failed to load runtime config, using defaults:', err);
    // Fallback: set default config if loading fails
    (window as any)['runtimeConfig'] = { backendUrl: 'http://localhost:8080' };
    return platformBrowserDynamic().bootstrapModule(AppModule);
  })
  .catch((err) => console.error('Bootstrap failed:', err));
