<?php

namespace Database\Seeders;

use App\Models\Grade;
use App\Models\SecurityLog;
use App\Models\Student;
use App\Models\User;
use Illuminate\Database\Seeder;
use Illuminate\Support\Facades\Hash;

class SecurityLabSeeder extends Seeder
{
    public function run(): void
    {
        $members = [
            [
                'name' => 'Sore Ramatou',
                'email' => 'ramatou.sore@loko.ci',
                'role' => 'student',
                'matricule' => 'LOKO-2026-001',
                'moyenne' => 15.75,
                'bio' => 'Responsable Introduction & Pilier 1 (Injection SQL). Passionnée par MariaDB et l\'ORM Eloquent.',
                'course_code' => 'INF-301',
                'course_name' => 'Base de Données (XAMPP) & Laravel',
                'score' => 15.75,
                'jury_remark' => 'Très bonne maîtrise des requêtes préparées PDO.',
            ],
            [
                'name' => 'Siby Mody',
                'email' => 'mody.siby@loko.ci',
                'role' => 'student',
                'matricule' => 'LOKO-2026-002',
                'moyenne' => 16.25,
                'bio' => 'Responsable Pilier 2 (Mass Assignment & FormRequest). Focus sur l\'intégrité des colonnes SQL.',
                'course_code' => 'INF-302',
                'course_name' => 'Sécurité des Systèmes Web',
                'score' => 16.25,
                'jury_remark' => 'Confidentiel : dossier réservé exclusivement à Siby Mody.',
            ],
            [
                'name' => 'Boin Naomi',
                'email' => 'naomi.boin@loko.ci',
                'role' => 'student',
                'matricule' => 'LOKO-2026-003',
                'moyenne' => 15.50,
                'bio' => 'Responsable Pilier 3 (Faille XSS, Blade & En-têtes HTTP CSP).',
                'course_code' => 'INF-303',
                'course_name' => 'Interfaces Blade & Sécurité Navigateur',
                'score' => 15.50,
                'jury_remark' => 'Excellente démonstration de l\'échappement {{ }}.',
            ],
            [
                'name' => 'Traoré Charifat Leyla',
                'email' => 'leyla.traore@loko.ci',
                'role' => 'student',
                'matricule' => 'LOKO-2026-004',
                'moyenne' => 16.00,
                'bio' => 'Responsable Pilier 4 (Faille CSRF, Sessions & Jeton cryptographique @csrf).',
                'course_code' => 'INF-304',
                'course_name' => 'Architecture Sessions & Cookies',
                'score' => 16.00,
                'jury_remark' => 'Analyse rigoureuse des jetons anti-CSRF.',
            ],
            [
                'name' => 'Djan Kouassi Noël',
                'email' => 'noel.djan@loko.ci',
                'role' => 'student',
                'matricule' => 'LOKO-2026-005',
                'moyenne' => 15.90,
                'bio' => 'Responsable Pilier 5 (Bcrypt, IDOR Policies, RateLimiter & Durcissement .env).',
                'course_code' => 'INF-305',
                'course_name' => 'Cryptographie & Administration Serveur',
                'score' => 15.90,
                'jury_remark' => 'Très bon contrôle d\'accès basé sur les Policies.',
            ],
        ];

        foreach ($members as $data) {
            $user = User::query()->updateOrCreate(
                ['email' => $data['email']],
                [
                    'name' => $data['name'],
                    'password' => Hash::make('Loko@2026!'),
                ]
            );
            $user->forceFill(['role' => $data['role']])->save();

            $student = Student::query()->updateOrCreate(
                ['matricule' => $data['matricule']],
                [
                    'user_id' => $user->id,
                    'full_name' => $data['name'],
                    'filiere' => 'Informatique L3',
                    'moyenne' => $data['moyenne'],
                    'bio' => $data['bio'],
                ]
            );

            Grade::query()->updateOrCreate(
                ['student_id' => $student->id, 'course_code' => $data['course_code']],
                [
                    'course_name' => $data['course_name'],
                    'score' => $data['score'],
                    'jury_remark' => $data['jury_remark'],
                ]
            );
        }

        $admin = User::query()->updateOrCreate(
            ['email' => 'admin@loko.ci'],
            [
                'name' => 'Prof. M. Camara',
                'password' => Hash::make('Camara@Loko2026'),
            ]
        );
        $admin->forceFill(['role' => 'admin'])->save();

        if (SecurityLog::query()->count() === 0) {
            SecurityLog::create([
                'pillar' => 'Système',
                'mode' => 'secure',
                'actor' => 'LOKO-Vault',
                'payload' => 'Initialisation des données Groupe 5',
                'executed_sql' => 'SEED users, students, grades -> loko_security_lab',
                'outcome' => 'info',
                'ip_address' => '127.0.0.1',
            ]);
        }
    }
}
