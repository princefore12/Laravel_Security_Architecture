<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

return new class extends Migration
{
    public function up(): void
    {
        Schema::table('users', function (Blueprint $table) {
            $table->string('legacy_md5', 32)->nullable()->after('password');
        });

        Schema::create('campus_posts', function (Blueprint $table) {
            $table->id();
            $table->foreignId('user_id')->constrained()->cascadeOnDelete();
            $table->string('author_name', 120);
            $table->string('category', 60)->default('Annonce L3');
            $table->string('title', 160);
            $table->text('content');
            $table->timestamps();
        });
    }

    public function down(): void
    {
        Schema::dropIfExists('campus_posts');
        Schema::table('users', function (Blueprint $table) {
            $table->dropColumn('legacy_md5');
        });
    }
};
