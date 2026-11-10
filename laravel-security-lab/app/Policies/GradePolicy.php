<?php

namespace App\Policies;

use App\Models\Grade;
use App\Models\User;

class GradePolicy
{
    /**
     * Un utilisateur ne peut consulter que ses propres notes, sauf s'il est administrateur.
     */
    public function view(User $user, Grade $grade): bool
    {
        return $user->isAdmin() || $grade->student?->user_id === $user->id;
    }

    /**
     * Seul un administrateur peut modifier une note officielle.
     */
    public function update(User $user, Grade $grade): bool
    {
        return $user->isAdmin();
    }
}
