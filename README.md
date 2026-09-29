# 🌿 Niroza Ayurvedic – Instagram Auto Post

Ye system roz **3 product** apne aap aapke Instagram (@niroza_ayurvedic) par post karta hai —
har product ki **1 photo + description**, alag-alag time par:

| Post | Time (India) |
|---|---|
| Product 1 | ~10:10 AM |
| Product 2 | ~2:10 PM |
| Product 3 | ~7:10 PM |

Products list mein se ek-ek karke aage badhte hain. List khatam hone par phir se shuru se.
Ye **GitHub** par free chalta hai — aapka computer ya phone on rehne ki zaroorat nahi.

> GitHub ka time kabhi-kabhi 5–30 minute late ho sakta hai, ye normal hai.

---

## ✅ Ek baar ka setup (lagbhag 30 minute)

### Step 1 — Instagram ko Professional account banao
Instagram app → **Settings → Account type and tools → Switch to professional account** → *Business* chuniye.
(Agar pehle se Business/Creator hai to ye step skip karein.)

### Step 2 — Instagram Access Token banao (Meta Developer)
1. **https://developers.facebook.com** kholiye → Facebook ID se login → *Get Started* se developer account banaiye.
2. **My Apps → Create App**.
3. Use case mein **"Manage messaging & content on Instagram"** chuniye → App type **Business** → naam jaise `Niroza AutoPost` → Create.
4. Left menu → **Instagram → API setup with Instagram login**.
5. **"Generate access tokens"** section mein **Add account** → @niroza_ayurvedic se login karke **Allow** dabaiye
   (permission list mein *content publish* zaroor allow ho).
   - Agar tester invite maange: Instagram app → Settings → **Website permissions → Apps and websites → Tester invites** → Accept.
6. Account ke saamne **Generate token** → jo lamba token dikhe use **copy** karke kahin safe rakh lijiye.
   ⚠️ Ye token kisi ko mat bhejiye — ye aapke Instagram ki chaabi hai.

### Step 3 — GitHub repo banao aur files daalo
1. **https://github.com** par free account banaiye.
2. Upar **+ → New repository** → naam `niroza-insta-autopost` → **Public** chuniye → Create.
   (Public zaroori hai taaki Instagram photo le sake. Aapka token *Secrets* mein rehta hai, woh kisi ko nahi dikhta.)
3. Repo page par **"uploading an existing file"** link → is ZIP ko unzip karke **saari files aur folders** (`.github` folder bhi) drag-drop karein → **Commit changes**.
   - Agar `.github` folder upload na ho: **Add file → Create new file** → naam mein `.github/workflows/autopost.yml` likhiye → us file ka content paste karke Commit.

### Step 4 — Token ko Secret mein daalo
Repo → **Settings → Secrets and variables → Actions → New repository secret**
- Name: `IG_ACCESS_TOKEN`
- Secret: Step 2 wala token paste → **Add secret**

### Step 5 — Products daalo
**Tarika A — Instagram se apne aap (aasaan):**
Repo → **Actions** tab → (pehli baar "I understand… enable" dabaana pad sakta hai) → **Insta Auto Post** → **Run workflow** → action: **import** → Run.
Ye aapke purane photo posts ki photo aur caption `products.csv` mein daal dega.

**Tarika B — khud photo upload:**
`images` folder kholiye → **Add file → Upload files** → product photos daaliye (jaise `ashwagandha.jpg`).

Phir `products.csv` kholiye → ✏️ (pencil) se edit karein. Har line = 1 product:

| column | kya likhein |
|---|---|
| `active` | `yes` = post karo, `no` = mat karo |
| `name` | Product ka naam |
| `description` | Details / fayde. Nayi line ke liye `\n` likhein |
| `price` | Sirf number, jaise `349` (khali chhod sakte hain) |
| `image` | `images` folder mein photo ka naam, jaise `ashwagandha.jpg` |
| `hashtags` | Is product ke hashtags (khali = config.json wale default) |
| `caption` | Agar poora caption khud likhna hai to yahan; warna khali chhodiye |

Teen `Example Product` wali lines hata dijiye. Kisi text mein comma (`,`) ho to us poore text ko `"double quotes"` mein rakhiye.

### Step 6 — Test karo
Actions → Insta Auto Post → Run workflow:
1. **check** → token aur photos sahi hain ya nahi
2. **dry-run** → caption kaisa dikhega (post nahi hoga)
3. **post** → abhi 1 real post. Instagram par check kariye 🎉

Bas! Ab roz 3 post apne aap honge.

---

## ⚙️ Badlav kaise karein
- **Neeche wala text / default hashtags:** `config.json` mein `footer` aur `default_hashtags` badliye (WhatsApp number, website wagairah yahan daal sakte hain).
- **Post ka time:** `.github/workflows/autopost.yml` mein `cron` lines. Time UTC mein hai — IST se **5 ghante 30 minute ghata** kar likhiye.
  Example: 9:00 AM IST = `30 3 * * *`
- **Kaunsa product agla hai:** `state.json` mein `next_index` (0 = pehla product).
- **Kya-kya post hua:** `state.json` mein `history`.
- Photo ka size/shape apne aap Instagram ke hisaab se ho jaata hai (lambi photo ke side mein safed patti lag jaati hai).

## 🔑 Token 60 din wala niyam
Instagram token 60 din mein expire hota hai. Ye system **har Monday** token ko apne aap refresh karta hai.
Poori safety ke liye (optional, recommended): GitHub → profile photo → **Settings → Developer settings → Personal access tokens → Fine-grained → Generate** →
sirf is repo ko chuniye → Permissions: **Secrets: Read and write** → token copy karke repo mein secret `GH_PAT` naam se daal dijiye.
Tab refresh hua token bhi apne aap save ho jayega.

## ❗ Kuch galat ho to
Koi post fail hone par GitHub aapko **email** karta hai. Actions tab mein laal ❌ wale run par click karke message padhiye — error Hindi/Hinglish mein samjhaaya gaya hai.
- *Token expire / code 190* → Step 2 se naya token banakar Step 4 mein secret update karein.
- *Photo nahi mili* → `products.csv` ka `image` naam aur `images` folder ki photo ka naam same karein.
- *Public link nahi khul raha* → repo **Public** hona chahiye.
- 60 din tak repo mein koi activity na ho to GitHub schedule band kar deta hai — lekin ye system roz khud commit karta hai, isliye aisa nahi hoga.
