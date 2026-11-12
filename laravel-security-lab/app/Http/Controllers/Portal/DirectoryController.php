<?php

namespace App\Http\Controllers\Portal;

use App\Http\Controllers\Controller;
use App\Models\CampusPost;
use App\Models\Student;
use App\Services\SqlInspectorService;
use App\Support\SecurityConfig;
use Illuminate\Http\JsonResponse;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\DB;
use Illuminate\View\View;

class DirectoryController extends Controller
{
    public function __construct(private readonly SqlInspectorService $inspector)
    {
    }

    public function home(): View
    {
        return view('portal.home', [
            'studentCount' => Student::query()->count(),
            'recentPosts' => CampusPost::query()->latest('id')->limit(3)->get(),
        ]);
    }

    public function index(Request $request): View
    {
        $q = trim((string) $request->query('q', ''));
        $sort = (string) $request->query('sort', 'matricule');
        $hardened = SecurityConfig::isHardened();

        $rows = $this->runDirectoryQuery($q, $sort, $hardened, $request);

        return view('portal.directory', [
            'students' => $rows,
            'search' => $q,
            'sort' => $sort,
        ]);
    }

    public function api(Request $request): JsonResponse
    {
        $q = trim((string) $request->query('q', ''));
        $sort = (string) $request->query('sort', 'matricule');
        $hardened = SecurityConfig::isHardened();

        $rows = $this->runDirectoryQuery($q, $sort, $hardened, $request);

        return response()->json([
            'status' => 'ok',
            'count' => count($rows),
            'students' => $rows,
        ]);
    }

    /**
     * @return array<int, object>
     */
    private function runDirectoryQuery(string $q, string $sort, bool $hardened, Request $request): array
    {
        if (! $hardened) {
            $captured = $this->inspector->capture(function () use ($q, $sort): array {
                if ($q === '') {
                    return DB::select(
                        "SELECT id, matricule, full_name, filiere, moyenne FROM students ORDER BY {$sort} ASC"
                    );
                }

                $targetExpr = DB::getDriverName() === 'sqlite'
                    ? "(matricule || ' ' || full_name)"
                    : "CONCAT(matricule, ' ', full_name)";

                // VOLONTAIREMENT VULNÉRABLE : concaténation directe permettant erreurs SQL, OR '1'='1 et UNION SELECT
                return DB::select(
                    "SELECT id, matricule, full_name, filiere, moyenne FROM students WHERE {$targetExpr} LIKE '%{$q}%' ORDER BY {$sort} ASC"
                );
            });

            $looksMalicious = preg_match("/('|\"|union|select|--)/i", $q . ' ' . $sort) === 1;
            if ($looksMalicious) {
                $this->inspector->record(
                    $request,
                    '1. Injection SQL (Annuaire)',
                    'vulnerable',
                    $request->user()?->name ?? 'Visiteur',
                    $q !== '' ? $q : "sort={$sort}",
                    $captured['queries'],
                    count($captured['result']) > 0 ? 'exploited' : 'info'
                );
            }

            return $captured['result'];
        }

        $allowedSorts = ['id', 'matricule', 'full_name', 'moyenne'];
        $safeSort = in_array($sort, $allowedSorts, true) ? $sort : 'matricule';

        $captured = $this->inspector->capture(function () use ($q, $safeSort): array {
            $query = Student::query()->select(['id', 'matricule', 'full_name', 'filiere', 'moyenne']);
            if ($q !== '') {
                $query->where(function ($sub) use ($q): void {
                    $sub->where('matricule', 'like', "%{$q}%")
                        ->orWhere('full_name', 'like', "%{$q}%");
                });
            }

            return $query->orderBy($safeSort, 'asc')->get()->all();
        });

        if (preg_match("/('|\"|union|select|--)/i", $q . ' ' . $sort) === 1) {
            $this->inspector->record(
                $request,
                '1. Injection SQL (Annuaire)',
                'secure',
                $request->user()?->name ?? 'Visiteur',
                $q !== '' ? $q : "sort={$sort}",
                $captured['queries'],
                'blocked'
            );
        }

        return $captured['result'];
    }
}
