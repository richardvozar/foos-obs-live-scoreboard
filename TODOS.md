# TODOs

## obs_actions.py and obs_action_utils.py
 - implement functionalities of the buttons that saves clips
   - create separate folder for the clips of different matches
   - place the different clip types inside the match folder into different folders as well
   - folder structure should be something like:
     - /Category_State_Team1_VS_Team2
       - /goals
       - /faults
       - /others
 - implement functionalities of the replay buttons so the manager of the stream can:
   - replay goals, other clips, faults
   - replay the actual set's clips
   - replay the previous set
   - replay the whole match
   - THESE ABOVE should be something like collecting the file name(s) of the clip(s), 
   and put in a media source in OBS and play it.
 - implement the IMMEDIATELY GO BACK TO STREAM button's logic, 
so the stream manager can move back to live anytime if necessary

## control.css
 - UI should be more clean somehow with these many buttons

### TEST EVERYTHING IN A WHOLE MATCH to see the existing issues