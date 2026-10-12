# Meridian AH-40 Air Handler and VAV Terminals — Service Notes Excerpt

*Fictional sample document written for the FieldBrain demo. Not a real manufacturer's manual.*

## 1. Overview

The Meridian AH-40 is an indoor air handler serving variable-air-volume (VAV)
terminal units on two floors. It uses a direct-drive plenum fan and a chilled-water
coil fed from the building loop. This excerpt covers the parts of the unit a field
technician is expected to service without factory support.

## 2. VAV terminal dampers

Each VAV terminal has a damper actuator driven by the room controller. If a zone
reports too much or too little air:

- Confirm the room controller is calling for the damper position shown on the
  handheld readout.
- Stroke the damper from the controller: it should travel fully in under 90 seconds
  without hunting.
- A damper that hunts (oscillates around setpoint) usually has a loose actuator
  coupling on the damper shaft. Tighten the coupling set screw and re-stroke.

## 3. Chilled-water coil

- Bleed air from the coil vent at the start of the cooling season; an air-locked
  coil shows as one hot end and one cold end.
- The two-way control valve should modulate smoothly. A valve that jumps between
  open and shut points to a failed actuator motor, not a controls problem.
- Keep strainer screens clean; a clogged strainer starves the coil and mimics a
  low-flow complaint from every zone on the riser.

## 4. Fan and motor

The AH-40 plenum fan is direct drive — there is no belt to adjust. Fan faults are
almost always electrical: check the motor terminal box for heat discoloration and
confirm the drive's fault history before condemning the motor. The drive stores its
last 10 faults with timestamps; record them on the work order.

## 5. Fault codes (summary)

| Code | Meaning |
|------|---------|
| F03  | Damper actuator feedback mismatch |
| F14  | Chilled-water valve actuator failure |
| F22  | Fan drive over-temperature |

Fault F03 is raised when the damper's reported position disagrees with the commanded
position by more than 10 percent for over 5 minutes. Nine times out of ten the cause
is the loose actuator coupling described in section 2.
