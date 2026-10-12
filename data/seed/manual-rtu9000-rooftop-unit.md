# AeroCool RTU-9000 Rooftop Unit — Service Manual Excerpt

*Fictional sample document written for the FieldBrain demo. Not a real manufacturer's manual.*

## 1. Overview

The AeroCool RTU-9000 is a packaged rooftop air-conditioning unit for light commercial
buildings. It provides single-zone cooling with staged compressors and a belt-driven
supply fan. All service work must follow lockout/tagout procedure: open the unit
disconnect, verify zero energy with a meter, and tag the disconnect before removing
any panel.

## 2. Scheduled maintenance

- Replace return-air filters every 90 days, or monthly in dusty environments.
- Wash the condenser coil every spring before the cooling season, and again mid-season
  if the unit serves a kitchen or workshop space.
- Inspect the supply-fan belt for glazing and cracks every 6 months; replace if the belt
  deflects more than 12 mm under firm thumb pressure at mid-span.
- Clear the condensate drain trap at the start of every cooling season.

## 3. Fault code table (summary)

| Code | Meaning |
|------|---------|
| E12  | Return-air temperature sensor open circuit |
| E31  | Supply fan overload — check belt and motor amps |
| E47  | Compressor short-cycling protection |
| E52  | Condensate overflow switch tripped |

## 4. Fault E47 — Compressor short-cycling

Fault E47 is raised when the compressor starts more than 6 times in any 10-minute
window. The controller locks the compressor out for 30 minutes to protect it from
 overheating and logs E47 on the unit display. Short-cycling means the compressor
runs only briefly before a control or safety stops it, over and over.

Common causes, most frequent first:

1. **Dirty condenser coil.** A matted coil raises head pressure until the
   high-pressure switch opens, stops the compressor, then resets as pressure falls.
   This is the most common cause of E47 on this unit.
2. **Low refrigerant level.** A slow leak drops suction pressure until the
   low-pressure switch cuts the compressor out; pressure recovers at rest and the
   cycle repeats.
3. **Restricted airflow.** Clogged filters or a slipping fan belt starve the
   evaporator, dropping suction pressure the same way.
4. **Faulty high-pressure switch.** A switch that opens below its rated cut-out
   pressure will cycle the compressor even with a clean coil and correct charge.
5. **Thermostat cycle-rate setting.** A wall thermostat set to a very short cycle
   rate can call for cooling again within a minute of satisfying.

### Recommended checks for E47 — in this order

- Step 1: Lock out the unit, remove the condenser fan grille, and inspect the
  condenser coil. If the fins are matted with dirt or lint, wash the coil from the
  inside out with low-pressure water and a coil-safe cleaner.
- Step 2: Check the return-air filters and the supply-fan belt. Replace clogged
  filters; tighten or replace a slipping belt.
- Step 3: Restore power, run the unit in cooling, and watch one full cycle. If the
  compressor still stops within 2 minutes, attach gauges and record suction and
  discharge pressures at the moment of cut-out.
- Step 4: If discharge pressure spikes just before cut-out, suspect the coil or the
  high-pressure switch. Jumper-test the high-pressure switch only as a momentary
  diagnostic with gauges attached — never leave a safety switch bypassed.
- Step 5: If suction pressure falls steadily before cut-out, suspect low refrigerant
  level or an airflow restriction. Leak-check before adding any refrigerant.
- Step 6: Check the wall thermostat's cycle-rate setting; set it to the
  manufacturer's default of 3 cycles per hour for cooling.
- Step 7: If pressures are normal and the switches test good, escalate to a senior
  technician with the recorded pressures and cycle times attached to the work order.

## 5. Fault E31 — Supply fan overload

E31 trips when the fan motor draws more than its rated amps. Check for a seized
bearing, an over-tightened belt, or a blocked discharge duct before replacing the
motor. Record motor amps on the work order after any repair.

## 6. Fault E52 — Condensate overflow

E52 means the overflow float switch in the drain pan has lifted. Clear the drain
trap, flush the drain line, and confirm the pan slopes toward the drain outlet.
Do not bypass the overflow switch; water damage claims exceed the cost of the call.
