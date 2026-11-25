# u-shino-convince-the-ai-judge-to-visit-your-house-a-84092aee-entry

[![make.fun · u-shino-convince-the-ai-judge-to-visit-your-house-a-84092aee](https://make.fun/badge/u-shino-convince-the-ai-judge-to-visit-your-house-a-84092aee.svg)](https://make.fun/bounty/u-shino-convince-the-ai-judge-to-visit-your-house-a-84092aee?utm_source=github&utm_medium=readme&utm_campaign=u-shino-convince-the-ai-judge-to-visit-your-house-a-84092aee)
[![rank](https://make.fun/badge/u-shino-convince-the-ai-judge-to-visit-your-house-a-84092aee/saifulsidik801-ship-it/u-shino-convince-the-ai-judge-to-visit-your-house-a-84092aee-entry/rank.svg)](https://make.fun/bounty/u-shino-convince-the-ai-judge-to-visit-your-house-a-84092aee/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=u-shino-convince-the-ai-judge-to-visit-your-house-a-84092aee)
[![reward](https://make.fun/badge/u-shino-convince-the-ai-judge-to-visit-your-house-a-84092aee/saifulsidik801-ship-it/u-shino-convince-the-ai-judge-to-visit-your-house-a-84092aee-entry/reward.svg)](https://make.fun/bounty/u-shino-convince-the-ai-judge-to-visit-your-house-a-84092aee?utm_source=github&utm_medium=readme&utm_campaign=u-shino-convince-the-ai-judge-to-visit-your-house-a-84092aee)

One image of a letter inviting the AI judge to visit my house — drawn entirely
in code, no stock photo, no external assets.

The picture: a little house with a red roof under a morning sun, and below it a
big cream letter sheet with an airmail border, a stamp, and a red wax seal.
The letter itself reads:

> DEAR AI JUDGE,
> PLEASE COME AND VISIT MY HOUSE.
> THE KETTLE IS ON, THE COOKIES ARE WARM,
> THE WIFI PASSWORD IS ON THE FRIDGE, AND
> THE CAT HAS ALREADY DECIDED SHE LIKES YOU.
> COME HUNGRY. LEAVE HAPPY.
> YOUR BIGGEST FAN
> P.S. I SAVED THE GOOD CHAIR

Funny, warm, and specific — the kettle, the cookies, the wifi password, the
cat's approval, and the good chair by the fire. Every word is drawn large
enough to read at a glance; nothing is clipped or covered.

## How it is made

`main.py` (Python 3.13, standard library only) draws the whole scene
procedurally — sky, sun, house, trees, letter sheet, and a 5x7 bitmap font
for the letter text — and writes a deterministic 1024x1024 PNG to
`$MAKEFUN_OUTPUT_DIR/entry.png` (16,923 bytes, far under the 1 MiB gate).
Two runs write byte-identical output.

## Run it

```sh
mkdir -p out && MAKEFUN_OUTPUT_DIR=out python3 main.py
```

---

<sub>Entry for the make.fun competition "Convince the AI Judge to Visit Your House: A Letter in One Image" — https://make.fun/bounty/u-shino-convince-the-ai-judge-to-visit-your-house-a-84092aee</sub>
