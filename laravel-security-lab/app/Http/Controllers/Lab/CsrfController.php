<?php

namespace App\Http\Controllers\Lab;

use App\Http\Controllers\Controller;
use App\Models\Grade;
use App\Services\SqlInspectorService;
use Illuminate\Http\RedirectResponse;
use Illuminate\Http\Request;
use Illuminate\View\View;

class CsrfController extends Controller
{
    public function __construct(private readonly SqlInspectorService $inspector)
    {
    }

    public function index(Request $request): View
    {
        $mode = $request->query('mode', 'vulnerable') === 'secure' ? 'secure' : 'vulnerable';
        $grade = Grade::with('student')->orderBy('id')->firstOrFail();

        return view('lab.csrf', [
            'mode' => $mode,
            'grade' => $grade,
            'queries' => session('lab_csrf_queries', []),
            'csrfNotice' => session('lab_csrf_notice'),
            'csrfType' => session('lab_csrf_type'),
        ]);
    }

    public function evilSite(Request $request): View
    {
        $mode = $request->query('mode', 'vulnerable') === 'secure' ? 'secure' : 'vulnerable';
        $targetAction = $mode === 'secure'
            ? route('lab.csrf.secure-update')
            : route('lab.csrf.vulnerable-update');

        return view('lab.csrf-evil', [
            'mode' => $mode,
            'targetAction' => $targetAction,
        ]);
    }

    public function updateVulnerable(Request $request): RedirectResponse
    {
        $grade = Grade::query()->orderBy('id')->firstOrFail();
        $newScore = (float) $request->input('score', 20.00);
        $source = (string) $request->input('source', 'site-externe');

        $captured = $this->inspector->capture(function () use ($grade, $newScore, $source): void {
            $grade->update([
                'score' => $newScore,
                'jury_remark' => $source === 'evil'
                    ? '⚠️ NOTE MODIFIÉE FRAUDULEUSEMENT PAR ATTAQUE CSRF !'
                    : 'Note mise à jour sans jeton CSRF.',
            ]);
        });

        $this->inspector->record(
            $request,
            '4. Faille CSRF',
            'vulnerable',
            'Traoré Charifat Leyla',
            "POST sans _token (score={$newScore}, source={$source})",
            $captured['queries'],
            'exploited'
        );

        return redirect()->route('lab.csrf', ['mode' => 'vulnerable'])
            ->with('lab_csrf_queries', $captured['queries'])
            ->with('lab_csrf_type', 'exploited')
            ->with('lab_csrf_notice', "ATTAQUE CSRF RÉUSSIE : La requête forgée sans jeton _token a modifié la note en base MariaDB à {$newScore}/20 !");
    }

    public function updateSecure(Request $request): RedirectResponse
    {
        $grade = Grade::query()->orderBy('id')->firstOrFail();
        $newScore = max(0, min(20, (float) $request->input('score', 15.75)));

        $captured = $this->inspector->capture(function () use ($grade, $newScore): void {
            $grade->update([
                'score' => $newScore,
                'jury_remark' => 'Note validée légitimement avec jeton @csrf.',
            ]);
        });

        $this->inspector->record(
            $request,
            '4. Faille CSRF',
            'secure',
            'Traoré Charifat Leyla',
            "POST protégé par @csrf (score={$newScore})",
            $captured['queries'],
            'info'
        );

        return redirect()->route('lab.csrf', ['mode' => 'secure'])
            ->with('lab_csrf_queries', $captured['queries'])
            ->with('lab_csrf_type', 'info')
            ->with('lab_csrf_notice', "Mise à jour légitime acceptée avec succès (jeton _token vérifié par hash_equals).");
    }

    public function resetGrade(Request $request): RedirectResponse
    {
        $grade = Grade::query()->orderBy('id')->firstOrFail();
        $grade->update([
            'score' => 15.75,
            'jury_remark' => 'Très bonne maîtrise des requêtes préparées PDO.',
        ]);

        return redirect()->route('lab.csrf', ['mode' => $request->input('mode', 'vulnerable')])
            ->with('lab_csrf_type', 'info')
            ->with('lab_csrf_notice', 'Note officielle restaurée à 15.75/20.');
    }
}
