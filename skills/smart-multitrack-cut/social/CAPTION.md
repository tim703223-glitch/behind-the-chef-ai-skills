We tried to let the AI randomly pick which camera to show. Bad idea — it cuts away from whatever's actually happening, live, with zero judgment.

So instead we built something smarter: a tool that watches the *recorded* footage afterward and picks the right shot based on what's really going on — motion on screen, actual speech on the mic — not a coin flip.

First real test run? It picked the webcam for 100% of a clip where nobody was even talking. Turned out flat room noise was tricking the math into thinking it was a "confident" signal. Found it, fixed it, re-ran it — got a clean, sensible cut.

Then found out the real mic wasn't even wired into the recording the whole time. That's the job, honestly — build it, break it, find out why, fix it for real.

Full build write-up + the actual code: https://github.com/tim703223-glitch/behind-the-chef-ai-skills/tree/main/skills/smart-multitrack-cut
