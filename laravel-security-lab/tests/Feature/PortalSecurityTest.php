<?php

namespace Tests\Feature;

use App\Http\Middleware\DynamicCsrfMiddleware;
use App\Models\Grade;
use App\Models\User;
use Illuminate\Database\QueryException;
use Illuminate\Foundation\Testing\RefreshDatabase;
use Illuminate\Http\Request;
use Illuminate\Http\Response;
use Illuminate\Session\TokenMismatchException;
use Illuminate\Support\Facades\Hash;
use Tests\TestCase;

class PortalSecurityTest extends TestCase
{
    use RefreshDatabase;

    protected function setUp(): void
    {
        parent::setUp();
        $this->seed();
    }

    public function test_public_portal_pages_render_without_spoilers_or_lab_controls(): void
    {
        config(['security.hardened' => false]);

        $response = $this->get('/');
        $response->assertOk();
        $response->assertSee('Portail Académique UT LOKO');
        $response->assertSee('Annuaire');
        $response->assertSee('Mur du Campus');
        $response->assertDontSee('FAILLE EXPLOITÉE');
        $response->assertDontSee('Mode Vulnérable');
    }

    public function test_sqli_login_bypass_and_union_extraction_work_when_unhardened_and_fail_when_hardened(): void
    {
        // 1. Mode vulnérable : SQLi login bypass sur admin@loko.ci sans mot de passe
        config(['security.hardened' => false]);
        $bypassResponse = $this->post('/connexion', [
            'email' => "admin@loko.ci' -- ",
            'password' => 'mauvais-mot-de-passe',
        ]);
        $bypassResponse->assertRedirect('/');
        $this->assertAuthenticated();
        $this->assertTrue(auth()->user()->isAdmin());

        auth()->logout();

        // 2. Mode vulnérable : SQLi UNION SELECT dans l'annuaire + tri API
        $unionPayload = "' AND 1=0 UNION SELECT id, email, password, legacy_md5, role FROM users -- ";
        $dirResponse = $this->get('/annuaire?q=' . urlencode($unionPayload));
        $dirResponse->assertOk();
        $dirResponse->assertSee('admin@loko.ci');
        $dirResponse->assertSee(md5('Loko@2026!'));

        // Requête API JSON vulnérable avec tri injecté / erreur SQL sous APP_DEBUG
        $apiOk = $this->get('/api/annuaire?sort=moyenne');
        $apiOk->assertOk()->assertJsonPath('count', 5);

        $this->withoutExceptionHandling();
        $thrown = false;
        try {
            $this->get('/annuaire?q=' . urlencode("'"));
        } catch (QueryException) {
            $thrown = true;
        }
        $this->withExceptionHandling();
        $this->assertTrue($thrown, 'Une quote simple en mode non durci doit déclencher une vraie erreur SQL.');

        // 3. Mode durci : les mêmes attaques échouent
        config(['security.hardened' => true]);
        $blockedLogin = $this->post('/connexion', [
            'email' => "admin@loko.ci' -- ",
            'password' => 'mauvais-mot-de-passe',
        ]);
        $blockedLogin->assertStatus(401);
        $this->assertGuest();

        $safeDir = $this->get('/annuaire?q=' . urlencode($unionPayload));
        $safeDir->assertOk();
        $safeDir->assertDontSee('admin@loko.ci');
        $safeDir->assertDontSee(md5('Loko@2026!'));
        $safeDir->assertSee('Aucun étudiant ne correspond à votre recherche');

        // Tri invalide ignoré via liste blanche
        $safeApi = $this->get('/api/annuaire?sort=invalid_column');
        $safeApi->assertOk()->assertJsonPath('count', 5);
    }

    public function test_mass_assignment_escalates_role_when_unhardened_and_ignores_role_when_hardened(): void
    {
        $siby = User::query()->where('email', 'mody.siby@loko.ci')->firstOrFail();
        $this->assertSame('student', $siby->role);

        // Mode vulnérable : champ injecté dans F12 élève Siby Mody en admin
        config(['security.hardened' => false]);
        $this->actingAs($siby)
            ->post('/profil', [
                'name' => 'Siby Mody',
                'email' => 'mody.siby@loko.ci',
                'role' => 'admin',
            ])
            ->assertRedirect('/profil');

        $siby->refresh();
        $this->assertSame('admin', $siby->role);
        $this->actingAs($siby)->get('/')->assertSee('Administration');

        // Réinitialisation du rôle pour tester le mode durci
        $siby->forceFill(['role' => 'student'])->save();
        config(['security.hardened' => true]);

        $this->actingAs($siby)
            ->post('/profil', [
                'name' => 'Siby Mody',
                'email' => 'mody.siby@loko.ci',
                'role' => 'admin',
            ])
            ->assertRedirect('/profil');

        $siby->refresh();
        $this->assertSame('student', $siby->role);
        $this->actingAs($siby)->get('/admin/notes')->assertForbidden();
    }

