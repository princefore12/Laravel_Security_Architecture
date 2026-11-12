<?php

namespace App\Http\Middleware;

use App\Support\SecurityConfig;
use Closure;
use Illuminate\Http\Request;
use Symfony\Component\HttpFoundation\Response;

class EnsureLocalLabMiddleware
{
    public function handle(Request $request, Closure $next): Response
    {
        if (app()->environment('testing')) {
            return $next($request);
        }

        $enabled = SecurityConfig::readEnvBool('LAB_DEMO_ENABLED', true);
        $allowedIps = ['127.0.0.1', '::1'];

        if (! app()->environment('local') || ! $enabled || ! in_array($request->ip(), $allowedIps, true)) {
            abort(403, 'Accès strictement réservé à l\'environnement local de démonstration.');
        }

        return $next($request);
    }
}
