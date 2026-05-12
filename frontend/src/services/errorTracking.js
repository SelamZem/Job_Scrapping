/**
 * Error tracking service for production monitoring
 */

const isProduction = import.meta.env.PROD;

class ErrorTracker {
  constructor() {
    this.errors = [];
    this.setupGlobalErrorHandling();
  }

  setupGlobalErrorHandling() {
    // Catch unhandled promise rejections
    window.addEventListener('unhandledrejection', (event) => {
      this.logError('Unhandled Promise Rejection', {
        error: event.reason,
        stack: event.reason?.stack,
        url: window.location.href
      });
    });

    // Catch uncaught JavaScript errors
    window.addEventListener('error', (event) => {
      this.logError('JavaScript Error', {
        error: event.error?.message,
        stack: event.error?.stack,
        url: window.location.href,
        line: event.lineno,
        column: event.colno
      });
    });
  }

  logError(type, details) {
    const errorData = {
      timestamp: new Date().toISOString(),
      type,
      environment: isProduction ? 'production' : 'development',
      userAgent: navigator.userAgent,
      url: details.url,
      ...details
    };

    // Log to console in development
    if (!isProduction) {
      console.error('🚨 Error:', errorData);
      return;
    }

    // Send to error tracking service in production
    if (isProduction) {
      this.sendToErrorService(errorData);
    }

    this.errors.push(errorData);
  }

  sendToErrorService(errorData) {
    // You can integrate with services like Sentry, LogRocket, etc.
    // For now, we'll store in localStorage for debugging
    try {
      const existingErrors = JSON.parse(localStorage.getItem('app_errors') || '[]');
      existingErrors.push(errorData);
      
      // Keep only last 50 errors
      const recentErrors = existingErrors.slice(-50);
      localStorage.setItem('app_errors', JSON.stringify(recentErrors));
    } catch (e) {
      console.error('Failed to log error:', e);
    }
  }

  getRecentErrors() {
    try {
      return JSON.parse(localStorage.getItem('app_errors') || '[]');
    } catch (e) {
      return [];
    }
  }

  clearErrors() {
    localStorage.removeItem('app_errors');
    this.errors = [];
  }
}

export default new ErrorTracker();
