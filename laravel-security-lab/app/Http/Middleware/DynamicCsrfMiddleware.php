<?php

namespace App\Http\Middleware;

use App\Support\SecurityConfig;
use Illuminate\Foundation\Http\Middleware\ValidateCsrfToken;

class DynamicCsrfMiddleware extends ValidateCsrfToken
{
    /**
     * Lorsque SECURITY_HARDENED=false, la route de modification des notes est
     * volontairement exemptée (simulation d'une exclusion dangereuse dans app.php).
     */
    protected function inExceptArray($request): bool
    {
        if (! SecurityConfig::isHardened() && $request->is('notes/*/modifier')) {
            return true;
        }

        return parent::inExceptArray($request);
    }
}
