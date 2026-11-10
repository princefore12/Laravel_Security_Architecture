<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;

class SecurityLog extends Model
{
    protected $fillable = [
        'pillar',
        'mode',
        'actor',
        'payload',
        'executed_sql',
        'outcome',
        'ip_address',
    ];
}
