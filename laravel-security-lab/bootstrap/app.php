<?php

use App\Http\Middleware\EnsureLocalLabMiddleware;
use App\Http\Middleware\SecurityHeadersMiddleware;
use Illuminate\Foundation\Application;
use Illuminate\Foundation\Configuration\Exceptions;
use Illuminate\Foundation\Configuration\Middleware;
use Illuminate\Http\Request;

return Application::configure(basePath: dirname(__DIR__))
    ->withRouting(
        web: __DIR__.'/../routes/web.php',
        commands: __DIR__.'/../routes/console.php',
        health: '/up',
    )
    ->withMiddleware(function (Middleware $middleware): void {
        // Exception pédagogique volontaire pour démontrer la faille CSRF sur l'Atelier 4 uniquement
        $middleware->validateCsrfTokens(except: [
            'lab/csrf/vulnerable-update',
        ]);

        $middleware->alias([
            'lab.local' => EnsureLocalLabMiddleware::class,
            'lab.headers' => SecurityHeadersMiddleware::class,
        ]);
    })
    ->withExceptions(function (Exceptions $exceptions): void {
        $exceptions->shouldRenderJsonWhen(
            fn (Request $request) => $request->is('api/*') || $request->expectsJson(),
        );
    })->create();
