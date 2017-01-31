# -*- coding: utf-8 -*-
# Copyright 2017 Tomasz "Niektóry" Turowski

class Wound(object):
	def __init__(self, name, location, duration=1, penalties=0, effects=[]):
		self.name = name
		self.location = location
		self.duration = duration
		self.pdm_penalty = penalties
		self.skill_penalty = penalties
		self.effects = effects
	
	def onEndTurn(self):
		self.duration -= 1
		return self.duration


"""		
Minor wounds
 
Head 
­2 to all actions
+2 to PDM
1 round
penalties reduced by 1 with a successful Pain Threshold check

Torso 
­1 to all actions
+1 to PDM
1 round

Arms 
­1 to all actions with the hand
1 round

Legs 
knocked down to sitting/crouched/prone
 
Severe Wounds
 
Head 
on a failed pain threshold check, the character loses consciousness

Loss of Hearing / Ringing Ears 
a couple of minutes

Temporary Loss of Sight 
blinded for 2 rounds, then:
­1 to all actions
+1 to PDM
a couple of minutes

Stumble 
move d3 metres to random direction (no AoO)
­2 to all actions
+2 to PDM
1 round

Dizziness 
+3 to PDM
a couple of minutes

Striking Pain 
­2 to all actions
+2 to PDM
a couple of minutes

Bleeding Wound 
2 points of damage on her own initiative each round
until bound
Binding the wound is a one round action that gets +2 to First Aid check. 
 
Torso 
on a failed pain threshold check, the character loses consciousness

Hurt in the privates 
stunned until she succeeds in a pain threshold check, then:
­2 to all actions
+2 to PDM
1 round
+2 to the pain threshold check to see if she loses consciousness because of this wound

Fractured rib 
­1 to all physical checks
+1 PDM
(20­CON modifier) days

Knocked back 
knocked back one metre and falls prone there
­1 to all actions
+1 to PDM
a couple of minutes

Blood Poisoning 
On the next day the character falls ill and:
­1 penalty on all checks
+1 penalty to PDM
Make a Constitution check every day. On a failed check the penalty increases by another ­1. If the penalty reaches ­5, the character is unconscious of fever. The character needs to be tended with a successful medicine check to start recovering. The character recovers at the rate of one point of penalty each 24 hours she spends at least 8h resting.

Striking Pain 
­2 to all actions
+2 to PDM
a couple of minutes

Bleeding Wound 
2 points of damage on her own initiative each round
until bound
Binding the wound is a one round action that gets +2 to First Aid check. 

Limb  
arm: on a failed pain threshold check, the character drops what she is holding in her hand
leg: on a failed pain threshold check, the character falls prone

Limb Numb 
leg:
movement score is halved
can’t run or charge
can’t benefit from Dodge ranks to PDM
arm:
can’t use the hand at all. 
4 rounds

Minor Fracture 
­1 penalty to all actions with the limb
leg: +1 to PDM
(20­CON modifier) days
With a successful medicine or surgery check a cast can be applied on the fractured limb. The limb can’t be used while the cast is on, but the wound heals in half time.

Muscle Tear 
­1 to all actions with the limb
limb STR is halved
leg:
+1 to PDM
movement speed is reduced to 75%
a good night’s sleep

Dislocation 
can’t use the limb at all
leg:
falls prone
movement score is halved
can’t run or charge
can’t benefit from Dodge ranks to PDM
Reducing the limb into its normal position is a one round action requiring a first aid check from another character.

Bruised Badly 
­2 to all actions with the limb
leg: +2 to PDM
a couple of minutes

Bleeding Wound 
2 points of damage on her own initiative each round
until bound
Binding the wound is a one round action that gets +2 to First Aid check. 
"""