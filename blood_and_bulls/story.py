"""BLOOD & BULLS - 20 episode script.

Line format: (speaker, text) or (speaker, text, sfx)
Speakers: N narrator, D Dante, R Rhea, K Kane, L Lina, M Mo
SFX: hit, bell, whoosh, beep, crash, cash, heart, tick
Scene: motif (ring|chart|skyline|pulse), mood (tense|cold|warm|dark), music (fight|tense|soft)
"""


def S(motif, mood, music, lines, **kw):
    d = dict(motif=motif, mood=mood, music=music, lines=lines)
    d.update(kw)
    return d


EPISODES = [
    # ---------------------------------------------------------------- 1
    dict(title="The Bet", scenes=[
        S("ring", "tense", "fight", [
            ("N", "Seven p.m. A warehouse nobody admits exists. Two hundred people. One cage.", "bell"),
            ("N", "Dante Mora. They call him Ghost, because nobody hits him twice."),
        ]),
        S("chart", "cold", "tense", [
            ("N", "In the crowd, Rhea Vance watched numbers instead of fighters."),
            ("N", "Once, she traded billions on Wall Street. Now she trades anything that moves."),
            ("R", "Everyone is betting on the big guy. The line says he loses in round three. I'm all in on Ghost.", "tick"),
        ], up=True),
        S("ring", "tense", "fight", [
            ("N", "Round three. Dante takes a punch that should have ended him."),
            ("D", "Not tonight.", "hit"),
            ("N", "He doesn't fall. The whole room goes silent. And Rhea just made forty thousand dollars.", "cash"),
        ]),
        S("skyline", "warm", "soft", [
            ("R", "You fight like a man with something to lose."),
            ("D", "And you bet like a woman who already lost everything."),
            ("N", "Neither of them was wrong. And that was the problem."),
        ], couple=False),
    ]),
    # ---------------------------------------------------------------- 2
    dict(title="The Tell", scenes=[
        S("chart", "cold", "tense", [
            ("N", "Three a.m. Rhea hasn't slept. Four screens. Forty fights. One pattern."),
            ("R", "Ninety seconds before every bell, the odds move. Always toward the winner.", "tick"),
            ("R", "That isn't luck. That's a leak."),
        ], up=False),
        S("skyline", "dark", "soft", [
            ("D", "You left eight grand on the table. I don't take charity."),
            ("R", "It's not charity. It's your cut. You made me money."),
            ("D", "I fight. I don't gamble."),
            ("R", "Everything is a gamble, Dante. You just get punched when you lose."),
        ]),
        S("chart", "dark", "tense", [
            ("N", "She turned the screen toward him. Forty fights. Forty tells."),
            ("D", "So someone fixes the fights."),
            ("R", "Someone fixes the odds. Which means someone already knows who wins.", "beep"),
            ("N", "On Saturday, Dante was fighting the champion. And the numbers had already picked."),
            ("D", "Then I guess I'm not supposed to win."),
        ], up=False),
    ]),
    # ---------------------------------------------------------------- 3
    dict(title="Lesson One", scenes=[
        S("ring", "warm", "soft", [
            ("N", "Six a.m. An empty gym. A heavy bag that had seen too much."),
            ("D", "You wanted to learn to take a hit? Plant your feet. Chin down. Breathe out when it lands."),
            ("R", "That's it? That's the secret?"),
            ("D", "The secret is you don't flinch. Flinching is what costs you.", "hit"),
            ("R", "Okay. Okay, that one actually hurt."),
        ]),
        S("chart", "warm", "soft", [
            ("R", "My turn. Look at this chart. What do you see?"),
            ("D", "A mountain range. A bad one."),
            ("R", "That's fear. See where it drops, then stops, then everybody panics? The panic is the trade."),
            ("D", "You buy when everyone's scared."),
            ("R", "And you hit when they drop their guard.", "tick"),
        ], up=True),
        S("pulse", "warm", "soft", [
            ("N", "She laughed. He didn't remember the last time someone had made him laugh."),
            ("N", "Two worlds. One language. And neither of them noticed the distance disappearing.", "heart"),
        ]),
    ]),
    # ---------------------------------------------------------------- 4
    dict(title="Lina", scenes=[
        S("pulse", "cold", "soft", [
            ("N", "St. Anne's Hospital. Room two-eleven. The only fight Dante couldn't win with his hands.", "beep"),
            ("L", "You look terrible. Did you lose?"),
            ("D", "I never lose, Lina."),
            ("L", "Liar. You have a black eye and a girlfriend. I can tell."),
            ("D", "She's not my girlfriend."),
        ]),
        S("chart", "cold", "tense", [
            ("N", "Lina was nineteen. Her kidneys were failing. The treatment cost eighty-four thousand dollars."),
            ("N", "That was why Dante fought. Every broken rib had a price tag, and every price tag had her name on it."),
        ], up=False),
        S("skyline", "cold", "soft", [
            ("R", "How much does she need?"),
            ("D", "Eighty-four. I'm at nineteen."),
            ("R", "Then we stop fighting for rent money, and we start making your money work.", "tick"),
            ("D", "Rhea, I can't lose what I don't have."),
            ("R", "That's exactly why you can't lose.", "heart"),
        ]),
    ]),
    # ---------------------------------------------------------------- 5
    dict(title="First Trade", scenes=[
        S("chart", "warm", "tense", [
            ("R", "Two thousand dollars. Your last purse. Rule one: never risk what you can't afford to lose."),
            ("D", "That's all I can afford to lose."),
            ("R", "Then we're going to be very careful. Buy now. Watch the line.", "tick"),
            ("N", "The chart crawled up. Dante held his breath like it was round twelve."),
            ("D", "It's moving! It's up! How much?"),
            ("R", "Eleven percent. You just won without bleeding.", "cash"),
        ], up=True),
        S("pulse", "warm", "soft", [
            ("N", "Dante laughed. A real laugh. The kind that comes from somewhere you thought was broken."),
        ]),
        S("chart", "dark", "tense", [
            ("N", "Then the market turned. Fast."),
            ("D", "It's dropping. Rhea, it's dropping!", "crash"),
            ("R", "Rule two. Cut your losers like a bad corner man. Sell. Now."),
            ("N", "He sold. Lost one hundred dollars. Saved eight hundred."),
            ("R", "That's the whole game. Survive the round, win the fight."),
        ], up=False),
    ]),
    # ---------------------------------------------------------------- 6
    dict(title="The Offer", scenes=[
        S("skyline", "dark", "tense", [
            ("N", "A black car outside the gym. A man in a coat that cost more than Dante's whole life."),
            ("K", "Mr. Mora. Victor Kane. I own the league you fight in."),
            ("K", "Two hundred fifty thousand dollars. One contract. Three fights. You fight for me, exclusively."),
            ("D", "That's more than I need."),
            ("K", "That is exactly why I offered it.", "tick"),
        ]),
        S("chart", "tense", "tense", [
            ("N", "Across town, Rhea saw the name on a screen. Her blood ran cold."),
            ("R", "Kane Capital. Victor Kane. He was my boss. He fired me when I refused to hide his losses."),
            ("N", "She'd been blacklisted by every desk on Wall Street. Because of him."),
            ("R", "Dante. Don't sign anything.", "beep"),
        ], up=False),
        S("ring", "tense", "fight", [
            ("N", "But Dante was already looking at the number. And behind it, Lina's face."),
            ("N", "Some deals look like rescue. Until the door closes behind you.", "bell"),
        ]),
    ]),
    # ---------------------------------------------------------------- 7
    dict(title="Rooftop", scenes=[
        S("skyline", "warm", "soft", [
            ("N", "Midnight. The market was closed. For the first time in years, so was Rhea."),
            ("D", "You never told me why you got into trading."),
            ("R", "Because numbers don't lie. People do."),
            ("D", "And what about me?"),
            ("R", "You're the first thing that doesn't fit the model."),
        ], couple=True),
        S("pulse", "warm", "soft", [
            ("D", "I'm scared, Rhea. Not of the cage. Of this."),
            ("R", "Good. That means it's real.", "heart"),
            ("N", "He kissed her. And for one perfect minute, nobody on that rooftop was losing."),
        ]),
        S("skyline", "dark", "tense", [
            ("N", "Somewhere below, a phone buzzed. A text from an unknown number."),
            ("N", "Saturday. Round four. You know what to do.", "beep"),
        ], couple=True),
    ]),
    # ---------------------------------------------------------------- 8
    dict(title="Signed", scenes=[
        S("chart", "dark", "tense", [
            ("N", "The contract was thirty pages. Dante read twenty-nine. Page thirty was the knife."),
            ("N", "Clause nine. The fighter agrees to lose by knockout in round four of the championship bout."),
            ("K", "It's only a story, Mr. Mora. The crowd loves a fall. And your sister walks out of that hospital healthy.", "tick"),
        ], up=False),
        S("pulse", "cold", "soft", [
            ("L", "Danny, why is there a man in a suit in my room paying my bills?"),
            ("N", "It was already done. The treatment had started."),
            ("D", "Because I made a deal, Lina."),
        ]),
        S("ring", "dark", "tense", [
            ("N", "He signed. One signature. Black ink. Not a word to Rhea."),
            ("N", "He told himself it was to protect her.", "hit"),
            ("N", "That was the first lie. And lies, like bad trades, compound."),
        ]),
    ]),
    # ---------------------------------------------------------------- 9
    dict(title="Leverage", scenes=[
        S("chart", "cold", "tense", [
            ("N", "Rhea didn't know about the contract. But she knew Kane."),
            ("R", "He moves money like a magician. You look at his right hand while the left hand steals the room."),
            ("R", "Fixed fights create clean money. Win, lose, it doesn't matter. The books always balance.", "tick"),
        ], up=True),
        S("chart", "tense", "tense", [
            ("N", "She dug through every filing. Every shell company. Every offshore account."),
            ("R", "There it is. Forty to one leverage. Kane Capital owns forty times what it actually has."),
            ("R", "If the money stops flowing for even one night, the whole castle burns.", "beep"),
            ("N", "She didn't have an army. She had a laptop, forty thousand dollars, and nothing left to lose."),
        ], up=False),
        S("skyline", "dark", "soft", [
            ("N", "She called Dante. He didn't pick up."),
            ("N", "And for the first time, the numbers weren't enough."),
        ]),
    ]),
    # ---------------------------------------------------------------- 10
    dict(title="The Script", scenes=[
        S("chart", "tense", "tense", [
            ("N", "Saturday morning. Odds are posted for the championship. Rhea stared at the screen."),
            ("R", "Ninety percent on the champion. Round four. Knockout. Every bet on one line."),
            ("R", "That isn't a prediction. That's a script.", "beep"),
        ], up=False),
        S("skyline", "dark", "tense", [
            ("N", "She ran to the gym. Dante was wrapping his hands."),
            ("R", "Tell me the odds are wrong."),
            ("D", "Rhea..."),
            ("R", "Tell me you're not on the wrong side of this."),
            ("N", "Silence is the loudest answer there is."),
        ]),
        S("ring", "tense", "fight", [
            ("R", "You signed. You signed with him. After everything I told you."),
            ("D", "He's paying for Lina."),
            ("R", "And what is he paying you with? Your name?", "hit"),
            ("N", "Outside, the crowd was already chanting. The cage was already waiting.", "bell"),
        ]),
    ]),
    # ---------------------------------------------------------------- 11
    dict(title="Confession", scenes=[
        S("pulse", "dark", "soft", [
            ("D", "I was going to tell you. I swear. Every night I tried."),
            ("R", "For three weeks I showed you charts. I showed you everything. I trusted you."),
            ("D", "I didn't have a choice."),
            ("R", "There is always a choice, Dante. You made yours."),
        ]),
        S("ring", "tense", "fight", [
            ("N", "But in the arena, the lights were on. Eight thousand voices. And a script."),
            ("N", "Dante walked out anyway. Because when you've been cornered long enough, you stop seeing the door.", "bell"),
        ]),
        S("chart", "dark", "tense", [
            ("N", "From the crowd, Rhea watched. Her hand shook on her phone."),
            ("R", "If he lies down, I lose him. If he wins, he loses everything else."),
            ("N", "Round one. Round two. Round three."),
            ("N", "The knockout was coming. Everyone in the building knew it.", "heart"),
        ], up=False),
    ]),
    # ---------------------------------------------------------------- 12
    dict(title="The Fall", scenes=[
        S("ring", "tense", "fight", [
            ("N", "Round four. The bell rang. Dante looked at the champion. Then at the crowd. Then at Rhea.", "bell"),
            ("N", "He raised his guard. Then he dropped it."),
            ("N", "The champion's right hand came in like a verdict.", "hit"),
            ("N", "Dante went down. Ten seconds. Nine. Eight."),
        ]),
        S("pulse", "dark", "soft", [
            ("N", "In the crowd, Rhea didn't cheer. She didn't scream. She just walked out."),
            ("R", "He chose the money. Fine. I won't be here for the count."),
        ]),
        S("skyline", "cold", "soft", [
            ("N", "Three in the morning. An empty ring. A fighter with nothing left."),
            ("D", "I did what I had to do, Lina."),
            ("L", "Did you? Because you sound like someone who just sold his soul for my kidneys."),
            ("N", "Love is the only trade you can't hedge. And he'd just taken a position against it."),
        ]),
    ]),
    # ---------------------------------------------------------------- 13
    dict(title="Collateral", scenes=[
        S("pulse", "cold", "tense", [
            ("N", "Two days later. The hospital called. Lina's treatment had been moved."),
            ("L", "They're transferring me. Danny, who are these people?", "beep"),
            ("N", "A nurse who didn't look up. A clipboard with Kane Capital stamped on every page."),
        ]),
        S("skyline", "dark", "tense", [
            ("K", "You did beautifully, Mr. Mora. A very convincing fall."),
            ("D", "My sister. Where is she?"),
            ("K", "Safe. For now. I've decided you'll fight again. And lose again. Twice more."),
            ("D", "The contract said one."),
            ("K", "Contracts are like markets, Mr. Mora. They change when I say so.", "tick"),
        ]),
        S("ring", "dark", "fight", [
            ("N", "That was the moment Dante understood. It had never been a deal. It was a leash."),
            ("N", "And the only person who could cut it had just walked away from him.", "hit"),
        ]),
    ]),
    # ---------------------------------------------------------------- 14
    dict(title="The Short", scenes=[
        S("chart", "cold", "tense", [
            ("N", "Rhea didn't go home. She went to war."),
            ("R", "Kane Capital's stock is overbought. Bloated. Leveraged to the sky. It only needs a push."),
            ("R", "I can short it. If I time it right, one night, one move, and it all comes down.", "tick"),
        ], up=False),
        S("chart", "tense", "tense", [
            ("M", "Rhea, it's Mo. I heard what you're planning. It's suicide."),
            ("R", "Mo, I need margin. Five million dollars."),
            ("M", "You have forty thousand."),
            ("R", "I have a plan. And Kane has a weakness. His fights."),
            ("M", "Why the fights?"),
            ("R", "Because he can fix a cage. He can't fix a knockout he didn't plan."),
        ], up=True),
        S("skyline", "dark", "soft", [
            ("N", "The trade wasn't ready. But the man who could trigger it was waiting for her, in the ring."),
        ]),
    ]),
    # ---------------------------------------------------------------- 15
    dict(title="Ghost Trains", scenes=[
        S("ring", "dark", "soft", [
            ("N", "Five a.m. No cameras. No crowd. Just a man and a bag."),
            ("D", "Dad, you told me. Never take a dive. It costs more than the money."),
            ("N", "His father had been a boxer too. A good one, until he took one fall for the wrong man."),
            ("N", "He never fought again. He never forgave himself.", "hit"),
        ]),
        S("pulse", "cold", "soft", [
            ("D", "Lina, I'm going to fix this."),
            ("L", "Danny, stop trying to save me. Start trying to save yourself."),
            ("N", "He hung up. He looked at his hands. The same hands that signed the contract."),
        ]),
        S("ring", "tense", "fight", [
            ("N", "He trained like a man possessed. Because the only thing worse than losing is losing on purpose.", "hit"),
            ("D", "Never again."),
            ("N", "And then the gym door opened.", "bell"),
        ]),
    ]),
    # ---------------------------------------------------------------- 16
    dict(title="Reunion", scenes=[
        S("skyline", "cold", "soft", [
            ("R", "I'm not here to forgive you."),
            ("D", "I wouldn't ask you to."),
            ("R", "I'm here because I have a plan. And it needs a fighter who won't fall."),
            ("D", "Tell me."),
        ]),
        S("chart", "warm", "tense", [
            ("R", "Kane scripted round four of the next fight. Every dollar of his empire is leveraged against it."),
            ("R", "At the moment you were meant to fall, I short his company with everything I have."),
            ("D", "And if I stay on my feet?"),
            ("R", "Then his bets collapse. His books break. His margin calls arrive all at once.", "crash"),
            ("D", "A dive is a trade. A win is a margin call."),
        ], up=False),
        S("pulse", "warm", "soft", [
            ("N", "She looked at him. Just for a second, the old Rhea came back."),
            ("R", "Don't make me regret this."),
            ("D", "I'll make you the best trade you ever made.", "heart"),
        ]),
    ]),
    # ---------------------------------------------------------------- 17
    dict(title="Frozen", scenes=[
        S("chart", "tense", "tense", [
            ("N", "Three days before the fight, Rhea logged in to her trading account."),
            ("R", "Access denied. Account restricted. Under review.", "beep"),
            ("R", "Kane. He knows."),
            ("N", "Forty thousand dollars. Locked. Her entire war chest, gone with a keystroke."),
        ], up=False),
        S("skyline", "dark", "tense", [
            ("K", "I admire you, Rhea. Truly. You could have been great. But you were always too honest."),
            ("R", "And you were always too afraid to lose."),
            ("K", "I'm not afraid. I'm prepared. You have nothing. And the fighter has less."),
            ("N", "He hung up. Rhea stared at the screen. Silence. Then a ring.", "tick"),
        ]),
        S("pulse", "warm", "soft", [
            ("M", "It's Mo. I'm not letting you go in alone. I put my firm's name behind you. Five million, locked and ready."),
            ("R", "Mo, you'll be ruined if this fails."),
            ("M", "Then you'd better not fail.", "heart"),
        ]),
    ]),
    # ---------------------------------------------------------------- 18
    dict(title="The File", scenes=[
        S("pulse", "cold", "soft", [
            ("L", "I've been in this hospital for six weeks. Do you know what I do all day? I watch."),
            ("L", "The nurses talk. The paperwork talks. Kane's company pays this entire wing."),
            ("L", "And the head of the hospital signs it off, every Tuesday, in a private office.", "tick"),
        ]),
        S("chart", "tense", "tense", [
            ("L", "Rhea, it's Lina. I took photos. Every invoice. Every transfer. It's all here."),
            ("R", "Lina, you could get hurt."),
            ("L", "I'm already sick. I'd rather be useful."),
            ("N", "Bribes. Shell companies. Payments for fighters, for doctors, for silence."),
            ("R", "This isn't a trade, Lina. This is an indictment.", "beep"),
        ], up=True),
        S("skyline", "warm", "soft", [
            ("N", "Rhea sent it to a federal prosecutor she once trusted. The reply came in four minutes."),
            ("N", "We can move. But only if the market breaks first.", "heart"),
        ]),
    ]),
    # ---------------------------------------------------------------- 19
    dict(title="Round Four", scenes=[
        S("ring", "tense", "fight", [
            ("N", "Fight night. Ten thousand people. Kane in the front row, smiling. The champion in the cage.", "bell"),
            ("D", "Here we go."),
            ("N", "Rounds one through three. The champion pounded. Dante absorbed. He was holding on."),
        ]),
        S("chart", "tense", "tense", [
            ("R", "Mo, the bell is about to ring. Are we ready?"),
            ("M", "Positions loaded. Five million. Say the word.", "tick"),
            ("N", "Round four. The exact second Kane had written."),
        ], up=False),
        S("ring", "tense", "fight", [
            ("N", "The champion threw the right hand. The one that was supposed to end it."),
            ("N", "Dante slipped it. He slipped it like a ghost.", "whoosh"),
            ("D", "My name is not on your script."),
            ("N", "The crowd went wild. Kane stood up, white as paper."),
            ("R", "Now, Mo. Sell everything.", "crash"),
        ]),
    ]),
    # ---------------------------------------------------------------- 20
    dict(title="Closing Bell", scenes=[
        S("chart", "tense", "fight", [
            ("N", "Kane's stock opened down eight percent. Then twenty. Then the circuit breakers hit.", "crash"),
            ("M", "It's a massacre, Rhea! Margin calls on every desk!"),
            ("R", "Hold. Hold. Let it fall."),
        ], up=False),
        S("ring", "tense", "fight", [
            ("N", "In the ring, Dante turned the fight inside out. Round six. Round seven."),
            ("N", "And in round eight, the champion finally fell.", "hit"),
            ("N", "The referee counted to ten. And Ghost stood alone in the light.", "bell"),
        ]),
        S("skyline", "dark", "tense", [
            ("N", "Outside, federal agents were already walking toward the door."),
            ("K", "This is impossible. I own everything."),
            ("N", "You never own the one thing that refuses to stay down.", "tick"),
        ]),
        S("skyline", "warm", "soft", [
            ("L", "Danny! I'm cleared. The new hospital says I'm cleared!"),
            ("R", "We did it."),
            ("D", "No. You did. Every trade. Every round."),
            ("N", "He kissed her on the rooftop where it began. The market was closed. The city was finally quiet.", "heart"),
            ("N", "Some trades are worth every risk. This one was love. End of season one."),
        ], couple=True),
    ]),
]
