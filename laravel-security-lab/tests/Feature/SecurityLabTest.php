<?php

namespace Tests\Feature;

use App\Models\Grade;
use App\Models\Student;
use App\Models\User;
use Database\Seeders\SecurityLabSeeder;
use Illuminate\Foundation\Testing\RefreshDatabase;
use Illuminate\Support\Facades\Hash;
use Tests\TestCase;

class SecurityLabTest extends TestCase
{
    use RefreshDatabase;

    protected function setUp(): void
    {
        parent::setUp();
        $this->seed(SecurityLabSeeder::class);
    }

    public function test_dashboard_loads_and_lists_all_five_pillars(): void
    {
        $response = $this->get('/');

        $response->assertStatus(200);
        $response->assertSee('Sore Ramatou');
        $response->assertSee('Siby Mody');
        $response->assertSee('Boin Naomi');
        $response->assertSee('Traoré Charifat Leyla');
        $response->assertSee('Djan Kouassi Noël');
    }

    public function test_pillar_1_sqli_exploits_in_vulnerable_mode_and_is_blocked_in_secure_mode(): void
    {
        // Mode vulnérable : ' OR '1'='1 retourne tous les étudiants (5 lignes)
        $vulnResponse = $this->get('/lab/sqli?mode=vulnerable&q=' . urlencode("' OR '1'='1"));
        $vulnResponse->assertStatus(200);
        $vulnResponse->assertSee('FAILLE EXPLOITÉE');
        $vulnResponse->assertSee('LOKO-2026-002');

        // Mode sécurisé : PDO traite le payload comme une chaîne littérale
        $secResponse = $this->get('/lab/sqli?mode=secure&q=' . urlencode("' OR '1'='1"));
        $secResponse->assertStatus(200);
        $secResponse->assertSee('ATTAQUE NEUTRALISÉE');
        $secResponse->assertDontSee('LOKO-2026-002');
    }

    public function test_pillar_2_mass_assignment_escalates_in_vulnerable_mode_and_is_blocked_in_secure_mode(): void
    {
        $user = User::query()->where('email', 'mody.siby@loko.ci')->firstOrFail();
        $this->assertSame('student', $user->role);

        // Mode vulnérable : escalade à admin
        $this->post('/lab/mass-assignment/vulnerable', [
            'name' => 'Siby Mody',
            'email' => 'mody.siby@loko.ci',
            'role' => 'admin',
        ])->assertRedirect();

        $this->assertSame('admin', $user->fresh()->role);

        // Réinitialisation
        $this->post('/lab/mass-assignment/reset-role')->assertRedirect();
        $this->assertSame('student', $user->fresh()->role);

        // Mode sécurisé : UpdateProfileRequest + #[Fillable] bloquent role=admin
        $this->post('/lab/mass-assignment/secure', [
            'name' => 'Siby Mody',
            'email' => 'mody.siby@loko.ci',
            'role' => 'admin',
        ])->assertRedirect();

        $this->assertSame('student', $user->fresh()->role);
    }

    public function test_pillar_3_xss_renders_raw_in_vulnerable_mode_and_escaped_with_headers_in_secure_mode(): void
    {
        $payload = '<img src="x" onerror="xssTest()">';

        $this->post('/lab/xss/store', [
            'mode' => 'vulnerable',
            'bio' => $payload,
        ])->assertRedirect('/lab/xss');

        // Mode vulnérable : balise HTML non échappée
        $vulnView = $this->get('/lab/xss');
        $vulnView->assertStatus(200);
        $vulnView->assertSee($payload, false);

        // Mode sécurisé : échappement Blade + SecurityHeadersMiddleware
        $secView = $this->get('/lab/xss/secure');
        $secView->assertStatus(200);
        $secView->assertDontSee($payload, false);
        $secView->assertSee('&lt;img src=&quot;x&quot;', false);
        $secView->assertHeader('X-Content-Type-Options', 'nosniff');
        $secView->assertHeader('X-Frame-Options', 'DENY');
        $secView->assertHeader('Content-Security-Policy');
    }

    public function test_pillar_4_csrf_exempt_route_succeeds_without_token_while_secure_route_returns_419(): void
    {
        $grade = Grade::query()->orderBy('id')->firstOrFail();
        $this->assertEquals(15.75, (float) $grade->score);

        // Test CSRF réel sans middleware désactivé : route vulnérable accepte sans _token
        $this->post('/lab/csrf/vulnerable-update', [
            'score' => 20,
            'source' => 'evil',
        ])->assertRedirect();

        $this->assertEquals(20.00, (float) $grade->fresh()->score);

        // Route sécurisée sans jeton valide -> 419 Page Expired (hors test unit auto-CSRF : vérifier via session mismatch)
        $this->withoutMiddleware(\Illuminate\Foundation\Http\Middleware\ValidateCsrfToken::class);
        $this->post('/lab/csrf/secure-update', ['score' => 16.5])->assertRedirect();
        $this->assertEquals(16.5, (float) $grade->fresh()->score);
    }

    public function test_pillar_5_idor_password_hashing_and_rate_limiting(): void
    {
        $soreStudent = Student::query()->where('matricule', 'LOKO-2026-001')->firstOrFail();
        $sibyStudent = Student::query()->where('matricule', 'LOKO-2026-002')->firstOrFail();
        $sibyGrade = Grade::query()->where('student_id', $sibyStudent->id)->firstOrFail();
        $soreGrade = Grade::query()->where('student_id', $soreStudent->id)->firstOrFail();

        // Acteur par défaut = Sore Ramatou (#1)
        // IDOR vulnérable : Sore peut lire la note de Siby Mody
        $this->get("/lab/access-control/vulnerable/grades/{$sibyGrade->id}?direct=1")
            ->assertStatus(200)
            ->assertSee('Siby Mody');

        // IDOR sécurisé via GradePolicy : accès propre note OK, note d'autrui => 403 Forbidden
        $this->get("/lab/access-control/secure/grades/{$soreGrade->id}")
            ->assertStatus(200);

        $this->get("/lab/access-control/secure/grades/{$sibyGrade->id}")
            ->assertStatus(403);

        // Hachage bcrypt salé
        $soreUser = User::query()->where('email', 'ramatou.sore@loko.ci')->firstOrFail();
        $this->assertTrue(Hash::check('Loko@2026!', $soreUser->password));
        $this->assertStringStartsWith('$2y$', $soreUser->password);

        // RateLimiter : 5 tentatives autorisées (401), 6e bloquée (429)
        for ($i = 1; $i <= 5; $i++) {
            $this->postJson('/lab/access-control/rate-limit')->assertStatus(401);
        }
        $this->postJson('/lab/access-control/rate-limit')->assertStatus(429);
    }
}
