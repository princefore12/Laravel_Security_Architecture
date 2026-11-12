<?php

use App\Http\Middleware\DynamicCsrfMiddleware;
use App\Http\Middleware\EnsureLocalLabMiddleware;
use App\Http\Middleware\SecurityHeadersMiddleware;
use App\Http\Middleware\SyncSecurityModeMiddleware;
use Illuminate\Foundation\Application;
use Illuminate\Foundation\Configuration\Exceptions;
use Illuminate\Foundation\Configuration\Middleware;
use Illuminate\Foundation\Http\Middleware\PreventRequestForgery;
use Illuminate\Http\Request;
use Illuminate\Session\Middleware\StartSession;

return Application::configure(basePath: dirname(__DIR__))
    ->withRouting(
        web: __DIR__.'/../routes/web.php',
        commands: __DIR__.'/../routes/console.php',
        health: '/up',
    )
    ->withMiddleware(function (Middleware $middleware): void {
        $middleware->web(
            prepend: [
                SyncSecurityModeMiddleware::class,
                EnsureLocalLabMiddleware::class,
            ],
            append: [
                SecurityHeadersMiddleware::class,
            ],
            replace: [
                PreventRequestForgery::class => DynamicCsrfMiddleware::class,
            ],
        );

        $middleware->prependToPriorityList(StartSession::class, SyncSecurityModeMiddleware::class);
        $middleware->appendToPriorityList(StartSession::class, DynamicCsrfMiddleware::class);
    })
    ->withExceptions(function (Exceptions $exceptions): void {
        $exceptions->shouldRenderJsonWhen(
            fn (Request $request) => $request->is('api/*') || $request->expectsJson(),
        );
    })->create();
