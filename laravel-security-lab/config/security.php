<?php

return [
    /*
    |--------------------------------------------------------------------------
    | Mode de durcissement sécuritaire (Portail UT LOKO)
    |--------------------------------------------------------------------------
    | false : l'application reproduit volontairement des erreurs classiques de
    |         développement pour la démonstration en direct.
    | true  : active toutes les défenses natives de Laravel (PDO, FormRequest,
    |         $fillable, échappement Blade, CSP, HttpOnly, @csrf, Policy, RateLimiter).
    */
    'hardened' => filter_var(env('SECURITY_HARDENED', false), FILTER_VALIDATE_BOOLEAN),
];
