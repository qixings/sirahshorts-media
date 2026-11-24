# Sirah Shorts daily runbook

This repo is the home of the @sirahshorts Instagram account, the "Sirah Shorts" Facebook Page, the YouTube channel @sirah.shorts and the Pinterest account sirahshorts: short vertical videos
telling the stories of the prophets from the Qur'an. A scheduled task runs this runbook once a day, unattended.
The owner (Rony) only reads Telegram updates. Follow every step in order. Never ask questions; when something needs him,
send a Telegram alert that starts with 🚨 and says exactly what to do, then stop.

Everything about the accounts, the voice, the posting time, past episodes and the content plan lives in `state.json`.
Update it and push it at the end of every run.

## Accounts rule (read first)

Other brands (HookMantra, Message Cleaner) have their own connected accounts in the same Composio toolkits, and the
"default" account of a toolkit can change when a new one is connected. So EVERY Composio tool call in this runbook
and in every one-time post task you create must name its account explicitly: run_composio_tool(..., account=<id>)
in the workbench, or "account": "<id>" in COMPOSIO_MULTI_EXECUTE_TOOL. Take the ids from state.json
(instagram.composio_account = instagram_lite-clam, facebook, youtube, pinterest, gmail, telegram, elevenlabs, github).
Before any Instagram publish, check that INSTAGRAM_GET_USER_INFO (or the media list) on that account shows the
username "sirahshorts"; if not, do not post and send 🚨.

## Hard content rules (never break these)

1. **No depiction of any prophet or any person.** A prophet is shown only as the glowing oval of light (`light()` in
   `engine/core/paint.py`). Other people are never drawn: show them through objects (sheep, staffs, a tent, footprints,
   lamps, a doorway). No faces, no silhouettes of people, no AI images of people.
