<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

return new class extends Migration
{
    public function up(): void
    {
        Schema::table('users', function (Blueprint $table) {
            $table->string('role', 30)->default('student')->after('password');
        });

        Schema::create('students', function (Blueprint $table) {
            $table->id();
            $table->foreignId('user_id')->constrained()->cascadeOnDelete();
            $table->string('matricule', 32)->unique();
            $table->string('full_name', 120);
            $table->string('filiere', 120)->default('Informatique L3');
            $table->decimal('moyenne', 4, 2)->default(14.00);
            $table->text('bio');
            $table->timestamps();
        });

        Schema::create('grades', function (Blueprint $table) {
            $table->id();
            $table->foreignId('student_id')->constrained()->cascadeOnDelete();
            $table->string('course_code', 24);
            $table->string('course_name', 140);
            $table->decimal('score', 4, 2);
            $table->string('jury_remark', 160);
            $table->timestamps();
        });

        Schema::create('security_logs', function (Blueprint $table) {
            $table->id();
            $table->string('pillar', 60);
            $table->string('mode', 20); // vulnerable | secure
            $table->string('actor', 100);
            $table->text('payload')->nullable();
            $table->text('executed_sql')->nullable();
            $table->string('outcome', 40); // exploited | blocked | info
            $table->string('ip_address', 45)->nullable();
            $table->timestamps();
        });
    }

    public function down(): void
    {
        Schema::dropIfExists('security_logs');
        Schema::dropIfExists('grades');
        Schema::dropIfExists('students');
        Schema::table('users', function (Blueprint $table) {
            $table->dropColumn('role');
        });
    }
};
