<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Relations\BelongsTo;

class Grade extends Model
{
    protected $fillable = [
        'student_id',
        'course_code',
        'course_name',
        'score',
        'jury_remark',
    ];

    public function student(): BelongsTo
    {
        return $this->belongsTo(Student::class);
    }
}
