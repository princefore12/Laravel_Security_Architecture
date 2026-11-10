<?php

namespace App\Http\Middleware;

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

        $enabled = filter_var(env('LAB_DEMO_ENABLED', false), FILTER_VALIDATE_BOOLEAN);
        $allowedIps = ['127.0.0.1', '::1'];

        if (! app()->environment('local') || ! $enabled || ! in_array($request->ip(), $allowedIps, true)) {
            abort(403, 'Le laboratoire LOKO-Vault est strictement réservé à l\'environnement pédagogique local.');
        }

        return $next($request);
    }
}
