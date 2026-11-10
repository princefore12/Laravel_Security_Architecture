<?php

use App\Http\Controllers\Lab\AccessControlController;
use App\Http\Controllers\Lab\CsrfController;
use App\Http\Controllers\Lab\LabDashboardController;
use App\Http\Controllers\Lab\MassAssignmentController;
use App\Http\Controllers\Lab\SqlInjectionController;
use App\Http\Controllers\Lab\XssController;
use Illuminate\Support\Facades\Route;

Route::middleware(['lab.local'])->group(function (): void {
    Route::get('/', [LabDashboardController::class, 'index'])->name('lab.dashboard');
    Route::post('/lab/reset', [LabDashboardController::class, 'reset'])->name('lab.reset');

    // Pilier 1 : Injection SQL (Sore Ramatou)
    Route::get('/lab/sqli', [SqlInjectionController::class, 'index'])->name('lab.sqli');

    // Pilier 2 : Mass Assignment & FormRequest (Siby Mody)
    Route::get('/lab/mass-assignment', [MassAssignmentController::class, 'index'])->name('lab.mass-assignment');
    Route::post('/lab/mass-assignment/vulnerable', [MassAssignmentController::class, 'updateVulnerable'])->name('lab.mass-assignment.vulnerable');
    Route::post('/lab/mass-assignment/secure', [MassAssignmentController::class, 'updateSecure'])->name('lab.mass-assignment.secure');
    Route::post('/lab/mass-assignment/reset-role', [MassAssignmentController::class, 'resetRole'])->name('lab.mass-assignment.reset-role');

    // Pilier 3 : XSS Stocké & Blade + CSP (Boin Naomi)
    Route::get('/lab/xss', [XssController::class, 'indexVulnerable'])->name('lab.xss.vulnerable');
    Route::get('/lab/xss/secure', [XssController::class, 'indexSecure'])->middleware('lab.headers')->name('lab.xss.secure');
    Route::post('/lab/xss/store', [XssController::class, 'store'])->name('lab.xss.store');
    Route::post('/lab/xss/reset-bio', [XssController::class, 'resetBio'])->name('lab.xss.reset-bio');

    // Pilier 4 : CSRF & Sessions (Traoré Charifat Leyla)
    Route::get('/lab/csrf', [CsrfController::class, 'index'])->name('lab.csrf');
    Route::get('/lab/csrf/evil-site', [CsrfController::class, 'evilSite'])->name('lab.csrf.evil');
    Route::post('/lab/csrf/vulnerable-update', [CsrfController::class, 'updateVulnerable'])->name('lab.csrf.vulnerable-update');
    Route::post('/lab/csrf/secure-update', [CsrfController::class, 'updateSecure'])->name('lab.csrf.secure-update');
    Route::post('/lab/csrf/reset-grade', [CsrfController::class, 'resetGrade'])->name('lab.csrf.reset-grade');

    // Pilier 5 : Auth, Bcrypt, IDOR / Policies & RateLimiter (Djan Kouassi Noël)
    Route::get('/lab/access-control', [AccessControlController::class, 'index'])->name('lab.access');
    Route::post('/lab/access-control/actor', [AccessControlController::class, 'switchActor'])->name('lab.access.actor');
    Route::get('/lab/access-control/vulnerable/grades/{grade}', [AccessControlController::class, 'showGradeVulnerable'])->name('lab.access.grade.vulnerable');
    Route::get('/lab/access-control/secure/grades/{grade}', [AccessControlController::class, 'showGradeSecure'])->name('lab.access.grade.secure');
    Route::post('/lab/access-control/hash', [AccessControlController::class, 'compareHash'])->name('lab.access.hash');
    Route::post('/lab/access-control/rate-limit', [AccessControlController::class, 'attemptLogin'])->name('lab.access.rate-limit');
    Route::post('/lab/access-control/rate-limit/clear', [AccessControlController::class, 'clearRateLimit'])->name('lab.access.rate-limit.clear');
});
