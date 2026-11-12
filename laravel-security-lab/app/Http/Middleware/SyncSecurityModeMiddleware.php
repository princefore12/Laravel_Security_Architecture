<?php

namespace App\Http\Middleware;

use App\Support\SecurityConfig;
use Closure;
use Illuminate\Http\Request;
use Symfony\Component\HttpFoundation\Response;

class SyncSecurityModeMiddleware
{
    public function handle(Request $request, Closure $next): Response
    {
        $hardened = SecurityConfig::isHardened();

        config([
            'security.hardened' => $hardened,
            'app.debug' => $hardened ? false : SecurityConfig::readEnvBool('APP_DEBUG', true),
            'session.http_only' => $hardened,
            'session.same_site' => 'lax',
        ]);

        return $next($request);
    }
}