    public function test_xss_cookies_httponly_and_csp_toggle_with_security_hardened(): void
    {
        $naomi = User::query()->where('email', 'naomi.boin@loko.ci')->firstOrFail();
        $payload = '<img src="x" onerror="alert(document.cookie)">';

        // Publication sur le Mur du Campus
        config(['security.hardened' => false]);
        $this->actingAs($naomi)->post('/campus', [
            'title' => 'Annonce XSS test',
            'category' => 'Projet L3',
            'content' => $payload,
        ])->assertRedirect('/campus');

        $vulnPage = $this->get('/campus');
        $vulnPage->assertOk();
        $vulnPage->assertSee($payload, false);
        $vulnPage->assertHeaderMissing('Content-Security-Policy');

        $vulnCookies = collect($vulnPage->headers->getCookies())->keyBy->getName();
        $sessionCookieName = config('session.cookie');
        $this->assertTrue($vulnCookies->has($sessionCookieName));
        $this->assertFalse($vulnCookies[$sessionCookieName]->isHttpOnly());

        // Mode durci : Blade échappe HTML + HttpOnly + CSP strict sans unsafe-inline pour scripts
        config(['security.hardened' => true]);
        $secPage = $this->get('/campus');
        $secPage->assertOk();
        $secPage->assertDontSee($payload, false);
        $secPage->assertSee($payload, true);
        $secPage->assertHeader('X-Frame-Options', 'DENY');
        $this->assertStringContainsString("script-src 'self'", (string) $secPage->headers->get('Content-Security-Policy'));
        $this->assertStringNotContainsString("script-src 'self' 'unsafe-inline'", (string) $secPage->headers->get('Content-Security-Policy'));

        $secCookies = collect($secPage->headers->getCookies())->keyBy->getName();
        $this->assertTrue($secCookies[$sessionCookieName]->isHttpOnly());
    }

    public function test_csrf_dynamic_middleware_allows_forged_update_only_when_unhardened(): void
    {
        $request = Request::create('/notes/4/modifier', 'POST', ['score' => '20.00']);
        $request->setLaravelSession($this->app['session']->driver());
        $request->session()->start();

        $middleware = new class($this->app, $this->app['encrypter']) extends DynamicCsrfMiddleware
        {
            protected function runningUnitTests(): bool
            {
                return false;
            }
        };

        config(['security.hardened' => false]);
        $response = $middleware->handle($request, fn (): Response => new Response('ok', 200));
        $this->assertSame(200, $response->getStatusCode());

        config(['security.hardened' => true]);
        $this->expectException(TokenMismatchException::class);
        $middleware->handle($request, fn (): Response => new Response('ok', 200));
    }

    public function test_idor_policy_rate_limiter_and_password_hashes(): void
    {
        $sore = User::query()->where('email', 'ramatou.sore@loko.ci')->firstOrFail();
        $sibyGrade = Grade::query()->where('course_code', 'INF-302')->firstOrFail();

        // MD5 historique identique pour deux comptes ayant le même mot de passe vs bcrypt unique
        $siby = User::query()->where('email', 'mody.siby@loko.ci')->firstOrFail();
        $this->assertSame($sore->legacy_md5, $siby->legacy_md5);
        $this->assertNotSame($sore->password, $siby->password);
        $this->assertTrue(Hash::check('Loko@2026!', $siby->password));

        // IDOR ouvert en mode non durci
        config(['security.hardened' => false]);
        $this->actingAs($sore)
            ->get("/bulletins/{$sibyGrade->id}")
            ->assertOk()
            ->assertSee('Siby Mody')
            ->assertSee('Confidentiel : relevé académique personnel réservé exclusivement à Siby Mody.');

        // IDOR bloqué en mode durci (403)
        config(['security.hardened' => true]);
        $this->actingAs($sore)
            ->get("/bulletins/{$sibyGrade->id}")
            ->assertForbidden();

        // RateLimiter HTTP 429 à la 6e tentative
        for ($i = 0; $i < 5; $i++) {
            $this->post('/connexion', [
                'email' => 'ramatou.sore@loko.ci',
                'password' => 'mauvais',
            ])->assertStatus(401);
        }

        $this->post('/connexion', [
            'email' => 'ramatou.sore@loko.ci',
            'password' => 'mauvais',
        ])->assertStatus(429);
    }
}
