<?php

namespace App\Http\Controllers\Portal;

use App\Http\Controllers\Controller;
use App\Models\CampusPost;
use App\Models\SecurityLog;
use App\Support\SecurityConfig;
use Illuminate\Http\RedirectResponse;
use Illuminate\Http\Request;
use Illuminate\View\View;

class CampusController extends Controller
{
    public function index(): View
    {
        return view('portal.campus', [
            'posts' => CampusPost::query()->latest('id')->get(),
            'hardened' => SecurityConfig::isHardened(),
        ]);
    }

    public function store(Request $request): RedirectResponse
    {
        $validated = $request->validate([
            'title' => ['required', 'string', 'max:160'],
            'category' => ['required', 'string', 'max:60'],
            'content' => ['required', 'string', 'max:2000'],
        ]);

        $user = $request->user();
        $post = CampusPost::create([
            'user_id' => $user->id,
            'author_name' => $user->name,
            'category' => $validated['category'],
            'title' => $validated['title'],
            'content' => $validated['content'],
        ]);

        if (preg_match('/<[^>]+>|onerror=|onload=|<script/i', $validated['content']) === 1) {
            SecurityLog::create([
                'pillar' => '3. XSS Stockée',
                'mode' => SecurityConfig::isHardened() ? 'secure' : 'vulnerable',
                'actor' => $user->name,
                'payload' => $validated['content'],
                'executed_sql' => "INSERT INTO campus_posts (id={$post->id})",
                'outcome' => SecurityConfig::isHardened() ? 'blocked' : 'exploited',
                'ip_address' => $request->ip(),
            ]);
        }

        return redirect()->route('portal.campus')->with('status', 'Publication ajoutée sur le mur du campus.');
    }
}
