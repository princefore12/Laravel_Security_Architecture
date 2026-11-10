<?php

namespace App\Http\Controllers\Lab;

use App\Http\Controllers\Controller;
use App\Models\Grade;
use App\Models\SecurityLog;
use App\Models\Student;
use App\Models\User;
use Database\Seeders\SecurityLabSeeder;
use Illuminate\Http\RedirectResponse;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\DB;
use Illuminate\Support\Facades\RateLimiter;
use Illuminate\View\View;

class LabDashboardController extends Controller
{
    public function index(): View
    {
        return view('lab.dashboard', [
            'stats' => [
                'users' => User::query()->count(),
                'students' => Student::query()->count(),
                'grades' => Grade::query()->count(),
                'logs' => SecurityLog::query()->count(),
                'exploited' => SecurityLog::query()->where('outcome', 'exploited')->count(),
                'blocked' => SecurityLog::query()->where('outcome', 'blocked')->count(),
            ],
            'logs' => SecurityLog::query()->latest('id')->limit(12)->get(),
            'dbDriver' => DB::connection()->getDriverName(),
            'dbName' => DB::connection()->getDatabaseName(),
        ]);
    }

    public function reset(Request $request): RedirectResponse
    {
        SecurityLog::query()->truncate();
        (new SecurityLabSeeder())->run();

        RateLimiter::clear('lab-login:' . $request->ip());
        $request->session()->put('lab_acting_user_email', 'ramatou.sore@loko.ci');

        return redirect()->route('lab.dashboard')
            ->with('status', 'Base de données loko_security_lab réinitialisée dans son état initial propre !');
    }
}
