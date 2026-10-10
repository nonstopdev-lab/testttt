"""Usage:
  python3 make.py tts            # synthesize all voice lines (serial, cached)
  python3 make.py render 1 2 3   # render the given episodes
  python3 make.py render all     # render every episode in 4 parallel workers
  python3 make.py preview 1      # render only the first 8 seconds of episode 1
"""
import sys
from multiprocessing import Pool

import engine
from story import EPISODES


def do_tts():
    n = 0
    for ep in EPISODES:
        for sc in ep["scenes"]:
            for ln in sc["lines"]:
                engine.tts(ln[0], ln[1])
                n += 1
    print("voice lines ready:", n)


def do_render(i):
    out, total = engine.render_episode(i, EPISODES)
    print(f"ep {i}: {out} ({total:.1f}s)", flush=True)
    return out


if __name__ == "__main__":
    cmd = sys.argv[1]
    if cmd == "tts":
        do_tts()
    elif cmd == "preview":
        i = int(sys.argv[2])
        print(engine.render_episode(i, EPISODES, limit=int(sys.argv[3]) if len(sys.argv) > 3 else 240))
    elif cmd == "render":
        do_tts()
        eps = list(range(1, len(EPISODES) + 1)) if sys.argv[2] == "all" else [int(x) for x in sys.argv[2:]]
        with Pool(4) as p:
            p.map(do_render, eps, chunksize=1)
