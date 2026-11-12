<?php

namespace App\Http\Controllers\Portal;

use App\Http\Controllers\Controller;
use App\Models\Grade;
use App\Models\SecurityLog;
use App\Support\SecurityConfig;
use Illuminate\Http\RedirectResponse;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\Gate;
use Illuminate\View\View;

class GradeController extends Controller
{
    public function myGrade(Request $request): RedirectResponse
    {
        $user = $request->user();
        $student = $user->student;

        if (! $student) {
            return redirect()->route('portal.admin.grades');
        }

        $grade = $student->grades()->orderBy('id')->firstOrFail();

        return redirect()->route('portal.grades.show', ['grade' => $grade->id]);
    }

    public function show(Request $request, Grade $grade): View
    {
        $hardened = SecurityConfig::isHardened();

        if ($hardened) {
            Gate::authorize('view', $grade);
        } else {
            $grade->load('student.user');
            $user = $request->user();
            if ($grade->student?->user_id !== $user->id && ! $user->isAdmin()) {
                SecurityLog::create([
                    'pillar' => '5. IDOR / Policy',
                    'mode' => 'vulnerable',
                    'actor' => $user->name,
                    'payload' => "GET /bulletins/{$grade->id}",
                    'executed_sql' => "SELECT * FROM grades WHERE id = {$grade->id} LIMIT 1",
                    'outcome' => 'exploited',
                    'ip_address' => $request->ip(),
                ]);
            }
        }

        $grade->load('student.user');

        return view('portal.grade', [
            'grade' => $grade,
        ]);
    }

    public function adminIndex(Request $request): View
    {
        abort_unless($request->user()->isAdmin(), 403, 'Espace réservé à l\'administration UT LOKO.');

        return view('portal.admin-grades', [
            'grades' => Grade::with('student.user')->orderBy('id')->get(),
        ]);
    }

    public function updateScore(Request $request, Grade $grade): RedirectResponse
    {
        $hardened = SecurityConfig::isHardened();

        if ($hardened) {
            Gate::authorize('update', $grade);
        } else {
            abort_unless($request->user()->isAdmin(), 403);
        }

        $validated = $request->validate([
            'score' => ['required', 'numeric', 'min:0', 'max:20'],
        ]);

        $grade->update([
            'score' => $validated['score'],
        ]);

        if ($grade->student) {
            $grade->student->update([
                'moyenne' => $validated['score'],
            ]);
        }

        SecurityLog::create([
            'pillar' => '4. CSRF / Modification Note',
            'mode' => $hardened ? 'secure' : 'vulnerable',
            'actor' => $request->user()->name,
            'payload' => "POST /notes/{$grade->id}/modifier -> score={$validated['score']}",
            'executed_sql' => "UPDATE grades SET score = {$validated['score']} WHERE id = {$grade->id}",
            'outcome' => $hardened ? 'info' : 'exploited',
            'ip_address' => $request->ip(),
        ]);

        return redirect()->route('portal.admin.grades')->with('status', "Note de {$grade->student?->full_name} mise à jour à {$validated['score']}/20.");
    }
}
