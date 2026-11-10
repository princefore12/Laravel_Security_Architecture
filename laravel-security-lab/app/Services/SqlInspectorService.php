<?php

namespace App\Services;

use App\Models\SecurityLog;
use Illuminate\Database\Events\QueryExecuted;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\DB;

class SqlInspectorService
{
    /**
     * Exécute un callback tout en capturant les requêtes SQL envoyées à MariaDB/SQLite.
     *
     * @return array{result: mixed, queries: array<int, array<string, mixed>>}
     */
    public function capture(callable $callback): array
    {
        $queries = [];
        $capturing = true;

        DB::listen(function (QueryExecuted $query) use (&$queries, &$capturing): void {
            if (! $capturing) {
                return;
            }
            // Ignorer les requêtes internes de table sessions/logs si bruyantes
            if (str_contains($query->sql, 'security_logs') || str_contains($query->sql, '`sessions`') || str_contains($query->sql, '"sessions"')) {
                return;
            }

            $queries[] = [
                'sql' => $query->sql,
                'bindings' => $query->bindings,
                'rendered' => $this->interpolate($query->sql, $query->bindings),
                'time_ms' => $query->time,
            ];
        });

        try {
            $result = $callback();
        } finally {
            $capturing = false;
        }

        return [
            'result' => $result,
            'queries' => $queries,
        ];
    }

    public function record(
        Request $request,
        string $pillar,
        string $mode,
        string $actor,
        ?string $payload,
        array $queries,
        string $outcome
    ): void {
        $sqlSummary = collect($queries)
            ->map(fn (array $q): string => $q['rendered'])
            ->implode(" ;\n");

        SecurityLog::create([
            'pillar' => $pillar,
            'mode' => $mode,
            'actor' => $actor,
            'payload' => $payload,
            'executed_sql' => $sqlSummary ?: null,
            'outcome' => $outcome,
            'ip_address' => $request->ip(),
        ]);
    }

    private function interpolate(string $sql, array $bindings): string
    {
        $rendered = $sql;
        foreach ($bindings as $binding) {
            $value = is_numeric($binding)
                ? (string) $binding
                : "'" . str_replace("'", "\\'", (string) $binding) . "'";
            $rendered = preg_replace('/\?/', $value, $rendered, 1) ?? $rendered;
        }

        return $rendered;
    }
}
