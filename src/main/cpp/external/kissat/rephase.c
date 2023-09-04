#include "backtrack.h"
#include "decide.h"
#include "internal.h"
#include "logging.h"
#include "print.h"
#include "rephase.h"
#include "report.h"
#include "terminate.h"
#include "walk.h"

#include <inttypes.h>
#include <string.h>

static void
kissat_reset_best_assigned (kissat * solver)
{
  if (!solver->best_assigned)
    return;
  kissat_extremely_verbose (solver,
			    "resetting best assigned trail height %u to 0",
			    solver->best_assigned);
  solver->best_assigned = 0;
}

static void
kissat_reset_target_assigned (kissat * solver)
{
  if (!solver->target_assigned)
    return;
  kissat_extremely_verbose (solver,
			    "resetting target assigned trail height %u to 0",
			    solver->target_assigned);
  solver->target_assigned = 0;
}

bool
kissat_rephasing (kissat * solver)
{
  if (!GET_OPTION (rephase))
    return false;
  if (!solver->stable)
    return false;
  return CONFLICTS > solver->limits_.rephase.conflicts;
}

static char
rephase_best (kissat * solver)
{
  const value *const best = solver->phases_.best;
  const value *const end_of_best = best + VARS;
  value const *b;

  value *const saved = solver->phases_.saved;
  value *s;

  value tmp;

  for (s = saved, b = best; b != end_of_best; s++, b++)
    if ((tmp = *b))
      *s = tmp;

  INC (rephased_best);

  return 'B';
}

static char
rephase_original (kissat * solver)
{
  const value initial_phase = INITIAL_PHASE;
  for (all_phases (saved, p))
    *p = initial_phase;
  INC (rephased_original);
  return 'O';
}

static char
rephase_inverted (kissat * solver)
{
  const value inverted_initial_phase = -INITIAL_PHASE;
  for (all_phases (saved, p))
    *p = inverted_initial_phase;
  INC (rephased_inverted);
  return 'I';
}

static char
rephase_walking (kissat * solver)
{
  assert (kissat_walking (solver));
  STOP (rephase);
  kissat_walk (solver);
  START (rephase);
  INC (rephased_walking);
  return 'W';
}

// *IDENT-OFF*

static char (*rephase_schedule[]) (kissat *) = {
  rephase_best, rephase_walking, rephase_inverted,
  rephase_best, rephase_walking, rephase_original,
};

#define size_rephase_schedule \
  (sizeof rephase_schedule / sizeof *rephase_schedule)

// *IDENT-ON*

#ifndef QUIET

static const char *
rephase_type_as_string (char type)
{
  if (type == 'B')
    return "best";
  if (type == 'I')
    return "inverted";
  if (type == 'O')
    return "original";
  assert (type == 'W');
  return "walking";
}

#endif

static char
reset_phases (kissat * solver)
{
  const uint64_t count = GET (rephased);
  assert (count > 0);
  const uint64_t select = (count - 1) % (uint64_t) size_rephase_schedule;
  const char type = rephase_schedule[select] (solver);
  kissat_phase (solver, "rephase", GET (rephased),
		"%s phases in %s search mode",
		rephase_type_as_string (type),
		solver->stable ? "stable" : "focused");
  LOG ("copying saved phases as target phases");
  memcpy (solver->phases_.target, solver->phases_.saved, VARS);
  UPDATE_CONFLICT_LIMIT (rephase, rephased, NLOG3N, false);
  kissat_reset_target_assigned (solver);
  if (type == 'B')
    kissat_reset_best_assigned (solver);
  return type;
}

void
kissat_rephase (kissat * solver)
{
  kissat_backtrack_propagate_and_flush_trail (solver);
  assert (!solver->inconsistent);
  START (rephase);
  INC (rephased);
#ifndef QUIET
  const char type =
#endif
    reset_phases (solver);
  REPORT (0, type);
  STOP (rephase);
}
