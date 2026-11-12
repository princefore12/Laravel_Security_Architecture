<?php

namespace App\Support;

class SecurityConfig
{
    /**
     * Détermine dynamiquement si les défenses Laravel sont actives.
     * En local, relit directement le fichier .env à chaque requête pour qu'une
     * modification dans VS Code (Ctrl+S) prenne effet dès le F5 sans redémarrer php -S.
     */
    public static function isHardened(): bool
    {
        if (app()->environment('testing')) {
            return filter_var(config('security.hardened', false), FILTER_VALIDATE_BOOLEAN);
        }

        $envFile = base_path('.env');
        if (is_file($envFile)) {
            $content = file_get_contents($envFile);
            if ($content !== false && preg_match('/^\s*SECURITY_HARDENED\s*=\s*(.+)$/m', $content, $matches)) {
                $value = trim($matches[1], " \t\n\r\0\x0B\"'");

                return filter_var($value, FILTER_VALIDATE_BOOLEAN);
            }
        }

        return filter_var(config('security.hardened', false), FILTER_VALIDATE_BOOLEAN);
    }

    /**
     * Lit une variable booléenne libre dans .env (ex. APP_DEBUG).
     */
    public static function readEnvBool(string $key, bool $default = false): bool
    {
        if (app()->environment('testing')) {
            return $default;
        }

        $envFile = base_path('.env');
        if (is_file($envFile)) {
            $content = file_get_contents($envFile);
            $pattern = '/^\s*' . preg_quote($key, '/') . '\s*=\s*(.+)$/m';
            if ($content !== false && preg_match($pattern, $content, $matches)) {
                $value = trim($matches[1], " \t\n\r\0\x0B\"'");

                return filter_var($value, FILTER_VALIDATE_BOOLEAN);
            }
        }

        return $default;
    }
}