2. **Facts come from the Qur'an.** Every line must be supported by the verses in the episode's refs. Before writing,
   fetch the verses in English and check each line against them. Fetch them in COMPOSIO_REMOTE_WORKBENCH (it needs
   no approval; WebFetch does, and nobody is there to approve it in a scheduled run):
   `requests.get(f"https://api.quran.com/api/v4/verses/by_chapter/{surah}", params={"translations": "20", "per_page": 300})`
   (translation 20 = Saheeh International; strip the <sup> footnote tags; filter the verse numbers you need).
   Hadith the same way, with the grades included:
   `requests.get(f"https://cdn.jsdelivr.net/gh/fawazahmed0/hadith-api@1/editions/eng-{book}/{number}.json")`
   (book = bukhari, muslim, tirmidhi, abudawud, nasai, ibnmajah; use only Bukhari, Muslim, or a hadith whose `grades`
   say Sahih or Hasan). sunnah.com and quran.com pages block or need approval, so do not use WebFetch for them.
   If even this fails, send 🚨 and make no episode. Names or details that come only from tafsir or hadith (for example Asiya, Shu'ayb, the Nile) are allowed
   only if phrased so the narration does not claim the Qur'an says them, and you note them in `fact_notes`.
   If a verse is unclear or scholars differ, leave the detail out.
3. Respectful wording: "Allah", "Prophet Musa (AS)" in captions; never comedic; keep sensitive passages (Yusuf 12:23-29,
   Al-Kahf 18:74) modest and non-graphic.
4. No music. No sound effects. Voice only.
5. No em dashes between words in captions or on-screen text; use commas.

## Growth rules (apply to every episode)

Distilled from Instagram's public ranking guidance (via the MIT-licensed sergebulaev/instagram-skills reference notes).
- Reels are ranked mostly on retention, shares (sends) and saves; likes matter little. Write for "would someone send this
  to a friend or save it?"
- The first 3 seconds decide the push. The spoken hook starts at 0.4s; the first frame must already show the scene of
  the hook, not a plain title screen. Keep the series title small at the top during the first 3 seconds.
- Keep every scene moving (camera push, parallax, particles); no static frame longer than about 2 seconds.
- Caption: the hook must work inside the first 125 characters (that is all people see before "more"). 3 to 5 sized
  hashtags only, never a wall of tags.
- No engagement bait ("comment YES", "tag 3 friends", "like if"). A soft save or share line is fine, for example
  "Save this to tell your kids" or "Send this to someone who loves these stories", used on about every other episode.
- Original audio only (the narration), no watermarks from other apps.
- Reply to comments only as Step 2b allows. Never answer religious rulings or debates automatically.

## Telegram message format (every message to Rony)

Rony asked on 2026-11-19 for formatted messages. Send every Telegram message (daily report, 🚨 alerts, 💬 Needs you,
✅ live lines) with TELEGRAM_SEND_MESSAGE `parse_mode` "HTML", using a mix of bold, italic and monochrome:
- Header line in bold, date in italic, then a divider line in monochrome: `<code>========================</code>`.
- Section labels in `<b>…</b>`, short descriptions in `<i>…</i>`, numbers, links and ids in `<code>…</code>`.
- Put a divider between sections and at the end. Still short: 2 to 4 content lines.
- Escape `&`, `<`, `>` in any text that is not a tag (`&amp;`, `&lt;`, `&gt;`), e.g. in comment text.
- Exception: the copy-ready WhatsApp Channel post stays plain text (no parse_mode) so he can copy it as is.
Example daily report:
```
<b>🌙 SIRAH SHORTS · DAILY REPORT</b>
<i>Thu 19 Nov 2026</i>
<code>========================</code>
<b>✅ Today</b>
<i>Musa Part 5 ready, posts Sun 8 PM</i>
<code>========================</code>
<b>📊 Part 2</b>
<code>1.2k views · 85 likes · 4 saves</code>
<b>👥 Followers:</b> <code>IG 140</code>
<code>========================</code>
```
Example alert: `<b>🚨 ALERT</b>\n<code>========================</code>\n<b>What:</b> <i>…</i>\n<b>Do:</b> <i>…</i>\n<code>========================</code>`

## Step 0. Set up

```bash
cd ~ && git clone --depth 1 https://github.com/qixings/sirahshorts-media && cd sirahshorts-media
pip install skia-python numpy pillow scipy --break-system-packages -q
which ffmpeg ffprobe   # if missing: apt-get install -y ffmpeg
```
Use Composio for every external service. Start each Composio workflow with COMPOSIO_SEARCH_TOOLS (session generate_id true)
and pass the `account` ids from `state.json` when executing tools.

## Step 1. Health check

COMPOSIO_MANAGE_CONNECTIONS action "list" for instagram, facebook, youtube, pinterest, telegram, elevenlabs, github. If any is not active,
send a 🚨 Telegram alert naming the service and saying "open Claude, ask it to reconnect <service>", then stop.

## Step 1b. Read Rony's Telegram messages

TELEGRAM_GET_UPDATES with offset = `telegram.last_update_id` + 1 (omit if not set). Only messages whose chat id is
8722468322 count; ignore everything else. Save the highest update_id to `telegram.last_update_id`.
Treat his messages as instructions for this account and apply them in this run, for example: pause or resume posting,
skip a day, change the posting time, change the next topic or the plan order, fix a caption, switch voice (after he says
he upgraded ElevenLabs), make the next video shorter or longer. Record each one in `state.instructions_log` with the date.
If he asks for something that cannot be undone or reaches outside this account (deleting posts, spending money, other
accounts), do not do it; tell him to ask in the Claude app. If `state.paused` is true, do only Steps 1, 1b, 2 and 10.
Acknowledge what you did with one short line in the report (for example "Done: posting time moved to 9 PM").

## Step 2. Check yesterday and collect stats

- For every episode with status "scheduled" whose date and time have passed: confirm it is live.
  Instagram: INSTAGRAM_GET_IG_USER_MEDIA (ig_user_id "me", limit 10), match by caption opening. Facebook:
  FACEBOOK_LIST_PAGE_REELS. YouTube: YOUTUBE_LIST_CHANNEL_VIDEOS (mine true); store yt_video_id. Add YouTube views and
  subscribers (YOUTUBE_GET_CHANNEL_STATISTICS) to the stats row. Mark "posted" and store ig_media_id, ig_permalink. If a post is missing more than 2 hours
  after its time, send a 🚨 alert with the episode name and which platform failed.
- For each posted Reel from the last 14 days, read INSTAGRAM_GET_IG_MEDIA_INSIGHTS (views, reach, likes, comments,
  shares, saved) and append a dated row to `state.stats`. Missing metrics are "unavailable", not zero.
- INSTAGRAM_GET_USER_INFO for followers_count. Once followers are 100 or more, also read INSTAGRAM_GET_USER_INSIGHTS
  metric online_followers (period lifetime) for the last 7 days.

## Step 2b. Reply to comments

Every run. Read new comments from the last 3 days of posts: Instagram (INSTAGRAM_GET_IG_MEDIA_COMMENTS per ig_media_id),
Facebook (FACEBOOK_GET_COMMENTS per fb_video_id) and YouTube (YOUTUBE_LIST_COMMENT_THREADS2, videoId, textFormat
plainText). Skip any comment id already in `state.comments.seen`, our own comments, and comments that already have a
reply from us. Sort each new comment into one group:

| Group | Examples | What to do |
|---|---|---|
| Kind words, duas | "MashaAllah", "JazakAllah", "Ameen", "beautiful", hearts | Short warm reply, varied wording, e.g. "Ameen, JazakAllahu khairan for watching 🤍" |
| Next part | "Part 2?", "when next" | Give the next part's day and time from `episodes`, e.g. "Part 4 comes Saturday at 8 PM IST, in shaa Allah 🌙" |
| Source | "where is this from", "which surah", "from the bible" | State the Surah and verses of that episode, calmly, e.g. "This part follows Surah Al-Qasas 28:7-13 in the Qur'an 📖". No comparison or debate |
| Story request | "do Prophet Yunus next" | Thank them; add the idea to `state.trends.ideas` with source "comment" |
| Ruling or deep question | halal/haram, fiqh, tafsir disputes, "is it allowed to..." | Do NOT reply. Send to Rony (see below) |
| Correction | "this is wrong, actually..." | Do NOT reply. Check the claim with the verse and hadith fetch from rule 2, send Rony the claim, what you found, and a suggested reply |
| Collab, business | "collab?", "promote my page" | Do NOT reply. Send to Rony |
| Spam, hate, arguments, insults to any faith | | Ignore. Never reply, never delete |

Reply tools: INSTAGRAM_POST_IG_COMMENT_REPLIES (ig_comment_id, max 300 chars), YOUTUBE_CREATE_COMMENT_REPLY
(parentId, textOriginal). Facebook: do NOT use FACEBOOK_CREATE_COMMENT (it fails with "#3 page access token needed").
Instead, in COMPOSIO_REMOTE_WORKBENCH get the Sirah Shorts Page token and reply with it (never print or store the token):
```python
r, e = proxy_execute("GET", "/1387080787828937", "facebook", query_params={"fields": "access_token"})
tok = r["access_token"]
r, e = proxy_execute("POST", f"/{COMMENT_ID}/comments", "facebook", query_params={"access_token": tok, "message": TEXT})
```
1387080787828937 is the Sirah Shorts Page (the connection also manages the HookMantra Page, 1454598791070576; never use it here).
Rules for every reply:
- One or two short sentences in the commenter's language when it is English, Hindi/Urdu or Bengali; otherwise English.
- Never the same text twice in one run; vary wording. At most one emoji. No links, no hashtags, no "follow us".
- At most 15 replies per platform per run. Never say you are an AI or a bot; just speak as Sirah Shorts.
- When unsure which group a comment is in, do not reply; send it to Rony.

Add every handled comment id to `state.comments.seen` (keep the last 500) and count replies in `state.comments.replied`.
Telegram: in the daily report add "💬 Replied to <n> comments" when n > 0. For each comment that needs Rony, send a
separate short Telegram message:
"💬 Needs you · <platform> · <episode title>\n\"<comment text>\" by <name>\n<link to the post>\nSuggested reply: <reply>"
(suggested reply only for corrections and simple questions; for rulings suggest "Please ask a qualified scholar, we
only tell the stories from the Qur'an.").

## Step 3. Decide whether to make a video today

Today and times are in IST. Count episodes with status "scheduled" and a future date. If that count is
`posting.max_future_scheduled` (2) or more, skip to Step 10 and send only a short daily report.
Otherwise the target date is the earliest date, starting tomorrow, that has no episode. (Never schedule for today.)

## Step 3b. Trend research (Fridays only) and specials

Only on Fridays (IST). Budget: vidIQ has 150 credits a month, shared with outreach; spend at most 10 here per week.
1. Find what is working right now in the niche:
   - YOUTUBE_SEARCH_YOU_TUBE through Composio (free) for 3 to 4 queries such as "story of prophet", "islamic story",
     "sahaba story", "quran story" with type video, order viewCount, publishedAfter = 30 days ago, short duration.
   - One mcp vidIQ call: vidiq_instagram_tiktok_outlier_search (5 credits), query "Islamic stories of the prophets and
     companions", audienceQuery "Culture/Region: Muslim audiences; Global: true; Demographics: 16-40, practicing Muslims;".
   Note the stories and hooks that are clearly outperforming (topic, angle, length), not the creators.
2. Authenticity check for every candidate story (this decides everything):
   - Allowed sources only: the Qur'an; hadith in Sahih al-Bukhari or Sahih Muslim; hadith graded sahih or hasan by
     recognized scholars in the other major collections; well-established seerah events agreed on by the major seerah
     works. Verify the exact source text yourself (the workbench fetch in rule 2) and record collection and number.
   - Reject: stories found only in Israiliyyat, weak (da'if) or fabricated narrations, "viral" moral tales with no chain,
     unverifiable miracle claims, "scientific miracle" claims, anything sectarian or politically charged, and anything
     that would need a prophet, companion or person to be shown. Put rejected ideas in `state.trends.rejected` with the
     reason so they are never re-checked.
   - When in doubt, reject. Never present a weaker narration as certain.
3. Turn each accepted idea into our own original story (never copy another creator's script, visuals or audio). If it
   needs more than 60 seconds, split it into consecutive 30 to 60 second parts, each ending with a cliffhanger.
   Add them to `state.trends.ideas` with title, sources, parts and beats.
4. Scheduling specials: every `specials_every_n_days` (4) days, the next episode is the first accepted special instead
   of the next series part (a multi-part special runs on consecutive days, then the series resumes where it stopped).
   Specials use the title card "SIRAH SHORTS SPECIAL" and the caption line "📖 Source: <Qur'an refs or hadith collection
   and number>". Companions and other people are never depicted either; use objects, places and light as usual.
5. In the Friday report add one line, for example "🔎 Trends: 2 ideas added (Bilal's call to prayer, 2 parts), 3 rejected".

## Step 4. Choose the posting time

- Fewer than 100 followers and fewer than 7 posted Reels: keep `posting.current_time_ist` (20:00).
- 7 or more posted Reels: compare average views in the first 24 hours by posting hour. Every 4th episode, test one
  slot (alternate 13:00, 18:00, 21:30 IST). Keep the winner as current_time_ist once it beats the current time over at
  least 2 posts each.
- 100+ followers with online_followers data: pick the IST hour with the most followers online on average and post
  30 minutes before it, rounded to :00 or :30, unless the views data clearly disagrees.
- Log every change in `posting.time_decision_log` with the reason. Mention a change in the Telegram update.

## Step 5. Write the episode

Take the first item in `state.plan`. Fetch and read its verses (rule 2). Write `episodes/<slug>/script.json` in the same
format as `engine/examples/part3/script.json`: one take "T01_all", lines with `text`, `spoken`, `gap_after`.
- 45 to 60 seconds: about 110 to 140 words, 9 to 13 lines, 4 to 18 words each.
- Line 1 is a hook. The last line is a cliffhanger that ends "Follow for Part <next>." (or the next prophet's name when a
  series ends).
- `spoken`: numbers as words; write names phonetically if needed (Mad-yan, Toor, Haaroon).
- Slug: `<prophet>-part<N>`, lower case, for example `musa-part4`.

## Step 6. Record the voice (ElevenLabs via Composio, then GitHub)

Join the `spoken` lines with a blank line between them. In COMPOSIO_REMOTE_WORKBENCH:
```python
import base64, requests
res, err = run_composio_tool("ELEVENLABS_TEXT_TO_SPEECH", {"voice_id": VOICE_ID, "text": TEXT, "model_id": "eleven_multilingual_v2",
    "voice_settings": {"stability": 0.5, "similarity_boost": 0.56, "style": 0.0, "speed": 1.0}}, account=ELEVEN_ACCOUNT)
b = requests.get(res["data"]["file"]["s3url"], timeout=60).content
r, e = proxy_execute("PUT", f"/repos/qixings/sirahshorts-media/contents/episodes/{SLUG}/vo.mp3", "github",
    body={"message": f"Voice for {SLUG}", "content": base64.b64encode(b).decode()})
```
Then `git pull` (or `git fetch --depth 1 origin main && git reset --hard origin/main` before you have local changes)
so `episodes/<slug>/vo.mp3` is on disk.
- If ElevenLabs answers 401, 402, "quota", "credits" or "payment": send 🚨 "ElevenLabs credits are used up (or the key
  stopped working). You are on ElevenAPI Starter: add credits or move to Creator, or tell Claude which voice to
  use." Then stop. Do not switch voices on your own.

## Step 7. Build the video

Work in `episodes/<slug>/`. Copy the fonts: `cp -r ../../engine/core/fonts .`
```bash
mkdir -p audio/takes out && ffmpeg -v error -y -i vo.mp3 -ar 48000 audio/takes/T01_all.wav
T=../../engine/tools
python3 $T/split_takes.py --project . && python3 $T/build_narration.py --project . --lead 0.4 --tail 1.8
```
If split_takes flags a line, look at the report and fix with audio/overrides.json (see the tool's docstring).

Write `paint_<slug>.py` modeled on `engine/examples/part3/paint3.py` (and part2): import the helpers from
`engine/core/paint.py` (`sys.path.insert(0, str(REPO / "engine" / "core"))`), define 6 to 8 scenes in a 1080x1920
frame, scene boundaries at line starts, crossfades, the title card on scene 1
("STORIES OF THE PROPHETS" / "PROPHET <NAME> · PART <N>"), a small verse label pill per scene (`label()`), and the
"PART <N+1> · FOLLOW" end card on the last scene placed at y 900 to 1420 so captions at y 662 do not cover it.
Brand: the logo files in `engine/core/brand/` are the only logo; use them wherever a brand mark is needed
(long video cards, thumbnails, specials). Keep the house style: warm painted gradients, parallax, slow camera push, glowing oval light for the prophet, gold
(222,182,96) accents, Bebas Neue (`TF_COND`) and Montserrat (`TF_SANS`). New helper drawings (mountain, sea, staff,
serpent as a simple curved shape, palace, boat) are fine; keep them simple and readable.

Review before rendering: `python3 paint_<slug>.py --probe <one time per scene>` then look at every still (Read the PNG).
Check: the light is visible, no person or face appears, text is readable and not cut off, nothing is empty or broken.
Fix and probe again. Then:
```bash
python3 paint_<slug>.py --out out/paint.mp4
ffmpeg -v error -y -i audio/narration.m4a -af loudnorm=I=-14:TP=-1.5:LRA=11 -c:a aac -b:a 192k -ar 48000 audio/voice.m4a
CAPTION_Y=0.345 python3 $T/burn_captions.py --project "$PWD" --video out/paint.mp4 --audio audio/voice.m4a --style highlighter --out out/cap.mp4 --workers 2 --crf 18
python3 $T/brand_logo.py out/cap.mp4 ../../videos/<slug>.mp4
```
`brand_logo.py` stamps the Sirah Shorts logo (`engine/core/brand/logo-transparent.png`, Rony's official logo since
19 Nov 2026) above the end card for the last 2.2 seconds and does the final compression. Never draw the logo yourself
or change it; always use that file. Check the last-second still: the logo must not cover the "PART <N+1>" text.
Check the final file with ffprobe: has video and audio, 30 to 75 seconds, under 95 MB. Grab 4 stills from it and look.

## Step 8. Publish the files

Commit `videos/<slug>.mp4` and `episodes/<slug>/` (script.json, paint file, vo.mp3; not out/ or audio/) and push to main.
Confirm `curl -sI <raw_base>videos/<slug>.mp4` returns 200.

## Step 9. Schedule the posts

Captions follow the pattern of the existing episodes:
```
<hook sentence> <one emoji>

Prophet <Name> (AS), Part <N>: <Title>
<one sentence summary>
📖 Surah <Name> <refs>

New here? Start with Part 1, pinned on our profile.
Follow @sirahshorts for Part <N+1> <emoji>

#Prophet<Name> #StoriesOfTheProphets #IslamicHistory #QuranStories #Islam
```
For Facebook replace "@sirahshorts" with "Sirah Shorts" and "pinned on our profile" with "on our Page".

- Facebook: FACEBOOK_PUBLISH_PAGE_REEL with page_id, file_url = raw URL, video_state "SCHEDULED",
  scheduled_publish_time = Unix time of the target date and time (IST is UTC+5:30), is_ai_generated false.
- Instagram, Story, YouTube, Pinterest and the Telegram LIVE message: do NOT create a scheduled task (unattended runs
  are not allowed to, since 22 Nov 2026). A separate recurring task, "Sirah Shorts 8 PM poster", runs every day at
  the posting time and publishes every episode in state.json whose `date` is today and `status` is "scheduled".
  So this run only has to save, in the episode entry: `ig_caption` (exact), `hook` (the caption's first line),
  `yt_title`, `yt_tags` (8 to 10), `pin_description`, `wa_text` (the WhatsApp post without the URL), and `video`.
  The poster follows the procedure below ("## 8 PM poster").

## 8 PM poster (run by the "Sirah Shorts 8 PM poster" task, not by the daily run)

For each episode with `date` == today (IST) and `status` "scheduled", publish the Reel: Composio
  INSTAGRAM_POST_IG_USER_MEDIA (ig_user_id "me", media_type REELS, share_to_feed true, thumb_offset 2500, video_url,
  exact caption), then INSTAGRAM_POST_IG_USER_MEDIA_PUBLISH (max_wait_seconds 240), verify with INSTAGRAM_GET_IG_MEDIA,
  skip if a Reel with the same caption opening already exists, then send a Telegram message to chat 8722468322
  (parse_mode "HTML", the house format): bold "✅ <title> LIVE", divider, IG and YT links in <code>, divider; or a 🚨
  alert in the same format on failure.
  Right after the Reel is live, the task also shares it to the Instagram Story: INSTAGRAM_POST_IG_USER_MEDIA with
  media_type "STORIES" and the same video_url (no caption), then INSTAGRAM_POST_IG_USER_MEDIA_PUBLISH. A failed Story
  is not an alert, just note it in the Telegram line.
  The same task also uploads to YouTube (account youtube_clam-adrip): in COMPOSIO_REMOTE_WORKBENCH skip if a video
  with the same title opening exists (YOUTUBE_LIST_CHANNEL_VIDEOS mine true), else download the raw video URL,
  upload_local_file() to get an s3key, YOUTUBE_MULTIPART_UPLOAD_VIDEO with title
  "Prophet <Name> (AS) Part <N>: <Title> <emoji> #Shorts" (max 100 chars), categoryId "27", privacyStatus "public",
  8 to 10 search tags, and the caption as description with "#Shorts" first among the hashtags, a line "Out of respect,
  no Prophet or person is shown; Prophet <Name> (AS) appears as a glowing light." and "Watch from Part 1 in the
  Prophet <Name> playlist." Then YOUTUBE_ADD_VIDEO_TO_PLAYLIST with the prophet's playlist from
  state.youtube.playlists; when a new prophet starts, create the playlist first (YOUTUBE_CREATE_PLAYLIST, public,
  title "Prophet <Name> (AS) | Full Story in Parts") and save its id in state.json.
  After YouTube, the same task pins the video on Pinterest (account pinterest_rasher-jato, board id in state.pinterest):
  in COMPOSIO_REMOTE_WORKBENCH call PINTEREST_REGISTER_MEDIA (media_type video), POST the video bytes to the returned
  upload_url as multipart/form-data with all upload_parameters as form fields plus the file, wait about 60 seconds, then
  PINTEREST_CREATE_PIN with board_id, title "Prophet <Name> (AS) Part <N>: <Title>", a plain description (hook, summary,
  refs, 4 hashtags), link = the YouTube Short URL, media_source {source_type "video_id", media_id,
  cover_image_url "https://i.ytimg.com/vi/<youtube id>/hqdefault.jpg"}. If it fails with a 500, wait 60 seconds and try
  once more. A failed Pin is not an alert, just note it in the Telegram line.
  Finally the task sends a second Telegram message, the copy-ready WhatsApp Channel post, plain text only (no parse_mode):
  "<hook sentence> <emoji>\n\nProphet <Name> (AS), Part <N>: <Title>\n📖 Surah <refs>\n\n▶️ Watch: <YouTube Short URL>"
  When an older episode does not have `yt_title`, `yt_tags`, `pin_description` or `wa_text`, build them from its
  title, refs and `ig_caption` in the formats above.
  Finally set the episode's `status` to "posted" and save `ig_media_id`, `ig_permalink`, `yt_video_id`, `pin_id`;
  commit and push state.json ("State: <slug> posted"). Every platform step skips itself if that post already exists,
  so running twice never double-posts. If nothing is due today, do nothing and send nothing.

## Step 9b. Weekly collab outreach (Mondays only)

Only when today is Monday (IST). Rules: propose an Instagram Collab post only (we post one of our episodes and invite
them as collaborator; they just tap Accept, nothing else is asked of them). Never ask them to record a voice or make
anything. At most `state.outreach.weekly_max` (5) new creators per week, never anyone already in
`state.outreach.contacted`.
1. Find candidates: vidiq_instagram_account_discovery with niche "Islamic reminders, Quran and prophet stories, Islamic
   history" and an audience line for English-speaking Muslims (Global: true), followers 5,000 to 150,000. Skip accounts
   that are not clearly respectful Islamic content, that post music, or that look like large media companies.
2. For each, read the public profile with SCRAPECREATORS_GET_INSTAGRAM_PROFILE through Composio (cheap; save vidIQ credits).
   If it fails with 402 (Composio wallet empty), use mcp vidiq_ig_profile instead (5 credits each, at most 3 profiles a
   week, only for the best candidates) and use only a business
   email the creator shows publicly in their bio or contact button. No email shown: skip them. Never guess emails.
3. Send from sirahshorts@gmail.com with GMAIL_SEND_EMAIL (account gmail_melas-mong), plain text, short and personal:
   subject "Collab idea: Stories of the Prophets x @<handle>"; mention one specific thing about their content; one line
   on Sirah Shorts (illustrated stories of the prophets from the Qur'an, no prophet or person ever depicted); the offer:
   "we'd post our next episode as an Instagram Collab with you, you would only need to tap Accept, and it shows on both
   profiles"; link to one of our Reels; sign "Rony, Sirah Shorts". No attachments, no pressure, no follow-up promises.
4. Add each to `state.outreach.contacted` with handle, email, date, status "sent".
5. Every run (any weekday): search Gmail (GMAIL_FETCH_EMAILS, query "to:sirahshorts@gmail.com newer_than:2d") for
   replies from contacted creators; mark them "replied" and tell Rony in the report: "📩 @handle replied about a collab".
   Send one polite follow-up 7 days after "sent" if there is no reply, then mark "closed". When a creator agrees, add
   their handle to the next episode's Instagram post as a collaborator if the Composio tool supports it, otherwise tell
   Rony to add them in the app.

## Step 9c. Weekly long video for YouTube (Sundays only)

Only when today is Sunday (IST). Long videos pay about 10 times more per view than Shorts and their watch hours count
toward YouTube monetization, so every Sunday we join finished Shorts into one 16:9 film. Make at most one per Sunday.
1. Pick what to join, in this order:
   a. Full story: a prophet whose parts are all posted (nothing left for them in `plan`) and who has no entry with
      `"kind": "full"` in `state.long_videos`. Use every part. Title "The Full Story".
   b. Chapter: otherwise, the current prophet's posted parts that are not yet in any `state.long_videos` entry of kind
      "chapter". Need at least 3 such parts. Title: a short name for that stretch of the story (e.g. "The Early Life",
      "Musa and Pharaoh").
   Only use episodes whose status is "posted". If nothing qualifies, skip this step silently.
2. Build: `python3 engine/tools/compile_long.py --prophet <Name> --title "<Title>" --parts "N:<Part title>:videos/<slug>.mp4" ...
   --next "Next: Part <N+1>, <Title>" --out long/<prophet>-<first>-<last>.mp4` (for a full story, --next names the next
   prophet in the plan). It adds a title card, side panels with the part names, and an end card, keeps the narration,
   adds no music, and writes `<out>.chapters.txt` and `<out>.thumb.jpg`. If the file is over 90 MB, rebuild with
   `--crf 27`. Check stills from the title card, two parts and the end card before going on.
3. Commit `long/` and push; confirm the raw URL returns 200.
4. YouTube (account youtube_clam-adrip), in COMPOSIO_REMOTE_WORKBENCH: skip if a video with the same title exists,
   else upload_local_file() then YOUTUBE_MULTIPART_UPLOAD_VIDEO with title
   "Prophet <Name> (AS) | <Title> (Parts <a> to <b>) | Stories of the Prophets" (max 100 chars, no #Shorts),
   categoryId "27", privacyStatus "public", 10 to 15 tags, and this description:
   one or two sentence summary; blank line; the chapters from chapters.txt (first one must be 0:00); blank line;
   "📖 Surah <refs of every part>"; "Out of respect, no Prophet or person is shown; Prophet <Name> (AS) appears as a
   glowing light."; "Watch the parts as Shorts in the Prophet <Name> playlist."; 3 hashtags.
   Then YOUTUBE_ADD_VIDEO_TO_PLAYLIST with the prophet's playlist, then YOUTUBE_UPDATE_THUMBNAIL with videoId and
   thumbnailUrl = the raw GitHub URL of `long/<name>.mp4.thumb.jpg` (the channel is phone-verified since 18 Nov 2026).
   If the thumbnail fails, note it in the report, not an alert.
5. Facebook: if the film is 3 minutes or longer, also post it on the Page as a normal video (not a Reel) with the
   same title and description, published now. A failure here is one line in the report, not an alert.
6. Add to `state.long_videos`: {kind, prophet, parts [n...], title, file, duration, yt_video_id, fb_video_id, date}.
   Report line: "🎬 Long video live: <Title> https://youtu.be/<id>".

## Step 10. Save state and report

Move the plan item into `episodes` with date, time, status "scheduled", fb_video_id, refs, video path, and the posting
fields from Step 9 (ig_caption, hook, yt_title, yt_tags, pin_description, wa_text). The 8 PM poster posts it.
When the plan has 5 or fewer items left, append the next parts for the next prophet in the same style (Ibrahim, Yunus,
Sulaiman, Isa, then Muhammad ﷺ, whose Sirah gives the account its name) and say so in the report.
Commit and push state.json.

Send one Telegram message (TELEGRAM_SEND_MESSAGE, chat_id 8722468322, parse_mode "HTML", in the format from
"Telegram message format" above).
Rony wants it short: 2 to 4 content lines, no explanations (see the example in "Telegram message format").
Leave out any line that has nothing to say. Every failure anywhere: one line, "🚨 <what failed>. <what to do>", then
stop. Never post anything you have not checked frame by frame.

## Step 11. Office page (PAUSED)

Paused by Rony on 2026-11-19: do not update the Sirah Shorts HQ artifact. Skip this step entirely until he
asks to turn it back on. Keep `state.office` as it is.
