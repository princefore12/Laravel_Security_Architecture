<?php

use App\Http\Controllers\Portal\AuthController;
use App\Http\Controllers\Portal\CampusController;
use App\Http\Controllers\Portal\DirectoryController;
use App\Http\Controllers\Portal\GradeController;
use App\Http\Controllers\Portal\ProfileController;
use Illuminate\Support\Facades\Route;

// Portail public UT LOKO
Route::get('/', [DirectoryController::class, 'home'])->name('portal.home');
Route::get('/annuaire', [DirectoryController::class, 'index'])->name('portal.directory');
Route::get('/api/annuaire', [DirectoryController::class, 'api'])->name('portal.api.directory');
Route::get('/campus', [CampusController::class, 'index'])->name('portal.campus');

// Authentification
Route::get('/connexion', [AuthController::class, 'showLogin'])->name('login');
Route::post('/connexion', [AuthController::class, 'login'])->name('portal.login.submit');
Route::post('/deconnexion', [AuthController::class, 'logout'])->name('portal.logout');

// Espace étudiant & administration authentifié
Route::middleware(['auth'])->group(function (): void {
    Route::get('/profil', [ProfileController::class, 'edit'])->name('portal.profile');
    Route::post('/profil', [ProfileController::class, 'update'])->name('portal.profile.update');

    Route::post('/campus', [CampusController::class, 'store'])->name('portal.campus.store');

    Route::get('/mes-notes', [GradeController::class, 'myGrade'])->name('portal.my-grades');
    Route::get('/bulletins/{grade}', [GradeController::class, 'show'])->name('portal.grades.show');

    Route::get('/admin/notes', [GradeController::class, 'adminIndex'])->name('portal.admin.grades');
    Route::post('/notes/{grade}/modifier', [GradeController::class, 'updateScore'])->name('portal.grades.update');
});
