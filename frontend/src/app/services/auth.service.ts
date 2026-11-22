import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

@Injectable({
  providedIn: 'root'
})
export class AuthService {
  private apiUrl = 'http://127.0.0.1:8000/auth';

  constructor(private http: HttpClient) { }

  login(credentials: any): Observable<any> {
    return this.http.post(`${this.apiUrl}/login`, credentials);
  }

    setRol(rol: string) {
    if (typeof window !== 'undefined' && window.localStorage) {
      localStorage.setItem('rol', rol);
    }
  }

  getRol(): string | null {
    if (typeof window !== 'undefined' && window.localStorage) {
      return localStorage.getItem('rol');
    }
    return null;
  }

  logout() {
    if (typeof window !== 'undefined' && window.localStorage) {
      localStorage.removeItem('rol');
    }
  }
}