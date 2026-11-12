<?php

namespace Database\Seeders;

use App\Models\CampusPost;
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
                'bio' => 'Étudiante en Licence 3 Informatique & Télécommunication — Spécialisation Bases de Données.',
                'course_code' => 'INF-301',
                'course_name' => 'Base de Données (XAMPP) & Laravel',
                'score' => 15.75,
                'jury_remark' => 'Très bonne maîtrise des requêtes SQL et de la modélisation relationnelle.',
            ],
            [
                'name' => 'Siby Mody',
                'email' => 'mody.siby@loko.ci',
                'role' => 'student',
                'matricule' => 'LOKO-2026-002',
                'moyenne' => 16.25,
                'bio' => 'Étudiant en Licence 3 Informatique — Développement Backend Laravel & Architecture Web.',
                'course_code' => 'INF-302',
                'course_name' => 'Sécurité des Systèmes Web',
                'score' => 16.25,
                'jury_remark' => 'Confidentiel : relevé académique personnel réservé exclusivement à Siby Mody.',
            ],
            [
                'name' => 'Boin Naomi',
                'email' => 'naomi.boin@loko.ci',
                'role' => 'student',
                'matricule' => 'LOKO-2026-003',
                'moyenne' => 15.50,
                'bio' => 'Étudiante en Licence 3 Informatique — Intégration Blade, UX et Sécurité Navigateur.',
                'course_code' => 'INF-303',
                'course_name' => 'Interfaces Blade & Sécurité Navigateur',
                'score' => 15.50,
                'jury_remark' => 'Excellente présentation technique des interfaces web.',
            ],
            [
                'name' => 'Traoré Charifat Leyla',
                'email' => 'leyla.traore@loko.ci',
                'role' => 'student',
                'matricule' => 'LOKO-2026-004',
                'moyenne' => 16.00,
                'bio' => 'Étudiante en Licence 3 Informatique — Protocoles HTTP, Sessions et Authentification.',
                'course_code' => 'INF-304',
                'course_name' => 'Architecture Sessions & Cookies',
                'score' => 16.00,
                'jury_remark' => 'Analyse rigoureuse du protocole HTTP et des sessions.',
            ],
            [
                'name' => 'Djan Kouassi Noël',
                'email' => 'noel.djan@loko.ci',
                'role' => 'student',
                'matricule' => 'LOKO-2026-005',
                'moyenne' => 15.90,
                'bio' => 'Étudiant en Licence 3 Informatique — Administration Serveur, Cryptographie et Déploiement.',
                'course_code' => 'INF-305',
                'course_name' => 'Cryptographie & Administration Serveur',
                'score' => 15.90,
                'jury_remark' => 'Très bon contrôle des accès et de la configuration serveur.',
            ],
        ];

        $createdUsers = [];
        foreach ($members as $data) {
            $user = User::query()->updateOrCreate(
                ['email' => $data['email']],
                [
                    'name' => $data['name'],
                    'password' => Hash::make('Loko@2026!'),
                ]
            );
            $user->forceFill([
                'role' => $data['role'],
                'legacy_md5' => md5('Loko@2026!'),
            ])->save();

            $createdUsers[$data['email']] = $user;

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
        $admin->forceFill([
            'role' => 'admin',
            'legacy_md5' => md5('Camara@Loko2026'),
        ])->save();

        if (CampusPost::query()->count() === 0) {
            CampusPost::create([
                'user_id' => $admin->id,
                'author_name' => $admin->name,
                'category' => 'Administration',
                'title' => 'Bienvenue sur le Portail Académique UT LOKO (2025 – 2026)',
                'content' => 'Les étudiants de Licence 3 Informatique peuvent consulter l\'annuaire, leurs relevés de notes et partager les actualités du département ITER sur cet espace.',
            ]);
            CampusPost::create([
                'user_id' => $createdUsers['ramatou.sore@loko.ci']->id,
                'author_name' => 'Sore Ramatou',
                'category' => 'Projet L3',
                'title' => 'Migration MariaDB sous XAMPP terminée',
                'content' => 'La base de données relationnelle du département est désormais opérationnelle sous MariaDB 10.11 avec les fiches LOKO-2026-001 à 005.',
            ]);
            CampusPost::create([
                'user_id' => $createdUsers['mody.siby@loko.ci']->id,
                'author_name' => 'Siby Mody',
                'category' => 'Développement',
                'title' => 'Mise en ligne de l\'espace Profil Étudiant',
                'content' => 'Chaque étudiant peut désormais mettre à jour son nom et son adresse électronique depuis la rubrique Mon Profil.',
            ]);
        }

        if (SecurityLog::query()->count() === 0) {
            SecurityLog::create([
                'pillar' => 'Portail',
                'mode' => 'info',
                'actor' => 'Système UT LOKO',
                'payload' => 'Initialisation Portail Académique Groupe 5',
                'executed_sql' => 'SEED users, students, grades, campus_posts -> loko_security_lab',
                'outcome' => 'info',
                'ip_address' => '127.0.0.1',
            ]);
        }
    }
}
