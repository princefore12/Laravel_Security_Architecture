<?php

namespace App\Http\Controllers\Lab;

use App\Http\Controllers\Controller;
use App\Models\Student;
use App\Services\SqlInspectorService;
use Illuminate\Http\RedirectResponse;
use Illuminate\Http\Request;
use Illuminate\View\View;

class XssController extends Controller
{
    public function __construct(private readonly SqlInspectorService $inspector)
    {
    }

    public function indexVulnerable(): View
    {
        return $this->renderView('vulnerable');
    }

    public function indexSecure(): View
    {
        return $this->renderView('secure');
    }

    private function renderView(string $mode): View
    {
        $student = Student::query()->where('matricule', 'LOKO-2026-003')->firstOrFail();

        return view('lab.xss', [
            'mode' => $mode,
            'student' => $student,
            'queries' => session('lab_xss_queries', []),
            'hasDangerousTag' => preg_match('/<[^>]+(onerror|onload|script|svg|iframe)/i', $student->bio) === 1,
        ]);
    }

    public function store(Request $request): RedirectResponse
    {
        $mode = $request->input('mode', 'vulnerable') === 'secure' ? 'secure' : 'vulnerable';
        $bio = (string) $request->input('bio', '');
        $student = Student::query()->where('matricule', 'LOKO-2026-003')->firstOrFail();

        $captured = $this->inspector->capture(function () use ($student, $bio): void {
            $student->update(['bio' => $bio]);
        });

        $isXss = preg_match('/<[^>]+(onerror|onload|script|svg|iframe)/i', $bio) === 1;
        $outcome = $isXss ? ($mode === 'vulnerable' ? 'exploited' : 'blocked') : 'info';

        $this->inspector->record($request, '3. Faille XSS', $mode, 'Boin Naomi', $bio, $captured['queries'], $outcome);

        $route = $mode === 'secure' ? 'lab.xss.secure' : 'lab.xss.vulnerable';

        return redirect()->route($route)->with('lab_xss_queries', $captured['queries']);
    }

    public function resetBio(Request $request): RedirectResponse
    {
        $mode = $request->input('mode', 'vulnerable') === 'secure' ? 'secure' : 'vulnerable';
        $student = Student::query()->where('matricule', 'LOKO-2026-003')->firstOrFail();
        $student->update([
            'bio' => 'Responsable Pilier 3 (Faille XSS, Blade & En-têtes HTTP CSP).',
        ]);

        $route = $mode === 'secure' ? 'lab.xss.secure' : 'lab.xss.vulnerable';

        return redirect()->route($route);
    }
}
