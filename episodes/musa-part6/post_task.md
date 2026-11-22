# One-time post task for Musa Part 6

Create a one-time scheduled task: name "Sirah Shorts: post Musa Part 6 (IG, YT, Pinterest)",
run_once_at 2026-11-23T20:00:00[Asia/Calcutta], initiation human_schedule, notifications push,
with the prompt below (same structure as the Part 5 task trig_019cM3cezQhW9YKrF5AS1FFP).

---

Publish Sirah Shorts episode "Musa Part 6: The Magicians" now. Facebook is already scheduled natively (video 1483241680331602); do NOT post to Facebook.

Rules: use Composio tools only, and pass the account explicitly on EVERY call: instagram_lite-clam, youtube_clam-adrip, pinterest_rasher-jato, telegram_hackle-scient. Before posting to Instagram, confirm the account username is "sirahshorts" (INSTAGRAM_GET_USER_INFO or the media list); if not, post nothing and send the Telegram alert below.

Video URL: https://raw.githubusercontent.com/qixings/sirahshorts-media/main/videos/musa-part6.mp4

Instagram caption (exact):
The magicians came to beat Musa, and left as believers ✨

Prophet Musa (AS), Part 6: The Magicians
Ropes that seemed to move, a staff that swallowed them all, and a faith no threat could break.
📖 Surah Taha 20:57-73, Surah Al-A'raf 7:113-126

Send this to someone who loves these stories.
New here? Start with Part 1, pinned on our profile.
Follow @sirahshorts for Part 7 🌾

#ProphetMusa #StoriesOfTheProphets #IslamicHistory #QuranStories #Islam

1. Instagram Reel: skip if a recent Reel already starts with "The magicians came to beat Musa". Else INSTAGRAM_POST_IG_USER_MEDIA (ig_user_id "me", media_type REELS, share_to_feed true, thumb_offset 2500, video_url, caption) then INSTAGRAM_POST_IG_USER_MEDIA_PUBLISH (max_wait_seconds 240). Verify with INSTAGRAM_GET_IG_MEDIA and get the permalink.
2. Instagram Story: INSTAGRAM_POST_IG_USER_MEDIA media_type "STORIES" with the same video_url (no caption), then publish. A failed Story is not an alert, just note it.
3. YouTube, in COMPOSIO_REMOTE_WORKBENCH: skip if a video titled "Prophet Musa (AS) Part 6" exists (YOUTUBE_LIST_CHANNEL_VIDEOS mine true). Else download the video URL, upload_local_file() for an s3key, then YOUTUBE_MULTIPART_UPLOAD_VIDEO with title "Prophet Musa (AS) Part 6: The Magicians ✨ #Shorts", categoryId "27", privacyStatus "public", tags ["prophet musa","moses","pharaoh","magicians","stories of the prophets","quran stories","islamic history","surah taha","surah al araf","islam shorts"], description = the Instagram caption with "#Shorts" added first among the hashtags, plus the lines "Out of respect, no Prophet or person is shown; Prophet Musa (AS) appears as a glowing light." and "Watch from Part 1 in the Prophet Musa playlist." Then YOUTUBE_ADD_VIDEO_TO_PLAYLIST to playlist PLZ_eT7sWEYTQ.
4. Pinterest (board 228135606063555213): in COMPOSIO_REMOTE_WORKBENCH PINTEREST_REGISTER_MEDIA (media_type video), POST the video bytes to upload_url as multipart/form-data with all upload_parameters plus the file, wait about 60 seconds, then PINTEREST_CREATE_PIN with title "Prophet Musa (AS) Part 6: The Magicians", description "The magicians came to beat Musa, and left as believers. A staff that swallowed their magic and a faith no threat could break. Surah Taha 20:57-73, Surah Al-A'raf 7:113-126. #ProphetMusa #StoriesOfTheProphets #QuranStories #IslamicHistory", link = the YouTube Short URL, media_source {source_type "video_id", media_id, cover_image_url "https://i.ytimg.com/vi/<youtube id>/hqdefault.jpg"}. On a 500, wait 60 s and retry once. A failed Pin is not an alert.
5. Telegram (TELEGRAM_SEND_MESSAGE, chat_id 8722468322), first message with parse_mode "HTML":
<b>✅ MUSA PART 6 · LIVE</b>
<i>The Magicians</i>
<code>========================</code>
<b>📸 IG:</b> <code><permalink></code>
<b>▶️ YT:</b> <code>https://youtube.com/shorts/<id></code>
<b>Story:</b> <i>✅ or failed</i> · <b>Pin:</b> <i>✅ or failed</i>
<code>========================</code>
Then a second message, the WhatsApp Channel post, plain text with NO parse_mode: "The magicians came to beat Musa, and left as believers ✨\n\nProphet Musa (AS), Part 6: The Magicians\n📖 Surah Taha 20:57-73, Surah Al-A'raf 7:113-126\n\n▶️ Watch: <YouTube Short URL>".
On any Instagram or YouTube failure send instead (parse_mode "HTML"):
<b>🚨 MUSA PART 6 FAILED</b>
<code>========================</code>
<b>Platform:</b> <i><platform></i>
<b>Error:</b> <i><short reason, with &, < and > escaped></i>
<b>Do:</b> <i>Check the account, or ask Claude to repost it.</i>
<code>========================</code>
6. Finally update state.json in the GitHub repo qixings/sirahshorts-media (clone it, edit, commit, push): in the episodes entry with part 6 set status "posted" and add ig_media_id, ig_permalink, yt_video_id, pin_id.
