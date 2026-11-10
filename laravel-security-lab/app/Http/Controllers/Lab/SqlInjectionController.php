<?php

namespace App\Http\Controllers\Lab;

use App\Http\Controllers\Controller;
use App\Models\Student;
use App\Services\SqlInspectorService;
use Illuminate\Database\QueryException;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\DB;
use Illuminate\View\View;

class SqlInjectionController extends Controller
{
    public function __construct(private readonly SqlInspectorService $inspector)
    {
    }

    public function index(Request $request): View
    {
        $mode = $request->query('mode', 'vulnerable') === 'secure' ? 'secure' : 'vulnerable';
        $query = $request->query('q', '');
        $rows = [];
        $queries = [];
        $sqlError = null;
        $statusBadge = null;

        if ($query !== '') {
            if ($mode === 'vulnerable') {
                try {
                    $captured = $this->inspector->capture(function () use ($query): array {
                        // VOLONTAIREMENT VULNÉRABLE : concaténation directe dans SQL brut
                        return DB::select(
                            "SELECT id, matricule, full_name, filiere, moyenne FROM students WHERE matricule = '{$query}'"
                        );
                    });
                    $rows = $captured['result'];
                    $queries = $captured['queries'];

                    $isInjection = count($rows) > 1 || str_contains(strtoupper($query), 'UNION') || str_contains($query, "'");
                    $outcome = ($isInjection && count($rows) > 0) ? 'exploited' : 'info';
                    $statusBadge = $outcome === 'exploited'
                        ? 'FAILLE EXPLOITÉE : MariaDB a exécuté la logique SQL injectée (' . count($rows) . ' lignes retournées) !'
                        : count($rows) . ' résultat(s) trouvé(s).';

                    $this->inspector->record($request, '1. Injection SQL', 'vulnerable', 'Sore Ramatou', $query, $queries, $outcome);
                } catch (QueryException $e) {
                    $sqlError = $e->getMessage();
                    $this->inspector->record($request, '1. Injection SQL', 'vulnerable', 'Sore Ramatou', $query, [], 'info');
                }
            } else {
                $captured = $this->inspector->capture(function () use ($query) {
                    // SÉCURISÉ : Eloquent ORM utilise automatiquement PDO + bindings préparés (?)
                    return Student::query()
                        ->where('matricule', $query)
                        ->get(['id', 'matricule', 'full_name', 'filiere', 'moyenne']);
                });
                $rows = $captured['result'];
                $queries = $captured['queries'];

                $looksMalicious = str_contains($query, "'") || str_contains(strtoupper($query), 'UNION');
                $outcome = $looksMalicious ? 'blocked' : 'info';
                $statusBadge = $looksMalicious
                    ? 'ATTAQUE NEUTRALISÉE : PDO a isolé le payload dans un paramètre lié (?) — 0 ligne fuite !'
                    : count($rows) . ' résultat(s) trouvé(s) via requête préparée.';

                $this->inspector->record($request, '1. Injection SQL', 'secure', 'Sore Ramatou', $query, $queries, $outcome);
            }
        }

        return view('lab.sqli', [
            'mode' => $mode,
            'query' => $query,
            'rows' => $rows,
            'queries' => $queries,
            'sqlError' => $sqlError,
            'statusBadge' => $statusBadge,
            'allMatricules' => Student::query()->pluck('matricule'),
        ]);
    }
}
